from rest_framework import exceptions, serializers, status

from core.serializers import ShowRecipeAddedSerializer
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для всех пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.follower.filter(author=author).exists()
        )


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'last_name',
            'first_name',
        )

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, author=author).exists():
            raise exceptions.ValidationError(
                detail='',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise exceptions.ValidationError(
                detail='', code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = ShowRecipeAddedSerializer(
            recipes,
            many=True,
            read_only=True,
        )

        return serializer.data
