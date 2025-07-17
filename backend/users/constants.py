from django.utils.translation import gettext_lazy as _

# Константы для длин полей
LENGTH_DATA_USER = 150
LENGTH_EMAIL = 254

# Константы для verbose name
USERNAME_VERBOSE_NAME = _('Имя пользователя')
FIRST_NAME_VERBOSE_NAME = _('Имя')
LAST_NAME_VERBOSE_NAME = _('Фамилия')
EMAIL_VERBOSE_NAME = _('Электронная почта')
PASSWORD_VERBOSE_NAME = _('Пароль')
AVATAR_VERBOSE_NAME = _('Аватар')

# Константы для сообщений валидатора
USERNAME_INVALID_CHARS_ERROR = _(
    'Имя пользователя может содержать только буквы, цифры и символы ./-/_')
