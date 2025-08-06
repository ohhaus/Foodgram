# ================================
# КОНСТАНТЫ ПРОЕКТА
# ================================

DEFAULT_PAGE_SIZE = 6

# User model field settings
LENGTH_DATA_USER = 150
LENGTH_EMAIL = 254
USERNAME_VERBOSE_NAME = 'Имя пользователя'
FIRST_NAME_VERBOSE_NAME = 'Имя'
LAST_NAME_VERBOSE_NAME = 'Фамилия'
EMAIL_VERBOSE_NAME = 'Адрес электронной почты'
PASSWORD_VERBOSE_NAME = 'Пароль'
AVATAR_VERBOSE_NAME = 'Аватар'
USERS_AVATARS_UPLOAD_PATH = 'users/avatars/'

# User model verbose names
USER_MODEL_VERBOSE_NAME = 'Пользователь'
USER_MODEL_VERBOSE_NAME_PLURAL = 'Пользователи'

# Follow model settings
FOLLOWER_RELATED_NAME = 'follower'
FOLLOWING_RELATED_NAME = 'following'
FOLLOW_MODEL_VERBOSE_NAME = 'Подписка'
FOLLOW_MODEL_VERBOSE_NAME_PLURAL = 'Подписки'
UNIQUE_FOLLOW_CONSTRAINT = 'unique_follow'
NO_SELF_FOLLOW_CONSTRAINT = 'no_self_follow'

# Username validation
USERNAME_INVALID_CHARS_ERROR = 'Имя пользователя содержит недопустимые символы'

# Recipe model settings
RECIPE_NAME_MAX_LENGTH = 256
RECIPE_TEXT_MAX_LENGTH = 1000
COOKING_TIME_MIN_VALUE = 1
COOKING_TIME_MAX_VALUE = 32000

# Ingredient model settings
INGREDIENT_NAME_MAX_LENGTH = 128
INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH = 64

# Tag model settings
TAG_NAME_MAX_LENGTH = 32
TAG_SLUG_MAX_LENGTH = 32

# Recipe ingredient model settings
RECIPE_INGREDIENT_AMOUNT_MIN_VALUE = 1
RECIPE_INGREDIENT_AMOUNT_MAX_VALUE = 32000
