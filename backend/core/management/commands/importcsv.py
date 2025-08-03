import csv
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """Команда для импорта данных из CSV файлов в БД."""

    help = 'Imports ingredients and tags from CSV files into the database.'

    def handle(self, *args: Any, **options: Any) -> None:
        """Обработка команды импорта."""
        files = {
            'ingredients.csv': (Ingredient, ['name', 'measurement_unit']),
            'tags.csv': (Tag, ['name', 'slug']),
        }

        for _file_name, (model, required_fields) in files.items():
            try:
                file_path = os.path.join(FILE_DIR, 'ingredients.csv')
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f'File {file_path} not found.')

                with open(file_path, encoding='utf-8') as data_file:
                    csv_reader = csv.DictReader(data_file)
                    if not set(required_fields).issubset(
                        csv_reader.fieldnames
                    ):
                        raise ValueError(
                            f'CSV {file_path} must contain {required_fields} columns.'
                        )

                    for row in csv_reader:
                        if not all(
                            row.get(field) for field in required_fields
                        ):
                            raise ValueError(
                                f'Invalid data in row {row} in {file_path}: '
                            f'missing {required_fields}.'
                            )

                        defaults = {
                            k: row[k].strip()
                            for k in required_fields
                            if k != required_fields[0]
                        }
                        obj, created = model.objects.get_or_create(
                            **{
                                required_fields[0]: row[
                                    required_fields[0]
                                ].strip()
                            },
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
            except csv.Error as e:
                raise CommandError(
                    f'Некорректный формат CSV в {file_path}: {e}'
                ) from e
            except ValueError as e:
                raise CommandError(f'Недопустимое значение: {e}') from e
            except Exception as e:
                raise CommandError(
                    f'Произошла непредвиденная ошибка: {e}'
                ) from e
