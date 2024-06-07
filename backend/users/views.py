from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, Profile
from .pagination import ProfilePagination
from .serializers import AvatarSerializer
from api.serializers import SubscriptionSerializer


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def profile_avatar(request):
    user = request.user

    if request.method == 'PUT':
        serializer = AvatarSerializer(data=request.data)

        if serializer.is_valid():
            user.avatar = serializer.validated_data['avatar']
            user.save()
            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response(
                {'avatar': avatar_url},
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.avatar = None
        user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ProfileViewSet(UserViewSet):
    pagination_class = ProfilePagination

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'GET':
            return self.retrieve(request, *args, **kwargs)
        else:
            return MethodNotAllowed(request.method)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(Profile, id=self.kwargs.get('id'))
        serializer = SubscriptionSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        if user == author:
            return Response({
                'errors': 'Нельзя подписаться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Subscription.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(Profile, id=id)
        subscription = Subscription.objects.filter(user=user, author=author)

        if user == author:
            return Response({
                'errors': 'Нельзя отписаться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)

        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            'errors': 'Вы не подписаны на этого пользователя'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = Profile.objects.filter(followers__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)
