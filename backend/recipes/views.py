from django.shortcuts import render
from rest_framework import viewsets, permissions, filters


from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient
from recipes.serializers import TagSerialzier, IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialzier
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
