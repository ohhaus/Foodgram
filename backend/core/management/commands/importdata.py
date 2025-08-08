import csv
import json
import os

from django.core.management.base import CommandError, CommandParser
from django.db import models

from core.management.commands.baseimport import FILE_DIR, BaseImportCommand
from recipes.models import Ingredient, Tag


class Command(BaseImportCommand):
    """Универсальный импорт данных из файлов различных форматов."""

    help = 'Импортирует данные из CSV/JSON с возможностью выбора формата'

    files: dict[str, type[models.Model]] = {
        'ingredients.csv': Ingredient,
        'tags.csv': Tag,
        'ingredients.json': Ingredient,
        'tags.json': Tag,
    }

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--format',
            choices=['json', 'csv', 'all'],
            default='all',
            help=('Формат файлов для импорта: json, csv, all (по умолчанию)'),
        )
        parser.add_argument(
            '--files', nargs='+', help='Список конкретных файлов для импорта'
        )

    def handle(self, *args, **options):
        files_to_process = self.get_files_to_process(options)

        for file_name, model in files_to_process.items():
            file_path = os.path.join(FILE_DIR, file_name)
            self.stdout.write(f'🔍 Обработка файла: {file_path}')

            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError('Файл не найден')

                data = self.load_data(file_path)
                if not isinstance(data, list):
                    raise TypeError('Данные должны быть списком объектов')

                self.import_data(model, data)
                msg = (
                    f'✅ Успешно импортировано {len(data)} записей '
                    f'для {model.__name__} из {file_name}'
                )
                self.stdout.write(self.style.SUCCESS(msg))

            except Exception as e:
                raise CommandError(
                    f'⛔ Ошибка при обработке {file_name}: {e}'
                ) from e

    def get_files_to_process(self, options) -> dict[str, type[models.Model]]:
        """Возвращает список файлов для обработки на основе параметров."""
        selected_files = {}

        if options['files']:
            for file_name in options['files']:
                if file_name in self.files:
                    selected_files[file_name] = self.files[file_name]
                else:
                    warning = (
                        f'⚠️ Файл "{file_name}" не найден в списке доступных.'
                    )
                    self.stdout.write(self.style.WARNING(warning))
            return selected_files

        file_format = options['format']
        for file_name, model in self.files.items():
            is_json = file_format == 'json' and file_name.endswith('.json')
            is_csv = file_format == 'csv' and file_name.endswith('.csv')
            if file_format == 'all' or is_json or is_csv:
                selected_files[file_name] = model

        return selected_files

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
