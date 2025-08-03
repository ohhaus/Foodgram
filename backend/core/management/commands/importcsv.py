import csv
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """Команда для импорта данных из CSV файлов в БД."""

    help = (
        'Imports ingredients and tags from CSV files into the database.'
    )

    def handle(self, *args: Any, **options: Any) -> None:
        files = {
            'ingredients.csv': (Ingredient, ['name', 'measurement_unit']),
            'tags.csv': (Tag, ['name', 'slug']),
        }

        for file_name, (model, required_fields) in files.items():
            file_path = os.path.join(FILE_DIR, file_name)

            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(
                        f'File {file_path} not found.'
                    )

                with open(file_path, encoding='utf-8') as data_file:
                    csv_reader = csv.DictReader(data_file)

                    if not set(required_fields).issubset(
                        csv_reader.fieldnames
                    ):
                        raise ValueError(
                            f'CSV {file_path} must contain columns: '
                            f'{required_fields}.'
                        )

                    for row in csv_reader:
                        if not all(
                            row.get(field) for field in required_fields
                        ):
                            raise ValueError(
                                f'Invalid row in {file_path}: {row}. '
                                f'Missing one of {required_fields}.'
                            )

                        defaults = {
                            k: row[k].strip()
                            for k in required_fields[1:]
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
                    self.style.SUCCESS(f'Imported: {file_path}')
                )

            except FileNotFoundError as e:
                raise CommandError(
                    f'Файл не найден: {e}'
                ) from e
            except csv.Error as e:
                raise CommandError(
                    f'Ошибка CSV в {file_path}: {e}'
                ) from e
            except ValueError as e:
                raise CommandError(
                    f'Недопустимое значение: {e}'
                ) from e
            except Exception as e:
                raise CommandError(
                    f'Непредвиденная ошибка: {e}'
                ) from e
