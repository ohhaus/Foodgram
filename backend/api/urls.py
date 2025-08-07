from rest_framework.routers import DefaultRouter

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserViewSet

api_router = DefaultRouter()

api_router.register('tags', TagViewSet, basename='tags')
api_router.register('ingredients', IngredientViewSet, basename='ingredients')
api_router.register('recipes', RecipeViewSet, basename='recipes')
api_router.register('users', UserViewSet, basename='users')

urlpatterns = api_router.urls
