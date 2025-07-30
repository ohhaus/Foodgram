import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword123",
    }


@pytest.fixture
def user(user_data):
    return User.objects.create_user(**user_data)


@pytest.fixture
def another_user():
    return User.objects.create_user(
        email="another@example.com",
        username="anotheruser",
        first_name="Another",
        last_name="User",
        password="anotherpassword123",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestUserRegistration:
    def test_create_user_success(self, api_client, user_data):
        """Тест успешной регистрации пользователя."""
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data["email"]).exists()
        
        # Проверяем структуру ответа
        response_data = response.json()
        assert "id" in response_data
        assert response_data["email"] == user_data["email"]
        assert response_data["username"] == user_data["username"]
        assert response_data["first_name"] == user_data["first_name"]
        assert response_data["last_name"] == user_data["last_name"]
        assert "password" not in response_data

    def test_create_user_without_email(self, api_client, user_data):
        """Тест регистрации без email."""
        user_data.pop("email")
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_without_username(self, api_client, user_data):
        """Тест регистрации без username."""
        user_data.pop("username")
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_without_first_name(self, api_client, user_data):
        """Тест регистрации без first_name."""
        user_data.pop("first_name")
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_without_last_name(self, api_client, user_data):
        """Тест регистрации без last_name."""
        user_data.pop("last_name")
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_without_password(self, api_client, user_data):
        """Тест регистрации без password."""
        user_data.pop("password")
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_duplicate_email(self, api_client, user, user_data):
        """Тест регистрации с уже существующим email."""
        user_data["username"] = "newusername"
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_duplicate_username(self, api_client, user, user_data):
        """Тест регистрации с уже существующим username."""
        user_data["email"] = "newemail@example.com"
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_invalid_username(self, api_client, user_data):
        """Тест регистрации с недопустимыми символами в username."""
        user_data["username"] = "test user!"
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_too_long_fields(self, api_client, user_data):
        """Тест регистрации со слишком длинными полями."""
        user_data["username"] = "a" * 151
        url = reverse("users-list")
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserAuthentication:
    def test_get_token_success(self, api_client, user):
        """Тест успешного получения токена."""
        url = reverse("login")
        data = {"email": user.email, "password": "testpassword123"}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "auth_token" in response.json()

    def test_get_token_invalid_credentials(self, api_client, user):
        """Тест получения токена с неверными данными."""
        url = reverse("login")
        data = {"email": user.email, "password": "wrongpassword"}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_token_without_email(self, api_client):
        """Тест получения токена без email."""
        url = reverse("login")
        data = {"password": "testpassword123"}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_token_without_password(self, api_client, user):
        """Тест получения токена без password."""
        url = reverse("login")
        data = {"email": user.email}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_success(self, authenticated_client):
        """Тест успешного выхода из системы."""
        url = reverse("logout")
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestUserList:
    def test_get_user_list_unauthenticated(self, api_client, user):
        """Тест получения списка пользователей без аутентификации."""
        url = reverse("users-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "count" in response_data
        assert "results" in response_data

    def test_get_user_list_authenticated(self, authenticated_client, user):
        """Тест получения списка пользователей с аутентификацией."""
        url = reverse("users-list")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "count" in response_data
        assert "results" in response_data

    def test_get_user_list_with_limit(self, authenticated_client, user, another_user):
        """Тест получения списка пользователей с параметром limit."""
        url = reverse("users-list") + "?limit=1"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["results"]) == 1


@pytest.mark.django_db
class TestUserProfile:
    def test_get_user_profile_unauthenticated(self, api_client, user):
        """Тест получения профиля пользователя без аутентификации."""
        url = reverse("users-detail", kwargs={"id": user.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == user.id
        assert response_data["email"] == user.email

    def test_get_user_profile_authenticated(self, authenticated_client, user):
        """Тест получения профиля пользователя с аутентификацией."""
        url = reverse("users-detail", kwargs={"id": user.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == user.id

    def test_get_current_user_profile(self, authenticated_client, user):
        """Тест получения профиля текущего пользователя."""
        url = reverse("users-me")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == user.id

    def test_get_current_user_profile_unauthenticated(self, api_client):
        """Тест получения профиля текущего пользователя без аутентификации."""
        url = reverse("users-me")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserSubscriptions:
    def test_subscribe_to_user(self, authenticated_client, user, another_user):
        """Тест подписки на пользователя."""
        url = reverse("users-subscribe", kwargs={"id": another_user.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert user.follower.filter(author=another_user).exists()

    def test_subscribe_to_user_already_subscribed(self, authenticated_client, user, another_user):
        """Тест повторной подписки на пользователя."""
        # Создаем подписку
        user.follower.create(author=another_user)
        
        url = reverse("users-subscribe", kwargs={"id": another_user.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unsubscribe_from_user(self, authenticated_client, user, another_user):
        """Тест отписки от пользователя."""
        # Создаем подписку
        user.follower.create(author=another_user)
        
        url = reverse("users-subscribe", kwargs={"id": another_user.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not user.follower.filter(author=another_user).exists()

    def test_unsubscribe_from_user_not_subscribed(self, authenticated_client, user, another_user):
        """Тест отписки от пользователя без подписки."""
        url = reverse("users-subscribe", kwargs={"id": another_user.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_subscriptions(self, authenticated_client, user, another_user):
        """Тест получения списка подписок."""
        # Создаем подписку
        user.follower.create(author=another_user)
        
        url = reverse("users-subscriptions")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "count" in response_data
        assert "results" in response_data
        assert len(response_data["results"]) == 1

    def test_get_subscriptions_unauthenticated(self, api_client):
        """Тест получения списка подписок без аутентификации."""
        url = reverse("users-subscriptions")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserAvatar:
    def test_set_avatar(self, authenticated_client, user):
        """Тест установки аватара."""
        url = reverse("users-avatar")
        # Простой base64 изображение (1x1 пиксель)
        avatar_data = {
            "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }
        response = authenticated_client.put(url, avatar_data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.avatar

    def test_delete_avatar(self, authenticated_client, user):
        """Тест удаления аватара."""
        # Устанавливаем аватар
        user.avatar = "test_avatar.jpg"
        user.save()
        
        url = reverse("users-avatar")
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_set_avatar_unauthenticated(self, api_client):
        """Тест установки аватара без аутентификации."""
        url = reverse("users-avatar")
        avatar_data = {
            "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }
        response = api_client.put(url, avatar_data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
