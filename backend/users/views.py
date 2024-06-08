from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, Profile
from api.pagination import FoodGramPagination
from api.serializers import AvatarSerializer, SubscriptionSerializer


class ProfileViewSet(UserViewSet):
    pagination_class = FoodGramPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(Profile, id=self.kwargs.get('id'))
        serializer = SubscriptionSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        Subscription.objects.create(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(Profile, id=id)
        subscription = Subscription.objects.filter(
            user=user,
            author=author
        ).delete()

        if subscription == (0, {}):
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = Profile.objects.filter(followers__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user
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
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
