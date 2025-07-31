import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-3!b-39e%$a5u^6feutvy3bp*pfjc@l*i5mc+shmw%z^i#n$b4z',
)

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

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
    'rest_framework.authtoken',
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
# if 'test' in sys.argv or os.getenv('USE_SQLITE', 'False').lower() == 'true':
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3'
#             if 'test' not in sys.argv
#             else ':memory:',
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': os.getenv('DB_NAME', 'foodgram'),
#             'USER': os.getenv('DB_USER', 'foodgram_user'),
#             'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
#             'HOST': os.getenv('DB_HOST', 'db'),
#             'PORT': os.getenv('DB_PORT', '5432'),
#         }
#     }

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

CORS_ALLOW_ALL_ORIGINS = (
    os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True').lower() == 'true'
)
CORS_ALLOWED_ORIGINS = (
    os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if os.getenv('CORS_ALLOWED_ORIGINS')
    else []
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 6,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'SERIALIZERS': {
        'user_create': 'users.serializers.CustomUserCreateSerializer',
        'user': 'users.serializers.CustomUserSerializer',
        'current_user': 'users.serializers.CustomUserSerializer',
    },
    'PERMISSIONS': {
        'user': ['djoser.permissions.CurrentUserOrAdminOrReadOnly'],
        'user_list': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    }
}

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
