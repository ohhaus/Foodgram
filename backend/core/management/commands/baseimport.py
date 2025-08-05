import os
from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class BaseImportCommand(BaseCommand, ABC):
    """Базовая команда импорта данных из файлов в БД."""

    help = 'Base class for importing data from files.'

    file_format = ''
    files = {}

    def handle(self, *args, **options):
        for file_name, (model, fields) in self.files.items():
            file_path = os.path.join(FILE_DIR, file_name)
            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f'Файл {file_path} не найден.')

                data = self.load_data(file_path)

                for item in data:
                    cleaned_data = {
                        field: item[field].strip()
                        for field in fields
                        if field in item and isinstance(item[field], str)
                    }

                    if not all(k in cleaned_data for k in fields):
                        raise ValueError(
                            f'Ошибка в {file_path}, отсутствуют поля: {fields}. '
                            f'Данные: {item}'
                        )

                    obj, created = model.objects.get_or_create(**cleaned_data)
                    action = 'Создан' if created else 'Уже существует'
                    self.stdout.write(self.style.SUCCESS(f'{action}: {obj}'))

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Импорт успешно завершён: {file_path}')
                )

            except Exception as e:
                raise CommandError(f'⛔ Ошибка при обработке {file_path}: {e}') from e

    @abstractmethod
    def load_data(self, file_path: str) -> list[dict[str, Any]]:
        """Загрузка данных из файла."""
        pass
