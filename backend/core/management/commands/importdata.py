import csv
import json

from core.management.commands.baseimport import BaseImportCommand
from recipes.models import Ingredient, Tag


class Command(BaseImportCommand):
    """Универсальный импорт данных из файлов различных форматов."""

    help = 'Импортирует данные из CSV/JSON файлов'

    files = {
        'ingredients.csv': Ingredient,
        'tags.csv': Tag,
        'ingredients.json': Ingredient,
        'tags.json': Tag,
    }

    def load_data(self, file_path: str) -> list[dict]:
        """Определяет формат файла и загружает данные."""
        if file_path.endswith('.csv'):
            return self.load_csv(file_path)
        elif file_path.endswith('.json'):
            return self.load_json(file_path)
        raise ValueError('Неподдерживаемый формат файла')

    def load_csv(self, file_path: str) -> list[dict]:
        """Загрузка данных из CSV файла."""
        try:
            with open(file_path, encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except (OSError, csv.Error) as e:
            raise ValueError(f'Ошибка CSV: {e}') from e

    def load_json(self, file_path: str) -> list[dict]:
        """Загрузка данных из JSON файла."""
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise TypeError('JSON должен содержать список объектов')
                return data
        except (OSError, json.JSONDecodeError) as e:
            raise ValueError(f'Ошибка JSON: {e}') from e
