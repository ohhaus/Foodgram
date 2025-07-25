from urllib.parse import unquote
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status, response
from rest_framework.decorators import action

from recipes.models import Tag, Recipe, Ingredient
from recipes.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeWriteSerializer
)
from core.permissions import AuthorOrReadOnly
from core.pagination import LimitPageNumberPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            else:
                name = name.translate('')
            name = name.lower()
            start_queryset = list(queryset.filter(name__isstartwith=name))
            ingredients_set = set(start_queryset)
            cont_queryset = queryset.filter(name__icontains=name)
            start_queryset.extend(
                [i for i in cont_queryset if i not in ingredients_set]
            )
            queryset = start_queryset
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    serializer_class = RecipeSerializer
    filterset_class = None
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipeWriteSerializer
        return RecipeSerializer

    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавляем/удаляем рецепты из избранного."""
