import base64

from django.core.files.base import ContentFile
from django.db import transaction
from django.urls import reverse
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    ShortLink,
    Tag,
)
from .utils import generate_unique_short_code


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='recipe.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели RecipeIngredient."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиентов в рецепте."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для короткой ссылки."""

    short_link = serializers.SerializerMethodField()

    class Meta:
        model = ShortLink
        fields = ('short_link',)

    def get_short_link(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse('short-link-redirect', args=[obj.short_code])
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {'short-link': data['short_link']}


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов и детального просмотра."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        """Проверяем наличие изображения только при создании рецепта."""
        if self.instance is None and 'image' not in data:
            raise serializers.ValidationError(
                {'image': 'Изображение обязательно при создании рецепта'}
            )
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один ингредиент.'
            )
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if len(existing_ingredients) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Один или несколько ингредиентов не существуют.'
            )
        for item in value:
            if item.get('amount', 0) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один тег.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0.'
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self._create_recipe_ingredients(recipe, ingredients_data)
        ShortLink.objects.get_or_create(
            recipe=recipe,
            defaults={'short_code': generate_unique_short_code()},
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        if 'image' not in validated_data:
            validated_data['image'] = instance.image
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._create_recipe_ingredients(instance, ingredients_data)
        return instance

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount'],
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
