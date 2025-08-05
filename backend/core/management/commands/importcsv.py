import csv
from core.management.commands.baseimport import BaseImportCommand
from recipes.models import Ingredient, Tag


class Command(BaseImportCommand):
    """Импорт ингредиентов и тегов из CSV."""

    help = 'Импортирует ингредиенты и теги из CSV файлов.'
    file_format = 'csv'

    files = {
        'ingredients.csv': (Ingredient, ['name', 'measurement_unit']),
        'tags.csv': (Tag, ['name', 'slug']),
    }

    def load_data(self, file_path):
        try:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except csv.Error as e:
            raise ValueError(f'Некорректный CSV формат: {e}') from e
