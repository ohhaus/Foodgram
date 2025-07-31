import django_filters

from .models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Filter for Recipe model."""

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        """Filter recipes by favorite status."""
        if not self.request.user.is_authenticated:
            return queryset
        if value in ['1', 'true', 'True']:
            return queryset.filter(favorites__user=self.request.user)
        elif value in ['0', 'false', 'False']:
            return queryset.exclude(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Filter recipes by shopping cart status."""
        if not self.request.user.is_authenticated:
            return queryset
        if value in ['1', 'true', 'True']:
            return queryset.filter(shopping_cart__user=self.request.user)
        elif value in ['0', 'false', 'False']:
            return queryset.exclude(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Filter for Ingredient model."""

    name = django_filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ['name']

    def filter_name(self, queryset, name, value):
        """Filter ingredients by name (case-insensitive, starts with)."""
        if value:
            return queryset.filter(name__istartswith=value)
        return queryset
