from django.db import models
from django.utils.translation import gettext_lazy as _


class NameModel(models.Model):
    """Абстрактная модель добавляющая название."""

    name = models.CharField(
        _('Название'),
        unique=True,
        max_length=200,  # Default max_length, will be overridden in child models
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class FavoriteShoppingCart(models.Model):
    """Асбстрактная модель добавляющая пользователя и рецепт"""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        null=True,
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'
