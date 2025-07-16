from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для всех пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscibed')

        # TODO: Допилить данный участок кода
        def get_is_subscribed(self, author):
            """Проверка подписки пользователя."""
            request = self.context.get('request')
            return (request and request.user.is_authenticated
                    and request.user.follower.filter(author=author).exists())
        
