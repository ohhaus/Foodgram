from django.conf import settings
from django.db import models, transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueTogetherValidator

from core.serializers import ShowRecipeAddedSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='ingredient'
    )
    name = serializers.SlugRelatedField(
        read_only=True, source='ingredient', slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        source='ingredient',
        slug_field='measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов (только чтение)."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set',
        read_only=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=models.F('recipes__ingredient_list'),
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.shopping_list.filter(recipe=obj).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания обновления рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.set(tags)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=instance, **ingredient_data)
        return super().update(instance, validated_data)

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(settings.COOKING_TIME_MIN_ERROR)
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if len(ingredients) <= 0:
            raise exceptions.ValidationError(
                {'ingredients': settings.INGREDIENT_AMOUNT_MIN_ERROR}
            )
        ingredients_list = []
        for item in ingredients:
            if item['id'] in ingredients_list:
                raise exceptions.ValidationError(
                    {'ingredients': settings.DUPLICATE_INGREDIENTS_ERROR}
                )
            ingredients_list.append(item['id'])
            if int(item['amount']) <= 0:
                raise exceptions.ValidationError(
                    {'amount': settings.INGREDIENT_AMOUNT_MIN_ERROR}
                )
        return data

    def validate_tags(self, data):
        tags = data
        if not tags:
            raise exceptions.ValidationError(
                {'tags': settings.TAGS_REQUIRED_ERROR}
            )
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise exceptions.ValidationError(
                    {'tags': settings.DUPLICATE_TAGS_ERROR}
                )
            tags_list.append(tag)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class AddFavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецептов в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message=settings.FAVORITE_ALREADY_EXISTS_ERROR,
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShowRecipeAddedSerializer(
            instance.recipe, context={'request': request}
        )


class AddShopingListRecipeSerializer(AddFavoriteRecipeSerializer):
    """Сериализатор добавления рецептов в список покупок."""

    class Meta(AddFavoriteRecipeSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message=settings.SHOPPING_CART_ALREADY_EXISTS_ERROR,
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShowRecipeAddedSerializer(
            instance.recipe, context={'request': request}
        )
