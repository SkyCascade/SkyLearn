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


class IsOwnerAdmin(permissions.BasePermission):
    """
    Проверяет, что объект принадлежит админу текущего пользователя
    """
    def has_object_permission(self, request, view, obj):
        # Проверяем, что пользователь аутентифицирован
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Суперпользователи могут видеть только свои объекты
        if request.user.is_superuser:
            # Проверяем, что объект принадлежит этому админу
            if hasattr(obj, 'admin'):
                return obj.admin == request.user
            return False
        
        # Преподаватели и студенты могут видеть объекты своего админа
        if hasattr(request.user, 'admin') and request.user.admin:
            if hasattr(obj, 'admin'):
                return obj.admin == request.user.admin
            return False
        
        return False


class CanModifyOwnData(permissions.BasePermission):
    """
    Проверяет, что пользователь может изменять только свои данные
    (только администраторы могут изменять данные своих объектов)
    """
    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Изменение разрешено только администраторам
        if not request.user.is_superuser:
            return False
        
        # Проверяем, что объект принадлежит этому админу
        if hasattr(obj, 'admin'):
            return obj.admin == request.user
        
        return False