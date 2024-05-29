from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet, profile_avatar

app_name = 'users'

router = DefaultRouter()

router.register('users', ProfileViewSet)

urlpatterns = [
    path('users/me/avatar/', profile_avatar, name='add_avatar_to_profile'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
