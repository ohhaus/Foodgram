from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constants import (
    COOKING_TIME_MAX_VALUE,
    COOKING_TIME_MIN_VALUE,
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    RECIPE_INGREDIENT_AMOUNT_MAX_VALUE,
    RECIPE_INGREDIENT_AMOUNT_MIN_VALUE,
    RECIPE_NAME_MAX_LENGTH,
    RECIPE_TEXT_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)
from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название',
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement_unit',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_NAME_MAX_LENGTH,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Описание',
        max_length=RECIPE_TEXT_MAX_LENGTH,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(COOKING_TIME_MIN_VALUE),
            MaxValueValidator(COOKING_TIME_MAX_VALUE),
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class ShortLink(models.Model):
    """Модель короткой ссылки."""

    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='short_link',
        verbose_name='Рецепт',
    )
    short_code = models.CharField(
        'Короткий код',
        max_length=10,
        unique=True,
        db_index=True,
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return f'Короткая ссылка для {self.recipe.name}: {self.short_code}'

    @property
    def full_url(self):
        return f'/s/{self.short_code}'


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиента с количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(RECIPE_INGREDIENT_AMOUNT_MIN_VALUE),
            MaxValueValidator(RECIPE_INGREDIENT_AMOUNT_MAX_VALUE),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}'


class Favorite(models.Model):
    """Модель избранного рецепта."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.name}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart_recipe',
            )
        ]

    def __str__(self):
        return (
            f'{self.user.username} добавил в список покупок {self.recipe.name}'
        )
