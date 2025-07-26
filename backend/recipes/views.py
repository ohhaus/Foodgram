from urllib.parse import unquote

from django.db.models import Sum
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action

from core.filters import RecipeFilter
from core.pagination import LimitPageNumberPagination
from core.permissions import AuthorOrReadOnly
from core.utils import handle_add_or_remove_recipe, delete_recipe_image, generate_shopping_list_file
from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart, RecipeIngredient
from recipes.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    AddFavoriteRecipeSerializer,
    AddShopingListRecipeSerializer,
    RecipeIngredientSerializer
)


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
            name = unquote(name) if name[0] == '%' else name.translate('')
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
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipeWriteSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Добавляем/удаляем рецепты из избранного."""
        return handle_add_or_remove_recipe(
            AddFavoriteRecipeSerializer, Favorite, request, pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated)
    )
    def shopping_cart(self, request, pk):
        """Добавляем/удаляем рецепты из списка покупок."""
        return handle_add_or_remove_recipe(
            AddShopingListRecipeSerializer, ShoppingCart, request, pk
        )

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')

        return generate_shopping_list_file(request.user, ingredients)
