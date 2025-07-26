from django.conf import settings
from django.core import validators
from django.db import models

from core.models import FavoriteShoppingCart, NameModel
from users.models import User


class Ingredient(NameModel):
    """Модель ингредиента."""

    name = models.CharField(
        settings.INGREDIENT_NAME_VERBOSE_NAME,
        unique=True,
        max_length=settings.INGREDIENT_NAME_LENGTH,
    )

    class MeasurementUnit(models.TextChoices):
        GRAM = settings.MEASUREMENT_UNITS[0]
        KILOGRAM = settings.MEASUREMENT_UNITS[1]
        MILLILITER = settings.MEASUREMENT_UNITS[2]
        LITER = settings.MEASUREMENT_UNITS[3]
        PIECE = settings.MEASUREMENT_UNITS[4]
        TEASPOON = settings.MEASUREMENT_UNITS[5]
        TABLESPOON = settings.MEASUREMENT_UNITS[6]

    measurement_unit = models.CharField(
        settings.INGREDIENT_MEASUREMENT_UNIT_VERBOSE_NAME,
        choices=MeasurementUnit.choices,
        max_length=settings.MEASUREMENT_UNIT_LENGTH,
        blank=False,
        null=False,
    )

    class Meta(NameModel.Meta):
        verbose_name = settings.INGREDIENT_MODEL_VERBOSE_NAME
        verbose_name_plural = settings.INGREDIENT_MODEL_VERBOSE_NAME_PLURAL
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]


class Tag(NameModel):
    """Модель тега."""

    name = models.CharField(
        settings.TAG_NAME_VERBOSE_NAME,
        unique=True,
        max_length=settings.TAG_NAME_LENGTH,
    )
    slug = models.SlugField(
        settings.TAG_SLUG_VERBOSE_NAME,
        max_length=settings.TAG_SLUG_LENGTH,
        unique=True,
        validators=(validators.validate_slug,),
    )

    class Meta(NameModel.Meta):
        verbose_name = settings.TAG_MODEL_VERBOSE_NAME
        verbose_name_plural = settings.TAG_MODEL_VERBOSE_NAME_PLURAL
        default_related_name = settings.TAGS_RELATED_NAME
        ordering = ('name',)


class Recipe(NameModel):
    name = models.CharField(
        settings.RECIPE_NAME_VERBOSE_NAME,
        unique=True,
        max_length=settings.RECIPE_NAME_LENGTH,
    )
    author = models.ForeignKey(
        User,
        verbose_name=settings.RECIPE_AUTHOR_VERBOSE_NAME,
        on_delete=models.SET_NULL,
        null=True,
    )
    text = models.TextField(
        settings.RECIPE_TEXT_VERBOSE_NAME,
        max_length=settings.RECIPE_TEXT_LENGTH,
    )
    image = models.ImageField(
        settings.RECIPE_IMAGE_VERBOSE_NAME,
        upload_to=settings.RECIPES_IMAGES_UPLOAD_PATH,
    )
    cooking_time = models.PositiveSmallIntegerField(
        settings.RECIPE_COOKING_TIME_VERBOSE_NAME,
        default=settings.MIN_COOKING_TIME,
        validators=(validators.MinValueValidator(settings.MIN_COOKING_TIME),),
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name=settings.RECIPE_INGREDIENTS_VERBOSE_NAME,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=settings.RECIPE_TAGS_VERBOSE_NAME,
    )
    pub_date = models.DateTimeField(
        settings.RECIPE_PUB_DATE_VERBOSE_NAME,
        auto_now_add=True,
        editable=False,
    )

    class Meta(NameModel.Meta):
        verbose_name = settings.RECIPE_MODEL_VERBOSE_NAME
        verbose_name_plural = settings.RECIPE_MODEL_VERBOSE_NAME_PLURAL
        default_related_name = settings.RECIPES_RELATED_NAME
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name=settings.UNIQUE_RECIPE_NAME_AUTHOR_CONSTRAINT,
            ),
        )


class RecipeIngredient(models.Model):
    """Модель ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=settings.RECIPE_MODEL_VERBOSE_NAME,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=settings.INGREDIENT_MODEL_VERBOSE_NAME,
    )
    amount = models.PositiveSmallIntegerField(
        settings.RECIPE_INGREDIENT_AMOUNT_VERBOSE_NAME,
        default=settings.MIN_INGREDIENT_AMOUNT,
        validators=(
            validators.MinValueValidator(settings.MIN_INGREDIENT_AMOUNT),
        ),
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = settings.RECIPE_INGREDIENT_MODEL_VERBOSE_NAME
        verbose_name_plural = (
            settings.RECIPE_INGREDIENT_MODEL_VERBOSE_NAME_PLURAL
        )
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


class ShoppingCart(FavoriteShoppingCart):
    """Модель списка покупок."""

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = settings.SHOPPING_CART_MODEL_VERBOSE_NAME
        verbose_name_plural = settings.SHOPPING_CART_MODEL_VERBOSE_NAME_PLURAL
        default_related_name = settings.SHOPPING_LIST_RELATED_NAME
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=settings.UNIQUE_USER_RECIPE_SHOPPING_CONSTRAINT,
            )
        ]


class Favorite(FavoriteShoppingCart):
    """Модель избранного."""

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = settings.FAVORITE_MODEL_VERBOSE_NAME
        verbose_name_plural = settings.FAVORITE_MODEL_VERBOSE_NAME_PLURAL
        default_related_name = settings.FAVORITES_RELATED_NAME
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=settings.UNIQUE_USER_RECIPE_FAVORITE_CONSTRAINT,
            )
        ]
