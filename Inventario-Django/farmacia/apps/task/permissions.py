
from rest_framework.permissions import BasePermission
"""Permisos personalizados para restringir acceso basado en roles de usuario."""

class IsAdmin(BasePermission):
    """Permite acceso solo a usuarios con rol 'administrador'."""
    message = 'Acceso denegado: Requiere rol de administrador.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol and request.user.rol.name == 'administrador')

class IsEmployee(BasePermission):
    """Permite acceso solo a usuarios con rol 'empleado'."""
    message = 'Acceso denegado: Requiere rol de empleado.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol and request.user.rol.name == 'empleado')

class IsClient(BasePermission):
    """Permite acceso solo a usuarios con rol 'cliente'."""
    message = 'Acceso denegado: Requiere rol de cliente.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol and request.user.rol.name == 'cliente')

class IsProvider(BasePermission):
    """Permite acceso solo a usuarios con rol 'proveedor'."""
    message = 'Acceso denegado: Requiere rol de proveedor.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol and request.user.rol.name == 'proveedor')