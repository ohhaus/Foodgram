import os
from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import models

FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class BaseImportCommand(BaseCommand, ABC):
    """Базовая команда импорта данных из файлов в БД."""

    help = 'Базовый класс для импорта данных из файлов.'
    files = {}

    def handle(self, *args, **options):
        for file_name, model in self.files.items():
            file_path = os.path.join(FILE_DIR, file_name)
            self.stdout.write(f'🔍 Обработка файла: {file_path}')

            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError('Файл не найден')

                data = self.load_data(file_path)
                if not isinstance(data, list):
                    raise TypeError('Данные должны быть списком объектов')

                self.import_data(model, data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Успешно импортировано {len(data)} записей '
                        f'для {model.__name__} из {file_name}'
                    )
                )

            except Exception as e:
                raise CommandError(
                    f'⛔ Ошибка при обработке {file_name}: {e}'
                ) from e

    def import_data(self, model: type[models.Model], data: list[dict]):
        """Основная логика импорта данных в модель."""
        required_fields = self.get_required_fields(model)

        for item in data:
            cleaned_data = self.clean_item_data(item)
            self.validate_fields(cleaned_data, required_fields, model.__name__)

            obj, created = model.objects.get_or_create(**cleaned_data)
            status = 'Создан' if created else 'Обновлен'
            self.stdout.write(f'  {status}: {obj}')

    def clean_item_data(self, item_data: dict) -> dict:
        """Очистка и нормализация данных перед импортом."""
        return {
            key: value.strip() if isinstance(value, str) else value
            for key, value in item_data.items()
        }

    def get_required_fields(self, model: type[models.Model]) -> list[str]:
        """Получение списка обязательных полей модели."""
        return [
            field.name
            for field in model._meta.fields
            if not field.blank and not field.null and not field.auto_created
        ]

    def validate_fields(
        self, data: dict, required_fields: list[str], model_name: str
    ):
        """Проверка наличия обязательных полей."""
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(
                f'Для модели {model_name} отсутствуют обязательные поля: '
                f'{", ".join(missing)}'
            )

    @abstractmethod
    def load_data(self, file_path: str) -> list[dict[str, Any]]:
        """Загрузка данных из файла (должен быть реализован в дочерних классах)."""
        raise NotImplementedError
