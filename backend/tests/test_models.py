import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart
from users.models import Follow

User = get_user_model()


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
class TestUserModel:
    def test_create_user_success(self):
        """Тест успешного создания пользователя."""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.check_password("testpassword123")

    def test_user_str_method(self, user):
        """Тест строкового представления пользователя."""
        assert str(user) == user.username

    def test_user_email_unique(self, user):
        """Тест уникальности email."""
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="test@example.com",
                username="anotheruser",
                first_name="Another",
                last_name="User",
                password="anotherpassword123",
            )

    def test_user_username_unique(self, user):
        """Тест уникальности username."""
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="another@example.com",
                username="testuser",
                first_name="Another",
                last_name="User",
                password="anotherpassword123",
            )


@pytest.mark.django_db
class TestTagModel:
    def test_create_tag_success(self):
        """Тест успешного создания тега."""
        tag = Tag.objects.create(
            name="Завтрак",
            slug="breakfast",
        )
        assert tag.name == "Завтрак"
        assert tag.slug == "breakfast"

    def test_tag_str_method(self, tag):
        """Тест строкового представления тега."""
        assert str(tag) == tag.name

    def test_tag_slug_unique(self, tag):
        """Тест уникальности slug тега."""
        with pytest.raises(IntegrityError):
            Tag.objects.create(
                name="Другой завтрак",
                slug="breakfast",
            )

    def test_tag_name_unique(self, tag):
        """Тест уникальности названия тега."""
        with pytest.raises(IntegrityError):
            Tag.objects.create(
                name="Завтрак",
                slug="another-breakfast",
            )


@pytest.mark.django_db
class TestIngredientModel:
    def test_create_ingredient_success(self):
        """Тест успешного создания ингредиента."""
        ingredient = Ingredient.objects.create(
            name="Мука",
            measurement_unit="г"
        )
        assert ingredient.name == "Мука"
        assert ingredient.measurement_unit == "г"

    def test_ingredient_str_method(self, ingredient):
        """Тест строкового представления ингредиента."""
        assert str(ingredient) == ingredient.name

    def test_ingredient_name_measurement_unit_unique(self, ingredient):
        """Тест уникальности комбинации название + единица измерения."""
        with pytest.raises(IntegrityError):
            Ingredient.objects.create(
                name="Мука",
                measurement_unit="г"
            )


@pytest.mark.django_db
class TestRecipeModel:
    def test_create_recipe_success(self, user):
        """Тест успешного создания рецепта."""
        recipe = Recipe.objects.create(
            name="Тестовый рецепт",
            text="Описание тестового рецепта",
            cooking_time=30,
            author=user,
            image="test_image.jpg"
        )
        assert recipe.name == "Тестовый рецепт"
        assert recipe.text == "Описание тестового рецепта"
        assert recipe.cooking_time == 30
        assert recipe.author == user

    def test_recipe_str_method(self, recipe):
        """Тест строкового представления рецепта."""
        assert str(recipe) == recipe.name

    def test_recipe_cooking_time_positive(self, user):
        """Тест валидации положительного времени приготовления."""
        with pytest.raises(ValidationError):
            recipe = Recipe(
                name="Тестовый рецепт",
                text="Описание тестового рецепта",
                cooking_time=0,
                author=user,
                image="test_image.jpg"
            )
            recipe.full_clean()


@pytest.mark.django_db
class TestRecipeIngredientModel:
    def test_create_recipe_ingredient_success(self, recipe, ingredient):
        """Тест успешного создания связи рецепт-ингредиент."""
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=100
        )
        assert recipe_ingredient.recipe == recipe
        assert recipe_ingredient.ingredient == ingredient
        assert recipe_ingredient.amount == 100

    def test_recipe_ingredient_str_method(self, recipe, ingredient):
        """Тест строкового представления связи рецепт-ингредиент."""
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=100
        )
        expected_str = f"{recipe.name} - {ingredient.name}"
        assert str(recipe_ingredient) == expected_str

    def test_recipe_ingredient_unique_together(self, recipe, ingredient):
        """Тест уникальности комбинации рецепт + ингредиент."""
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=100
        )
        with pytest.raises(IntegrityError):
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=200
            )

    def test_recipe_ingredient_amount_positive(self, recipe, ingredient):
        """Тест валидации положительного количества ингредиента."""
        with pytest.raises(ValidationError):
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=0
            )
            recipe_ingredient.full_clean()


@pytest.mark.django_db
class TestFavoriteModel:
    def test_create_favorite_success(self, user, recipe):
        """Тест успешного добавления рецепта в избранное."""
        favorite = Favorite.objects.create(
            user=user,
            recipe=recipe
        )
        assert favorite.user == user
        assert favorite.recipe == recipe

    def test_favorite_str_method(self, user, recipe):
        """Тест строкового представления избранного."""
        favorite = Favorite.objects.create(
            user=user,
            recipe=recipe
        )
        expected_str = f"{user.username} - {recipe.name}"
        assert str(favorite) == expected_str

    def test_favorite_unique_together(self, user, recipe):
        """Тест уникальности комбинации пользователь + рецепт в избранном."""
        Favorite.objects.create(user=user, recipe=recipe)
        with pytest.raises(IntegrityError):
            Favorite.objects.create(user=user, recipe=recipe)


@pytest.mark.django_db
class TestShoppingCartModel:
    def test_create_shopping_cart_success(self, user, recipe):
        """Тест успешного добавления рецепта в список покупок."""
        shopping_cart = ShoppingCart.objects.create(
            user=user,
            recipe=recipe
        )
        assert shopping_cart.user == user
        assert shopping_cart.recipe == recipe

    def test_shopping_cart_str_method(self, user, recipe):
        """Тест строкового представления списка покупок."""
        shopping_cart = ShoppingCart.objects.create(
            user=user,
            recipe=recipe
        )
        expected_str = f"{user.username} - {recipe.name}"
        assert str(shopping_cart) == expected_str

    def test_shopping_cart_unique_together(self, user, recipe):
        """Тест уникальности комбинации пользователь + рецепт в списке покупок."""
        ShoppingCart.objects.create(user=user, recipe=recipe)
        with pytest.raises(IntegrityError):
            ShoppingCart.objects.create(user=user, recipe=recipe)


@pytest.mark.django_db
class TestFollowModel:
    def test_create_follow_success(self, user, another_user):
        """Тест успешного создания подписки."""
        follow = Follow.objects.create(
            user=user,
            author=another_user
        )
        assert follow.user == user
        assert follow.author == another_user

    def test_follow_str_method(self, user, another_user):
        """Тест строкового представления подписки."""
        follow = Follow.objects.create(
            user=user,
            author=another_user
        )
        expected_str = f"{user.username} подписан на {another_user.username}"
        assert str(follow) == expected_str

    def test_follow_unique_together(self, user, another_user):
        """Тест уникальности комбинации подписчик + автор."""
        Follow.objects.create(user=user, author=another_user)
        with pytest.raises(IntegrityError):
            Follow.objects.create(user=user, author=another_user)

    def test_follow_self_constraint(self, user):
        """Тест ограничения подписки на самого себя."""
        with pytest.raises(ValidationError):
            follow = Follow(user=user, author=user)
            follow.full_clean()
