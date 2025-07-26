from django.db import models, transaction
from django.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.serializers import UserSerializer


class ShowRecipeAddedSerializer(serializers.ModelSerializer):
    """Сериализатор для минимизированного вывода рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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

    # FIXME: Настроить корректно валидацию данных
    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                _('Время готовки должно быть больше 0!')
            )
        return value

    # FIXME: Настроить корректно валидацию данных
    def validate_ingredients(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                _('Должен быть хотя бы один ингредиент!')
            )
        return value

    # FIXME: Настроить корректно валидацию данных
    def validate_tags(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError('Должен быть хотя бы один тег!')
        return value


class AddFavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецептов в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное!',
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
                message='Товар уже в корзине!',
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShowRecipeAddedSerializer(
            instance.recipe, context={'request': request}
        )
