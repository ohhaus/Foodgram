from django.db import models


class NameModel(models.Model):
    """Абстрактная модель добавляющая название."""

    name = models.CharField(
        'Название',
        unique=True,
        max_length=200,
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
        verbose_name='Пользователь',
        null=True,
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'
