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
                author=obj
            ).exists()

        return False


class SubscriptionSerializer(ProfileSerializer):
    # recipes = serializers.SerializerMethodField()
    # recipes_count = serializers.SerializerMethodField()

    class Meta(ProfileSerializer.Meta):
        fields = ProfileSerializer.Meta.fields  # + ('recipes',
        # 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    # def get_recipes(self, obj):
    #     request = self.context.get('request')
    #     limit = request.GET.get('recipes_limit')
    #     queryset = Recipe.objects.filter(author=obj.author)
    #     if limit:
    #         queryset = queryset[:int(limit)]
    #     return CropRecipeSerializer(queryset, many=True).data
    #
    # def get_recipes_count(self, obj):
    #     return Recipe.objects.filter(author=obj.author).count()
