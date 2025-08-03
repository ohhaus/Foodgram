import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestTagAPI:
    def test_tag_list(self, client):
        """Тест получения списка тегов."""
        url = reverse('api:tag-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_tag_detail(self, client, tag):
        """Тест получения информации о конкретном теге."""
        url = reverse('api:tag-detail', kwargs={'id': tag.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == tag.name
        assert response.data['slug'] == tag.slug
