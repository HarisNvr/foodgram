from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet

app_name = 'users'

router = DefaultRouter()

router.register('users', ProfileViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
