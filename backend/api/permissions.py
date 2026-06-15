from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPremiumOrReadOnly(BasePermission):
    """Allow read-only for everyone; write requires premium or admin role."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in (
            "premium",
            "admin",
        )


class IsAdminOrEditor(BasePermission):
    """Allow access only to admin or editor roles."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("admin",)


class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission: only the owner can edit."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "user", None) == request.user
