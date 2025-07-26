from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe


class ShowRecipeAddedSerializer(serializers.ModelSerializer):
    """Сериализатор для минимизированного вывода рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
