# 🍽️ Foodgram - Продуктовый помощник

![Foodgram Screenshot](https://i.imgur.com/FcmUX5c.png)

**Foodgram** - это веб-приложение для публикации рецептов, составления списка покупок и организации кулинарного вдохновения.

https://foodgram-ya.myddns.me/

## 🛠 Технологии

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/Django-3.2-092E20?logo=django&logoColor=white" alt="Django 3.2" />
  <img src="https://img.shields.io/badge/DRF-3.13.1-9A1F1A?logo=django&logoColor=white" alt="Django REST Framework" />
  <img src="https://img.shields.io/badge/PostgreSQL-13-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-24.0-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Nginx-1.25-009639?logo=nginx&logoColor=white" alt="Nginx" />
  <img src="https://img.shields.io/badge/Gunicorn-23.0.0-499848?logo=gunicorn&logoColor=white" alt="Gunicorn" />
</div>

## 🌟 Основные возможности

- 📖 Публикация и просмотр рецептов с фотографиями
- ❤️ Добавление рецептов в избранное
- 🛒 Формирование списка покупок
- 📥 Скачивание списка покупок в формате TXT
- 🔗 Генерация коротких ссылок для рецептов
- 👥 Подписки на авторов рецептов
- 🔍 Фильтрация рецептов по тегам и другим параметрам

## 🚀 Быстрый старт

### Требования

- Docker 24.0+
- Docker Compose 2.0+

### Запуск в production

1. Скопируйте примеры файлов окружения:
   ```bash
   cp .env.example .env
   cp docker-compose.production.yml docker-compose.yml
   ```
2. Запустите проект:
    ```bash
    docker compose up -d --build
    ```
3. Примените миграции:
    ```bash
    docker compose exec backend python manage.py migrate
    ```
4. Соберите статику
    ```bash
    docker compose exec backend python manage.py collectstatic --no-input
    ```
5. Создайте суперпользователя (опционально):
    ```bash
    docker compose exec backend python manage.py createsuperuser
    ```

Проект будет доступен по адресу http://localhost:8000

## Импорт данных 

Проект включает универсальную систему импорта данных:
    ```bash
    # Импорт всех данных (ингредиенты и теги)
    docker compose exec backend python manage.py importdata

    # Импорт только ингредиентов
    docker compose exec backend python manage.py importdata --file=ingredients.json

    # Импорт только тегов
    docker compose exec backend python manage.py importdata --file=tags.csv
    ```

## 🌐 Развертывание 

Для развертывания на сервере используйте docker-compose.production.yml. Не забудьте:

1. Настроить .env файл с реальными значениями
2. Указать правильные ALLOWED_HOSTS
3. Настроить SSL/TLS для production окружения

## 📄 Лицензия

MIT License


