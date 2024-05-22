from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import Profile, Subscription


class ProfileSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)

        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                following=obj
            ).exists()

        return False
