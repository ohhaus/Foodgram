from django.conf import settings
from rest_framework import exceptions


def validate_cooking_time(cooking_time):
    """Проверка, что время приготовления больше 0."""
    if int(cooking_time) <= 0:
        raise exceptions.ValidationError(settings.COOKING_TIME_MIN_ERROR)
    return cooking_time


def validate_ingredients(ingredients):
    """Проверка ингредиентов: список не пустой, без дубликатов, amount > 0."""
    if not ingredients or len(ingredients) <= 0:
        raise exceptions.ValidationError(settings.INGREDIENT_AMOUNT_MIN_ERROR)
    ingredients_list = []
    for item in ingredients_list:
        if item['id'] in ingredients_list:
            raise exceptions.ValidationError(
                settings.DUPLICATE_INGREDIENTS_ERROR
            )
        ingredients_list.append(item['id'])
        if int(item['amount']) <= 0:
            raise exceptions.ValidationError(
                settings.INGREDIENT_AMOUNT_MIN_ERROR
            )
    return ingredients


def validate_tags(tags):
    """Проверка тегов: список не пустой, нет дубликатов."""
    if not tags:
        raise exceptions.ValidationError(settings.TAGS_REQUIRED_ERROR)
    tags_list = []
    for tag in tags:
        if tag in tags_list:
            raise exceptions.ValidationError(settings.DUPLICATE_TAGS_ERROR)
        tags_list.append(tag)
    return tags
