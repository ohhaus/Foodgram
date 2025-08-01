from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    """Встроенный класс для ингредиентов рецепта."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Конфигурация админ-панели для модели Tag."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Конфигурация админ-панели для модели Ingredient."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Конфигурация админ-панели для модели Recipe."""

    list_display = (
        'name',
        'author',
        'cooking_time',
        'pub_date',
        'favorites_count',
    )
    list_filter = ('author', 'tags', 'pub_date')
    search_fields = ('name', 'author__username')
    readonly_fields = ('pub_date', 'short_link', 'favorites_count')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = 'В избранном'

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('author')
            .prefetch_related('tags', 'favorites')
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Конфигурация админ-панели для модели Favorite."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe__author')
    search_fields = ('user__username', 'recipe__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Конфигурация админ-панели для модели ShoppingCart."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe__author')
    search_fields = ('user__username', 'recipe__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recipe')
