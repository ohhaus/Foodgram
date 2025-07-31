"""
Views for recipes app.
"""

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsAuthorOrReadOnly

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    RecipeMinifiedSerializer,
    RecipeShortLinkSerializer,
    TagSerializer,
)
from .utils import generate_shopping_cart_pdf


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Tag model (read-only)."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Ingredient model (read-only)."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for Recipe model."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeListSerializer

    def create(self, request, *args, **kwargs):
        """Create recipe with authentication check."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update recipe with validation."""
        partial = kwargs.pop('partial', False)

        if not partial:
            required_fields = [
                'ingredients',
                'tags',
                'name',
                'text',
                'cooking_time',
                'image',
            ]
            missing_fields = []
            for field in required_fields:
                if field not in request.data:
                    missing_fields.append(field)

            if missing_fields:
                error_dict = {}
                for field in missing_fields:
                    if field == 'ingredients' or field == 'tags':
                        error_dict[field] = ['Это поле обязательно.']
                    else:
                        error_dict[field] = ['Это поле обязательно.']
                return Response(error_dict, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set author to current user when creating recipe."""
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """Return optimized queryset."""
        return Recipe.objects.select_related('author').prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
            'favorites',
            'shopping_cart',
        )

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Get short link for recipe."""
        recipe = self.get_object()
        serializer = RecipeShortLinkSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Add or remove recipe from favorites."""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=user, recipe=recipe
            ).first()
            if not favorite:
                return Response(
                    {'errors': 'Рецепт не найден в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Add or remove recipe from shopping cart."""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            cart_item, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_item = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).first()
            if not cart_item:
                return Response(
                    {'errors': 'Рецепт не найден в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Download shopping cart as PDF."""
        user = request.user
        shopping_cart_recipes = Recipe.objects.filter(shopping_cart__user=user)

        if not shopping_cart_recipes.exists():
            return Response(
                {'errors': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pdf_content = generate_shopping_cart_pdf(shopping_cart_recipes)

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        return response
