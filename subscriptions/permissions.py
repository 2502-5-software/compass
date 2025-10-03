from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Allow only users whose role == "ADMIN" or superusers.
    """
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        # allow Django superusers too
        if getattr(user, "is_superuser", False):
            return True
        # role stored as string
        return getattr(user, "role", None) == "ADMIN"

class IsAdminOrEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["ADMIN", "EDITOR"]
