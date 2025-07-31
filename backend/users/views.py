"""
Views for users app.
"""
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from .models import User, Follow
from .serializers import CustomUserSerializer, SetAvatarSerializer, SubscriptionSerializer


class UserViewSet(DjoserUserViewSet):
    """ViewSet for User model with custom actions."""
    
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Set or delete user avatar."""
        user = request.user
        
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Get user subscriptions."""
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = SubscriptionSerializer(subscriptions, many=True, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Subscribe or unsubscribe to/from user."""
        user = request.user
        try:
            author = get_object_or_404(User, pk=id)
        except ValueError:
            return Response(
                {'errors': 'Неверный ID пользователя'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == 'POST':
            follow, created = Follow.objects.get_or_create(user=user, author=author)
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = SubscriptionSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            follow = Follow.objects.filter(user=user, author=author).first()
            if not follow:
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

