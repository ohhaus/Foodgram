from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action

from users.models import User
from core.pagination import LimitPageNumberPagination


# TODO: Написать views для пользователей и для подписчиков
class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination
    serializer_class = None     # Написать сериализатор!!

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        # permission_classes=[]
    )
    
