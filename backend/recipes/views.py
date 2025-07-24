from django.shortcuts import render
from rest_framework import viewsets, permissions


from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient
from recipes.serializers import TagSerialzier, IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialzier
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
