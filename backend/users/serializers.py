from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Profile, Subscription


class ProfileSerializer(serializers.ModelSerializer):
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
        request = self.context.get('request')

        return (
                request and
                request.user.is_authenticated and
                Subscription.objects.filter(
                    user=request.user,
                    author=obj
                ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = Profile
        fields = ('avatar',)
