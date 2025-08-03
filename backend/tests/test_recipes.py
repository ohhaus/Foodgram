import pytest
from django.urls import reverse
from rest_framework import status

from recipes.models import Recipe, Tag


@pytest.mark.django_db
class TestRecipeAPI:
    def test_recipe_list_unauthorized(self, client):
        """Тест получения списка рецептов без авторизации."""
        url = reverse('api:recipe-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data.get('results'), list)

    def test_recipe_creation(self, auth_client, user, tag):
        """Тест создания рецепта авторизованным пользователем."""
        url = reverse('api:recipe-list')
        payload = {
            'name': 'Тестовый рецепт',
            'text': 'Описание тестового рецепта',
            'cooking_time': 30,
            'tags': [tag.id],
            'ingredients': [
                {'id': 1, 'amount': 100}
            ]
        }
        
        response = auth_client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.filter(name='Тестовый рецепт').exists()

    def test_recipe_detail(self, client, recipe):
        """Тест получения детальной информации о рецепте."""
        url = reverse('api:recipe-detail', kwargs={'id': recipe.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == recipe.name
        assert response.data['cooking_time'] == recipe.cooking_time

    def test_recipe_update_by_author(self, auth_client, recipe, tag):
        """Тест обновления рецепта автором."""
        url = reverse('api:recipe-detail', kwargs={'id': recipe.id})
        payload = {
            'name': 'Обновленный рецепт',
            'text': recipe.text,
            'cooking_time': recipe.cooking_time,
            'tags': [tag.id],
            'ingredients': [
                {'id': 1, 'amount': 100}
            ]
        }
        
        response = auth_client.patch(url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        recipe.refresh_from_db()
        assert recipe.name == 'Обновленный рецепт'
