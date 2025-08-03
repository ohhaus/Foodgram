import pytest


@pytest.fixture
def auth_client(client, user):
    """Фикстура для авторизованного клиента."""
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user(django_user_model):
    """Фикстура для создания тестового пользователя."""
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def tag(db):
    """Фикстура для создания тестового тега."""
    from recipes.models import Tag
    return Tag.objects.create(
        name='Тестовый тег',
        slug='test-tag'
    )


@pytest.fixture
def recipe(user, tag):
    """Фикстура для создания тестового рецепта."""
    from recipes.models import Recipe
    recipe = Recipe.objects.create(
        author=user,
        name='Тестовый рецепт',
        text='Описание тестового рецепта',
        cooking_time=30
    )
    recipe.tags.add(tag)
    return recipe
