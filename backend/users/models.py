from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        settings.USERNAME_VERBOSE_NAME,
        max_length=settings.LENGTH_DATA_USER,
        unique=True,
        blank=False,
        null=False,
        validators=(
            validators.RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=settings.USERNAME_INVALID_CHARS_ERROR,
            ),
        ),
    )
    first_name = models.CharField(
        settings.FIRST_NAME_VERBOSE_NAME,
        max_length=settings.LENGTH_DATA_USER,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        settings.LAST_NAME_VERBOSE_NAME,
        max_length=settings.LENGTH_DATA_USER,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        settings.EMAIL_VERBOSE_NAME,
        max_length=settings.LENGTH_EMAIL,
        unique=True,
        blank=False,
        null=False,
    )
    password = models.CharField(
        settings.PASSWORD_VERBOSE_NAME,
        max_length=128,
        blank=False,
        null=False,
    )
    avatar = models.ImageField(
        settings.AVATAR_VERBOSE_NAME,
        upload_to=settings.USERS_AVATARS_UPLOAD_PATH,
        blank=True,
        null=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = settings.USER_MODEL_VERBOSE_NAME
        verbose_name_plural = settings.USER_MODEL_VERBOSE_NAME_PLURAL

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=settings.FOLLOWER_RELATED_NAME,
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=settings.FOLLOWING_RELATED_NAME,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = settings.FOLLOW_MODEL_VERBOSE_NAME
        verbose_name_plural = settings.FOLLOW_MODEL_VERBOSE_NAME_PLURAL
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name=settings.UNIQUE_FOLLOW_CONSTRAINT,
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name=settings.NO_SELF_FOLLOW_CONSTRAINT,
            ),
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
