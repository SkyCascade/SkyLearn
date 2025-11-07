from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """
    Permission check for student users
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'student')
        )


class IsLecturer(permissions.BasePermission):
    """
    Permission check for lecturer users
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_lecturer
        )


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


class IsOwnerOrAdminOrLecturer(permissions.BasePermission):
    """
    Permission check: owner of the object, lecturer, or admin
    """
    def has_object_permission(self, request, view, obj):
        # Администраторы и преподаватели имеют полный доступ
        if request.user.is_staff or request.user.is_lecturer:
            return True
        
        # Студенты могут просматривать только свою посещаемость
        if hasattr(obj, 'Student') and hasattr(request.user, 'student'):
            return obj.Student == request.user.student
        
        return False
