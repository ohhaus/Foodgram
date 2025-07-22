from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators

from users.models import User
from core.models import NameModel


class Ingredient(NameModel):
    """Модель ингредиента."""

    mesurement_unit = models.CharField(
        _('Единица измерения'),
        max_length=150,
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
        validators=(validators.validate_slug,)
    )

    class Meta(NameModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        defaul_related_name = 'tags'
        ordering = ('name',)


class RecipeModel(NameModel):
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
    # ingredients
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
                name='unique_for_author',
            ),
        )
