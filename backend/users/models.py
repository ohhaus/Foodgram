from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models

from core.constants import (
    AVATAR_VERBOSE_NAME,
    EMAIL_VERBOSE_NAME,
    FIRST_NAME_VERBOSE_NAME,
    FOLLOW_MODEL_VERBOSE_NAME,
    FOLLOW_MODEL_VERBOSE_NAME_PLURAL,
    FOLLOWER_RELATED_NAME,
    FOLLOWING_RELATED_NAME,
    LAST_NAME_VERBOSE_NAME,
    LENGTH_DATA_USER,
    LENGTH_EMAIL,
    NO_SELF_FOLLOW_CONSTRAINT,
    PASSWORD_VERBOSE_NAME,
    UNIQUE_FOLLOW_CONSTRAINT,
    USER_MODEL_VERBOSE_NAME,
    USER_MODEL_VERBOSE_NAME_PLURAL,
    USERNAME_INVALID_CHARS_ERROR,
    USERNAME_VERBOSE_NAME,
    USERS_AVATARS_UPLOAD_PATH,
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
            validators.RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=USERNAME_INVALID_CHARS_ERROR,
            ),
        ),
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
        max_length=128,
        blank=False,
        null=False,
    )
    avatar = models.ImageField(
        AVATAR_VERBOSE_NAME,
        upload_to=USERS_AVATARS_UPLOAD_PATH,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = USER_MODEL_VERBOSE_NAME
        verbose_name_plural = USER_MODEL_VERBOSE_NAME_PLURAL

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=FOLLOWER_RELATED_NAME,
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=FOLLOWING_RELATED_NAME,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = FOLLOW_MODEL_VERBOSE_NAME
        verbose_name_plural = FOLLOW_MODEL_VERBOSE_NAME_PLURAL
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name=UNIQUE_FOLLOW_CONSTRAINT,
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name=NO_SELF_FOLLOW_CONSTRAINT,
            ),
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
