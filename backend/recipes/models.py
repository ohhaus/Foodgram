from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core import validators

from users.models import User
from core.models import NameModel


class Ingredient(NameModel):
    """Модель ингредиента."""

    class MeasurementUnit(models.TextChoices):
        GRAM = 'г', 'Грамм'
        KILOGRAM = 'кг', 'Килограмм'
        MILLILITER = 'мл', 'Миллилитр'
        LITER = 'л', 'Литр'
        PIECE = 'шт', 'Штука'
        TEASPOON = 'ч. л', 'Чайная ложка'
        TABLESPOON = 'ст. л', 'Столовая ложка'

    measurement_unit = models.CharField(
        _('Единица измерения'),
        choices=MeasurementUnit.choices,
        max_length=15,
        blank=False,
        null=False,
    )

    class Meta(NameModel.Meta):
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'mesurement_unit'], name='unique_ingredient')
        )


class Tag(NameModel):
    """Модель тега."""

    name = models.CharField(
        _('Название'),
        unique=True,
        max_length=150,
    )
    slug = models.SlugField(
        _('Уникальный слаг'),
        max_length=150,
        unique=True,
        validators=(validators.validate_slug,)
    )

    class Meta(NameModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        defaul_related_name = 'tags'
        ordering = ('name',)


class Recipe(NameModel):
    author = models.ForeignKey(
        User,
        verbose_name=_('Автор рецепта'),
        on_delete=models.SET_NULL,
        null=True,
    )
    text = models.TextField(
        _('Описание рецепта'),
    )
    image = models.ImageField(
        _('Изображние рецепта'),
        upload_to='recipes/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        _('Время приготовления в минутах'),
        default=1,
        validators=(validators.MinValueValidator(1),)
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name=_('Ингредиенты')
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Теги'),
    )
    pub_date = models.DateTimeField(
        _('Дата публикации'),
        auto_now_add=True,
        editable=False,
    )

    class Meta(NameModel.Meta):
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        default_related_name = 'recipes'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_name_author',
            ),
        )


class RecipeIngredient(models.Model):
    """Модель ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингредиент'),
    )
    amount = models.PositiveSmallIntegerField(
        _('Количество'),
        default=1,
        validators=(validators.MinValueValidator(1),)
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = _('Количество ингредиентов')
        verbose_name_plural = _('Количество ингредиентов')
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} - '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class FavoriteShoppingCart(models.Model):
    """Асбстрактная модель добавляющая пользователя и рецепт"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(FavoriteShoppingCart):
    """Модель списка покупок."""

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Списки покупок')
        default_related_name = 'shopping_list'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe',
            )
        )


class Favorite(FavoriteShoppingCart):
    """Модель избранного."""

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = _('Избранный рецепт')
        verbose_name_plural = _('Избранные рецепты')
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            )
        )
