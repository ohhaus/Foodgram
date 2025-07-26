from datetime import datetime
from pathlib import Path

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe


def handle_add_or_remove_recipe(serializer_class, model, request, recipe_id):
    """Добавление или удаление рецепта в/из избранного или списка покупок."""
    user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        serializer = serializer_class(data={'recipe': recipe.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    instance = get_object_or_404(model, user=user, recipe=recipe)
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@receiver(post_delete, sender=Recipe)
def delete_recipe_image(sender, instance, **kwargs):
    """Удаляет картинку после удалания рецепта."""
    if instance.image:
        image_path = Path(instance.image.path)
        if image_path.exists():
            image_path.unlink(missing_ok=True)


def generate_shopping_list_file(user, ingredients):
    """Генерация текстового файла со списком покупок."""
    today = datetime.today()
    filename = f'{user.username}_shopping_list.txt'

    lines = (
        [
            f'Список покупок для пользователя: {user.username}\n',
            f'Дата: {today:%Y-%m-%d}\n',
        ]
        + [
            f'- {item["ingredient__name"]} '
            f'({item["ingredient__measurement_unit"]}) — {item["amount"]}'
            for item in ingredients
        ]
        + [f'\n\nFoodgram ({today:%Y})']
    )

    content = '\n'.join(lines)
    response = HttpResponse(content, content_type='text.txt; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
