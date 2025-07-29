from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)


class RecipeByUserFilter(SimpleListFilter):
    title = 'Автор рецепта'
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        authors = model_admin.model.objects.values_list(
            'author__id', 'author__username'
        ).distinct()
        return list(authors)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(author_id=self.value())
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'cooking_time', 'display_image')
    list_filter = ('tags', RecipeByUserFilter, 'cooking_time')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = [
        RecipeIngredientInline
    ]  # Убраны FavoriteInline и ShoppingCartInline
    empty_value_display = '-пусто-'

    def display_image(self, obj):
        try:
            if obj.image and obj.image.url:
                return format_html(
                    '<img src="{}" width="50" height="50" />', obj.image.url
                )
        except ValueError:
            pass
        return '-нет изображения-'

    display_image.short_description = 'Изображение'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe__name', 'ingredient__name')
    search_fields = ('recipe__name', 'ingredient__name')
    empty_value_display = '-пусто-'
