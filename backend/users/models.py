from django.contrib.auth.models import AbstractUser
from django.db import models


LENGTH_DATA_USER = 150
LENGTH_EMAIL = 254
LIMITED_NUMBER_OF_CHARACTERS = f'Набор символов не более {LENGTH_DATA_USER}'


# TODO: Сделать валидацию username
class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        'Уникальное имя пользователя',
        max_length=LENGTH_DATA_USER,
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        'Имя',
        max_length=LENGTH_DATA_USER,
        blank=False,
        null=False,
        # help_text=LIMITED_NUMBER_OF_CHARACTERS,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LENGTH_DATA_USER,
        blank=False,
        null=False,
        # help_text=LIMITED_NUMBER_OF_CHARACTERS,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=LENGTH_EMAIL,
        unique=True,
        blank=False,
        null=False,

    )
    password = models.CharField(
        'Пароль',
        max_length=LENGTH_DATA_USER,
        blank=False,
        null=False,
        # help_text=LIMITED_NUMBER_OF_CHARACTERS,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи',

    def __str__(self):
        return f'{self.username} {self.email}'


class Follow(models.Model):
    """Модель подписчика."""
