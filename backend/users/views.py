from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, response, status
from rest_framework.decorators import action

from core.pagination import LimitPageNumberPagination
from core.permissions import AuthorOrReadOnly
from users.models import Follow, User
from users.serializers import (
    FollowSerializer,
    UserAvatarSerializer,
    UserSerializer,
)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination
    serializer_class = UserSerializer
    permission_classes = (AuthorOrReadOnly,)

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
            follow, created = Follow.objects.get_or_create(
                user=user, author=author
            )
            if not created:
                return response.Response(
                    {'detail': settings.FOLLOW_ALREADY_EXISTS_ERROR},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = FollowSerializer(author, context={'request': request})
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            queryset, many=True, context={'request': request}
        )
        return response.Response(serializer.data)

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'POST':
            serializer = UserAvatarSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_200_OK
            )
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
