import json
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """Команда для импорта данных из JSON в БД."""

    help = 'Imports ingredients and tags from JSON files into the database.'

    def handle(self, *args: Any, **options: Any) -> None:
        """Обработка команды импорта."""
        files = {
            'ingredients.json': (Ingredient, ['name', 'measurement_unit']),
            'tags.json': (Tag, ['name', 'slug']),
        }

        for file_name, (model, required_fields) in files.items():
            try:
                file_path = os.path.join(FILE_DIR, file_name)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f'File {file_path} not found.')

                with open(file_path, encoding='utf-8') as data_file:
                    data = json.loads(data_file.read())

                    if not isinstance(data, list):
                        raise ValueError(
                            f'{file_name} must be a list of objects.'
                        )

                    for item in data:
                        if not all(key in item for key in required_fields):
                            raise ValueError(
                                f'Invalid data in {item} in {file_name}: '
                            f'missing {required_fields}.'
                            )

                        defaults = {
                            k: item[k] for k in required_fields if k != 'id'
                        }
                        obj, created = model.objects.get_or_create(
                            **{required_fields[0]: item[required_fields[0]]},
                            defaults=defaults,
                        )
                        action = 'Created' if created else 'Already exists'
                        self.stdout.write(
                            self.style.SUCCESS(f'{action}: {obj}')
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'File {file_path} imported successfully.'
                    )
                )

            except FileNotFoundError as e:
                raise CommandError(f'Файл не найден: {e}') from e
            except json.JSONDecodeError as e:
                raise CommandError(
                    f'Некорректный формат JSON в {file_path}: {e}'
                ) from e
            except ValueError as e:
                raise CommandError(f'Недопустимое значение: {e}') from e
            except Exception as e:
                raise CommandError(
                    f'Произошла непредвиденная ошибка: {e}'
                ) from e
