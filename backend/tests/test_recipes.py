import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        password="testpassword123",
    )


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


@pytest.fixture
def tag():
    return Tag.objects.create(
        name="Завтрак",
        slug="breakfast",
    )


@pytest.fixture
def ingredient():
    return Ingredient.objects.create(
        name="Мука",
        measurement_unit="г"
    )


@pytest.fixture
def recipe_data(tag, ingredient):
    return {
        "name": "Тестовый рецепт",
        "text": "Описание тестового рецепта",
        "cooking_time": 30,
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "tags": [tag.id],
        "ingredients": [{"id": ingredient.id, "amount": 100}]
    }


@pytest.fixture
def recipe(user, tag, ingredient):
    recipe = Recipe.objects.create(
        name="Тестовый рецепт",
        text="Описание тестового рецепта",
        cooking_time=30,
        author=user,
        image="test_image.jpg"
    )
    recipe.tags.add(tag)
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=100
    )
    return recipe


@pytest.mark.django_db
class TestTags:
    def test_get_tags_list(self, api_client, tag):
        """Тест получения списка тегов."""
        url = reverse("tags-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["id"] == tag.id
        assert response_data[0]["name"] == tag.name
        assert response_data[0]["slug"] == tag.slug

    def test_get_tag_detail(self, api_client, tag):
        """Тест получения детальной информации о теге."""
        url = reverse("tags-detail", kwargs={"pk": tag.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == tag.id
        assert response_data["name"] == tag.name
        assert response_data["slug"] == tag.slug


@pytest.mark.django_db
class TestIngredients:
    def test_get_ingredients_list(self, api_client, ingredient):
        """Тест получения списка ингредиентов."""
        url = reverse("ingredients-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["id"] == ingredient.id
        assert response_data[0]["name"] == ingredient.name
        assert response_data[0]["measurement_unit"] == ingredient.measurement_unit

    def test_get_ingredient_detail(self, api_client, ingredient):
        """Тест получения детальной информации об ингредиенте."""
        url = reverse("ingredients-detail", kwargs={"pk": ingredient.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == ingredient.id
        assert response_data["name"] == ingredient.name
        assert response_data["measurement_unit"] == ingredient.measurement_unit


@pytest.mark.django_db
class TestRecipes:
    def test_get_recipes_list_unauthenticated(self, api_client, recipe):
        """Тест получения списка рецептов без аутентификации."""
        url = reverse("recipes-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "count" in response_data
        assert "results" in response_data
        assert len(response_data["results"]) == 1

    def test_get_recipes_list_authenticated(self, authenticated_client, recipe):
        """Тест получения списка рецептов с аутентификацией."""
        url = reverse("recipes-list")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "count" in response_data
        assert "results" in response_data

    def test_get_recipe_detail(self, api_client, recipe):
        """Тест получения детальной информации о рецепте."""
        url = reverse("recipes-detail", kwargs={"pk": recipe.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == recipe.id
        assert response_data["name"] == recipe.name
        assert response_data["text"] == recipe.text
        assert response_data["cooking_time"] == recipe.cooking_time

    def test_create_recipe_success(self, authenticated_client, recipe_data):
        """Тест успешного создания рецепта."""
        url = reverse("recipes-list")
        response = authenticated_client.post(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.filter(name=recipe_data["name"]).exists()

    def test_create_recipe_unauthenticated(self, api_client, recipe_data):
        """Тест создания рецепта без аутентификации."""
        url = reverse("recipes-list")
        response = api_client.post(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_recipe_without_name(self, authenticated_client, recipe_data):
        """Тест создания рецепта без названия."""
        recipe_data.pop("name")
        url = reverse("recipes-list")
        response = authenticated_client.post(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_recipe_without_ingredients(self, authenticated_client, recipe_data):
        """Тест создания рецепта без ингредиентов."""
        recipe_data["ingredients"] = []
        url = reverse("recipes-list")
        response = authenticated_client.post(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_recipe_without_tags(self, authenticated_client, recipe_data):
        """Тест создания рецепта без тегов."""
        recipe_data["tags"] = []
        url = reverse("recipes-list")
        response = authenticated_client.post(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_recipe_invalid_cooking_time(self, authenticated_client, recipe_data):
        """Тест создания рецепта с неверным временем приготовления."""
        recipe_data["cooking_time"] = 0
        url = reverse("recipes-list")
        response = authenticated_client.post(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_recipe_success(self, authenticated_client, recipe, recipe_data):
        """Тест успешного обновления рецепта."""
        recipe_data["name"] = "Обновленный рецепт"
        url = reverse("recipes-detail", kwargs={"pk": recipe.id})
        response = authenticated_client.patch(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        recipe.refresh_from_db()
        assert recipe.name == "Обновленный рецепт"

    def test_update_recipe_not_author(self, api_client, another_user, recipe, recipe_data):
        """Тест обновления рецепта не автором."""
        api_client.force_authenticate(user=another_user)
        url = reverse("recipes-detail", kwargs={"pk": recipe.id})
        response = api_client.patch(url, recipe_data, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_recipe_success(self, authenticated_client, recipe):
        """Тест успешного удаления рецепта."""
        url = reverse("recipes-detail", kwargs={"pk": recipe.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Recipe.objects.filter(id=recipe.id).exists()

    def test_delete_recipe_not_author(self, api_client, another_user, recipe):
        """Тест удаления рецепта не автором."""
        api_client.force_authenticate(user=another_user)
        url = reverse("recipes-detail", kwargs={"pk": recipe.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestFavorites:
    def test_add_recipe_to_favorites(self, authenticated_client, recipe):
        """Тест добавления рецепта в избранное."""
        url = reverse("recipes-favorite", kwargs={"pk": recipe.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Favorite.objects.filter(user=authenticated_client.handler._force_user, recipe=recipe).exists()

    def test_add_recipe_to_favorites_unauthenticated(self, api_client, recipe):
        """Тест добавления рецепта в избранное без аутентификации."""
        url = reverse("recipes-favorite", kwargs={"pk": recipe.id})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_recipe_to_favorites_already_exists(self, authenticated_client, recipe, user):
        """Тест повторного добавления рецепта в избранное."""
        Favorite.objects.create(user=user, recipe=recipe)
        
        url = reverse("recipes-favorite", kwargs={"pk": recipe.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_recipe_from_favorites(self, authenticated_client, recipe, user):
        """Тест удаления рецепта из избранного."""
        Favorite.objects.create(user=user, recipe=recipe)
        
        url = reverse("recipes-favorite", kwargs={"pk": recipe.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Favorite.objects.filter(user=user, recipe=recipe).exists()

    def test_remove_recipe_from_favorites_not_exists(self, authenticated_client, recipe):
        """Тест удаления рецепта из избранного, когда его там нет."""
        url = reverse("recipes-favorite", kwargs={"pk": recipe.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestShoppingCart:
    def test_add_recipe_to_shopping_cart(self, authenticated_client, recipe):
        """Тест добавления рецепта в список покупок."""
        url = reverse("recipes-shopping-cart", kwargs={"pk": recipe.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert ShoppingCart.objects.filter(user=authenticated_client.handler._force_user, recipe=recipe).exists()

    def test_add_recipe_to_shopping_cart_unauthenticated(self, api_client, recipe):
        """Тест добавления рецепта в список покупок без аутентификации."""
        url = reverse("recipes-shopping-cart", kwargs={"pk": recipe.id})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_recipe_to_shopping_cart_already_exists(self, authenticated_client, recipe, user):
        """Тест повторного добавления рецепта в список покупок."""
        ShoppingCart.objects.create(user=user, recipe=recipe)
        
        url = reverse("recipes-shopping-cart", kwargs={"pk": recipe.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_recipe_from_shopping_cart(self, authenticated_client, recipe, user):
        """Тест удаления рецепта из списка покупок."""
        ShoppingCart.objects.create(user=user, recipe=recipe)
        
        url = reverse("recipes-shopping-cart", kwargs={"pk": recipe.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

    def test_remove_recipe_from_shopping_cart_not_exists(self, authenticated_client, recipe):
        """Тест удаления рецепта из списка покупок, когда его там нет."""
        url = reverse("recipes-shopping-cart", kwargs={"pk": recipe.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_shopping_cart(self, authenticated_client, recipe, user):
        """Тест скачивания списка покупок."""
        ShoppingCart.objects.create(user=user, recipe=recipe)
        
        url = reverse("recipes-download-shopping-cart")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text.txt; charset=utf-8"

    def test_download_shopping_cart_unauthenticated(self, api_client):
        """Тест скачивания списка покупок без аутентификации."""
        url = reverse("recipes-download-shopping-cart")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRecipeFiltering:
    def test_filter_recipes_by_author(self, api_client, recipe, user):
        """Тест фильтрации рецептов по автору."""
        url = reverse("recipes-list") + f"?author={user.id}"
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["count"] == 1

    def test_filter_recipes_by_tags(self, api_client, recipe, tag):
        """Тест фильтрации рецептов по тегам."""
        url = reverse("recipes-list") + f"?tags={tag.slug}"
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["count"] == 1

    def test_filter_recipes_by_favorites(self, authenticated_client, recipe, user):
        """Тест фильтрации рецептов по избранному."""
        Favorite.objects.create(user=user, recipe=recipe)
        
        url = reverse("recipes-list") + "?is_favorited=1"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["count"] == 1

    def test_filter_recipes_by_shopping_cart(self, authenticated_client, recipe, user):
        """Тест фильтрации рецептов по списку покупок."""
        ShoppingCart.objects.create(user=user, recipe=recipe)
        
        url = reverse("recipes-list") + "?is_in_shopping_cart=1"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["count"] == 1
