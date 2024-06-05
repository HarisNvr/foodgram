from django.contrib import admin
from django.urls import include, path

from api.views import redirect_to_recipe

urlpatterns = [
    path(
        's/<str:recipe_hash>/',
        redirect_to_recipe,
        name='short-link-redirect'
    ),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('users.urls')),
]
