import json

from core.management.commands.baseimport import BaseImportCommand
from recipes.models import Ingredient, Tag


class Command(BaseImportCommand):
    """Импорт ингредиентов и тегов из JSON."""

    help = 'Импортирует ингредиенты и теги из JSON файлов.'
    file_format = 'json'

    files = {
        'ingredients.json': (Ingredient, ['name', 'measurement_unit']),
        'tags.json': (Tag, ['name', 'slug']),
    }

    def load_data(self, file_path):
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError('JSON должен содержать список объектов.')
                return data
        except json.JSONDecodeError as e:
            raise ValueError(f'Ошибка разбора JSON: {e}') from e
