from rest_framework import permissions

class IsLecturer(permissions.BasePermission):
    """
    Custom permission to only allow lecturers to access the view.
    """
    message = "Only lecturers are allowed to perform this action."

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is a lecturer
        return getattr(request.user, 'lecturer', False)

    def has_object_permission(self, request, view, obj):
        # For object-level permissions, also check if user is lecturer
        return self.has_permission(request, view)