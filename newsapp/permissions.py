from rest_framework import permissions

class IsAdminOrEditorOrOwnerWriter(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ["ADMIN", "EDITOR", "WRITER"]
    
    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser or getattr(request.user, 'role', None) in ["ADMIN", "EDITOR"]:
            return True
        
        return getattr(obj, 'writer_id', None) == request.user.id
