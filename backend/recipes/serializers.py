from django.conf import settings
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core.serializers import ShowRecipeAddedSerializer
from core.validators import (
    validate_cooking_time,
    validate_ingredients,
    validate_tags,
)
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
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)
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
            ingredient = ingredient_data.pop('id')
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount'],
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.recipeingredient_set.all().delete()
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('id')
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data['amount'],
            )
        return super().update(instance, validated_data)

    def validate_cooking_time(self, data):
        return validate_cooking_time(self.initial_data.get('cooking_time'))

    def validate_ingredients(self, data):
        return validate_ingredients(self.initial_data.get('ingredients'))

    def validate_tags(self, data):
        return validate_tags(data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class AddFavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецептов в избранное."""

    class Meta:
        model = Favorite
        fields = ('recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message=settings.FAVORITE_ALREADY_EXISTS_ERROR,
            )
        ]

    def validate(self, data):
        """Проверка существования рецепта и авторизации."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(settings.AUTHORIZATION_REQUIRED)
        recipe = data.get('recipe')
        if not Recipe.objects.filter(id=recipe.id).exists():
            raise serializers.ValidationError(settings.RECIPE_NOT_FOUND)
        return data

    def save(self, **kwargs):
        """Сохранение с текущим пользователем."""
        kwargs['user'] = self.context['request'].user
        return super().save(**kwargs)

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShowRecipeAddedSerializer(
            instance.recipe, context={'request': request}
        )


class AddShoppingListRecipeSerializer(AddFavoriteRecipeSerializer):
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
