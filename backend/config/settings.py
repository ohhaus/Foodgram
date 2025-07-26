import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-3!b-39e%$a5u^6feutvy3bp*pfjc@l*i5mc+shmw%z^i#n$b4z',
)

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_filters',
    'djoser',
    'corsheaders',
]

LOCAL_APPS = [
    'core',
    'recipes',
    'users',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USER': 'True',
    'SERIALIZERS': {
        'current_user': 'users.serializers.UserSerializer',
    },
    'PERMISSIONS': {
        'user': ['djoser.permissions.CurrentUserOrAdminOrReadOnly'],
    },
}

# ================================
# КОНСТАНТЫ ПРОЕКТА
# ================================

# Константы для длин полей
LENGTH_DATA_USER = 150
LENGTH_EMAIL = 254
RECIPE_NAME_LENGTH = 256
TAG_NAME_LENGTH = 256
TAG_SLUG_LENGTH = 256
INGREDIENT_NAME_LENGTH = 256
MEASUREMENT_UNIT_LENGTH = 15
RECIPE_TEXT_LENGTH = 5000

# Константы для валидации
MIN_COOKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1

# Константы для verbose name пользователей
USERNAME_VERBOSE_NAME = 'Имя пользователя'
FIRST_NAME_VERBOSE_NAME = 'Имя'
LAST_NAME_VERBOSE_NAME = 'Фамилия'
EMAIL_VERBOSE_NAME = 'Электронная почта'
PASSWORD_VERBOSE_NAME = 'Пароль'
AVATAR_VERBOSE_NAME = 'Аватар'

# Константы для verbose name рецептов
RECIPE_NAME_VERBOSE_NAME = 'Название рецепта'
RECIPE_TEXT_VERBOSE_NAME = 'Описание рецепта'
RECIPE_IMAGE_VERBOSE_NAME = 'Изображение рецепта'
RECIPE_COOKING_TIME_VERBOSE_NAME = 'Время приготовления (мин)'
RECIPE_PUB_DATE_VERBOSE_NAME = 'Дата публикации'
RECIPE_AUTHOR_VERBOSE_NAME = 'Автор рецепта'
RECIPE_INGREDIENTS_VERBOSE_NAME = 'Ингредиенты'
RECIPE_TAGS_VERBOSE_NAME = 'Теги'

# Константы для verbose name ингредиентов и тегов
INGREDIENT_NAME_VERBOSE_NAME = 'Название ингредиента'
INGREDIENT_MEASUREMENT_UNIT_VERBOSE_NAME = 'Единица измерения'
TAG_NAME_VERBOSE_NAME = 'Название тега'
TAG_SLUG_VERBOSE_NAME = 'Слаг тега'
TAG_COLOR_VERBOSE_NAME = 'Цвет тега'

# Константы для verbose name связей
RECIPE_INGREDIENT_AMOUNT_VERBOSE_NAME = 'Количество ингредиента'
FAVORITE_VERBOSE_NAME = 'Избранный рецепт'
SHOPPING_CART_VERBOSE_NAME = 'Список покупок'
FOLLOW_VERBOSE_NAME = 'Подписка'

# Константы для единиц измерения
MEASUREMENT_UNITS = [
    ('г', 'Грамм'),
    ('кг', 'Килограмм'),
    ('мл', 'Миллилитр'),
    ('л', 'Литр'),
    ('шт', 'Штука'),
    ('ч. л', 'Чайная ложка'),
    ('ст. л', 'Столовая ложка'),
]

# Константы для сообщений валидатора
USERNAME_INVALID_CHARS_ERROR = (
    'Имя пользователя может содержать только буквы, цифры и символы @ . + - _'
)
COOKING_TIME_MIN_ERROR = (
    f'Время готовки должно быть больше {MIN_COOKING_TIME} минут!'
)
INGREDIENT_AMOUNT_MIN_ERROR = (
    f'Количество ингредиента должно быть больше {MIN_INGREDIENT_AMOUNT}!'
)

INGREDIENTS_REQUIRED_ERROR = 'Должен быть хотя бы один ингредиент!'
TAGS_REQUIRED_ERROR = 'Должен быть хотя бы один тег!'
DUPLICATE_INGREDIENTS_ERROR = 'Ингредиенты не должны повторяться!'
DUPLICATE_TAGS_ERROR = 'Теги не должны повторяться!'

# Константы для сообщений о дублировании в базе данных
FAVORITE_ALREADY_EXISTS_ERROR = 'Рецепт уже добавлен в избранное!'
SHOPPING_CART_ALREADY_EXISTS_ERROR = 'Рецепт уже добавлен в список покупок!'
FOLLOW_ALREADY_EXISTS_ERROR = 'Вы уже подписаны на этого пользователя!'
SELF_FOLLOW_ERROR = 'Нельзя подписаться на самого себя!'
RECIPE_NAME_AUTHOR_UNIQUE_ERROR = (
    'У этого автора уже есть рецепт с таким названием!'
)

# Константы для названий моделей (verbose_name)
USER_MODEL_VERBOSE_NAME = 'Пользователь'
USER_MODEL_VERBOSE_NAME_PLURAL = 'Пользователи'
RECIPE_MODEL_VERBOSE_NAME = 'Рецепт'
RECIPE_MODEL_VERBOSE_NAME_PLURAL = 'Рецепты'
INGREDIENT_MODEL_VERBOSE_NAME = 'Ингредиент'
INGREDIENT_MODEL_VERBOSE_NAME_PLURAL = 'Ингредиенты'
TAG_MODEL_VERBOSE_NAME = 'Тег'
TAG_MODEL_VERBOSE_NAME_PLURAL = 'Теги'
RECIPE_INGREDIENT_MODEL_VERBOSE_NAME = 'Ингредиент в рецепте'
RECIPE_INGREDIENT_MODEL_VERBOSE_NAME_PLURAL = 'Ингредиенты в рецепте'
FAVORITE_MODEL_VERBOSE_NAME = 'Избранный рецепт'
FAVORITE_MODEL_VERBOSE_NAME_PLURAL = 'Избранные рецепты'
SHOPPING_CART_MODEL_VERBOSE_NAME = 'Список покупок'
SHOPPING_CART_MODEL_VERBOSE_NAME_PLURAL = 'Списки покупок'
FOLLOW_MODEL_VERBOSE_NAME = 'Подписка'
FOLLOW_MODEL_VERBOSE_NAME_PLURAL = 'Подписки'

# Константы для названий constraint'ов
UNIQUE_FOLLOW_CONSTRAINT = 'unique_follow'
NO_SELF_FOLLOW_CONSTRAINT = 'no_self_follow'
UNIQUE_RECIPE_NAME_AUTHOR_CONSTRAINT = 'unique_name_author'
UNIQUE_USER_RECIPE_SHOPPING_CONSTRAINT = 'unique_user_recipe_shopping'
UNIQUE_USER_RECIPE_FAVORITE_CONSTRAINT = 'unique_user_recipe_favorite'

# Константы для related_name
RECIPES_RELATED_NAME = 'recipes'
INGREDIENTS_RELATED_NAME = 'ingredients'
TAGS_RELATED_NAME = 'tags'
FAVORITES_RELATED_NAME = 'favorites'
SHOPPING_LIST_RELATED_NAME = 'shopping_list'
FOLLOWER_RELATED_NAME = 'follower'
FOLLOWING_RELATED_NAME = 'following'
RECIPE_INGREDIENTS_RELATED_NAME = 'recipe_ingredients'

# Константы для upload_to путей
USERS_AVATARS_UPLOAD_PATH = 'users/avatars/'
RECIPES_IMAGES_UPLOAD_PATH = 'recipes/images/'
