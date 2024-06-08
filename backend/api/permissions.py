from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            or request.user.is_superuser

        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and obj.author == request.user
            or request.user.is_superuser
        )
