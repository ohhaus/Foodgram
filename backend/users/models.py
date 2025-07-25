from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from .constants import (
    USERNAME_VERBOSE_NAME,
    FIRST_NAME_VERBOSE_NAME,
    LAST_NAME_VERBOSE_NAME,
    EMAIL_VERBOSE_NAME,
    PASSWORD_VERBOSE_NAME,
    AVATAR_VERBOSE_NAME,
    LENGTH_DATA_USER,
    LENGTH_EMAIL,
    USERNAME_INVALID_CHARS_ERROR,
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        USERNAME_VERBOSE_NAME,
        max_length=LENGTH_DATA_USER,
        unique=True,
        blank=False,
        null=False,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=USERNAME_INVALID_CHARS_ERROR
            ),
        )
    )
    first_name = models.CharField(
        FIRST_NAME_VERBOSE_NAME,
        max_length=LENGTH_DATA_USER,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        LAST_NAME_VERBOSE_NAME,
        max_length=LENGTH_DATA_USER,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        EMAIL_VERBOSE_NAME,
        max_length=LENGTH_EMAIL,
        unique=True,
        blank=False,
        null=False,
    )
    password = models.CharField(
        PASSWORD_VERBOSE_NAME,
        max_length=LENGTH_DATA_USER,
        blank=False,
        null=False,
    )
    avatar = models.ImageField(
        AVATAR_VERBOSE_NAME,
        upload_to='users/avatars/',
        blank=True,
        null=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
