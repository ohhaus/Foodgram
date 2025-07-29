from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe


class ShowRecipeAddedSerializer(serializers.ModelSerializer):
    """Сериализатор для минимизированного вывода рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShortLinkSerialzier(serializers.ModelSerializer):
    """Сериализатор для получения короткой ссылки."""

    short_link = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'short_link')

    def get_short_link(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        base_url = request.build_absolute_uri('/')[:-1]
        return f'{base_url}/api/recipes/{obj.id}/'
