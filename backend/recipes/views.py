from urllib.parse import unquote

from django.db.models import Sum
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from core.filters import RecipeFilter
from core.pagination import LimitPageNumberPagination
from core.permissions import AuthorOrReadOnly
from core.serializers import ShortLinkSerialzier
from core.utils import (
    generate_shopping_list_file,
    handle_add_or_remove_recipe,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.serializers import (
    AddFavoriteRecipeSerializer,
    AddShoppingListRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'
    ordering = ('name',)
    ordering_fields = ('name', 'id')
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        response = super().list(request, **args, **kwargs)
        return Response(response.data['results'])


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    ordering_fields = ('name',)
    filterset_fields = ('name',)
    search_fields = ('^name',)

    def list(self, request, *args, **kwargs):
        response = super().list(request, **args, **kwargs)
        return Response(response.data['results'])


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
        permission_classes=(permissions.IsAuthenticated),
    )
    def shopping_cart(self, request, pk):
        """Добавляем/удаляем рецепты из списка покупок."""
        return handle_add_or_remove_recipe(
            AddShoppingListRecipeSerializer, ShoppingCart, request, pk
        )

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_list__user=request.user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        return generate_shopping_list_file(request.user, ingredients)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_link(self, request, pk):
        recipe = self.get_object()
        serializer = ShortLinkSerialzier(recipe, context={'request': request})
        return Response(serializer.data)
