from rest_framework import permissions

class IsLecturer(permissions.BasePermission):
    """
    Permission check for lecturer users
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_lecturer)

class IsAdminOrLecturer(permissions.BasePermission):
    """
    Permission check for admin or lecturer users
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.is_lecturer)
        )