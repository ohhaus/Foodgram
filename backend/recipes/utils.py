import base64
import uuid
from collections import defaultdict

from django.db import transaction

from .models import ShortLink


def generate_shopping_cart_txt(recipes):
    """Генерация TXT-файла со списком покупок."""

    ingredients = defaultdict(int)
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            ingr = recipe_ingredient.ingredient
            key = f'{ingr.name} ({ingr.measurement_unit})'
            ingredients[key] += recipe_ingredient.amount

    lines = []
    lines.append('Список покупок')
    lines.append('----------------')

    if not ingredients:
        lines.append('Ваш список покупок пуст.')
    else:
        for ingredient, amount in ingredients.items():
            lines.append(f'• {ingredient}: {amount}')

    content = '\n'.join(lines)
    return content


def generate_unique_short_code(min_length=6, max_length=10):
    """Генерирует уникальный короткий код для ссылки."""
    for length in range(min_length, max_length + 1):
        with transaction.atomic():
            code = (
                base64.urlsafe_b64encode(uuid.uuid4().bytes)[:length]
                .decode('utf-8')
                .rstrip('=')
            )
            if not ShortLink.objects.filter(short_code=code).exists():
                return code
    raise ValueError('Пространство кодов исчерпано.')
