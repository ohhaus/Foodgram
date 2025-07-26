from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, response, status
from rest_framework.decorators import action

from core.pagination import LimitPageNumberPagination
from users.models import Follow, User
from users.serializers import FollowSerializer, UserSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        get_object_or_404(Follow, user=user, author=author).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            FollowSerializer(
                self.paginate_queryset(
                    User.objects.filter(following__user=request.user)
                ),
                many=True,
                context={'request': request},
            ).data
        )
