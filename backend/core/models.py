from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from recipes.models import Recipe
from recipes.models import User


class NameModel(models.Model):
    """Абстрактная модель добавляющая название."""

    name = models.CharField(
        _('Название'),
        unique=True,
        max_length=settings.RECIPE_NAME_LENGTH,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


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
