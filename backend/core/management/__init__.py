import json
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient

FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """Команда для импорта данных из ingredients.json в базу данных."""

    help = 'Imports ingredients from ingredients.json into the database.'

    def handle(self, *args: Any, **options: Any) -> None:
        """Обработка команды импорта."""
        try:
            file_path = os.path.join(FILE_DIR, 'ingredients.json')
            if not os.path.exists(file_path):
                raise FileNotFoundError(f'File {file_path} not found.')

            with open(file_path, encoding='utf-8') as data_file_ingredients:
                ingredient_data = json.loads(data_file_ingredients.read())

                if not isinstance(ingredient_data, list):
                    raise ValueError(
                        'JSON must be a list of ingredient objects.'
                    )

                for item in ingredient_data:
                    # Проверяем, что обязательные поля есть
                    if not all(
                        key in item for key in ['name', 'measurement_unit']
                    ):
                        raise ValueError(
                            f"Invalid data in {item}: missing 'name' or 'measurement_unit'."
                        )

                    # Создаем или обновляем ингредиент
                    obj, created = Ingredient.objects.get_or_create(
                        name=item['name'],
                        defaults={
                            'measurement_unit': item['measurement_unit']
                        },
                    )
                    action = 'Created' if created else 'Already exists'
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'{action}: {obj.name} ({obj.measurement_unit})'
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS(f'File {file_path} imported successfully.')
            )

        except FileNotFoundError as e:
            raise CommandError(str(e))
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON format in {file_path}: {str(e)}')
        except ValueError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f'An unexpected error occurred: {str(e)}')
