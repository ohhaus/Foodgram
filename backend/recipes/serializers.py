from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        # Должен быть поиск по имени


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(read_only=True, source="ingredient")
    name = serializers.SlugRelatedField(
        read_only=True, source="ingredient", slug_field="name"
    )
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        source="ingredient",
        slug_field="measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipeingredient_set",
        read_only=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and request.user.shopping_list.filter(recipe=obj).exists()
        )
