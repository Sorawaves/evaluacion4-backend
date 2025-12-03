"""
Permission classes personalizados para control de acceso por roles.
Implementa el sistema de autorización requerido en la evaluación.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    """
    Permiso para super_admin únicamente.
    Usado para gestión de empresas y suscripciones.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role == 'SUPER_ADMIN'
        )


class IsAdminCliente(BasePermission):
    """
    Permiso para admin_cliente únicamente.
    Puede administrar todo en su empresa (tenant).
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role == 'ADMIN_CLIENTE'
        )


class IsGerente(BasePermission):
    """
    Permiso para gerente únicamente.
    Acceso a gestión de inventario, reportes y proveedores.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role == 'GERENTE'
        )


class IsVendedor(BasePermission):
    """
    Permiso para vendedor únicamente.
    Acceso limitado a ventas POS y visualización de productos.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role == 'VENDEDOR'
        )


class IsSuperAdminOrAdminCliente(BasePermission):
    """
    Permiso para super_admin o admin_cliente.
    Para operaciones administrativas.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role in ['SUPER_ADMIN', 'ADMIN_CLIENTE']
        )


class IsAdminClienteOrGerente(BasePermission):
    """
    Permiso para admin_cliente o gerente.
    Para gestión de productos, proveedores e inventario.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role in ['ADMIN_CLIENTE', 'GERENTE']
        )


class IsAdminClienteOrGerenteOrVendedor(BasePermission):
    """
    Permiso para admin_cliente, gerente o vendedor.
    Para visualización de productos y realización de ventas.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role in ['ADMIN_CLIENTE', 'GERENTE', 'VENDEDOR']
        )


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Permite lectura a cualquiera, escritura solo a autenticados.
    Para catálogo público de e-commerce.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_active


class CanManageCompanyData(BasePermission):
    """
    Verifica que el usuario solo pueda acceder a datos de su empresa.
    Para multi-tenancy.
    """
    def has_object_permission(self, request, view, obj):
        # Super admin puede ver todo
        if request.user.role == 'SUPER_ADMIN':
            return True
        
        # Los demás usuarios solo pueden ver datos de su empresa
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        
        return False


class CanCreateSale(BasePermission):
    """
    Permiso para crear ventas POS.
    Solo admin_cliente, gerente y vendedor pueden crear ventas.
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role in ['ADMIN_CLIENTE', 'GERENTE', 'VENDEDOR']
        )


class CanViewReports(BasePermission):
    """
    Permiso para ver reportes.
    Solo admin_cliente y gerente pueden ver reportes.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role in ['ADMIN_CLIENTE', 'GERENTE']
        )


class CanManageSubscription(BasePermission):
    """
    Permiso para gestionar suscripciones.
    Solo super_admin puede gestionar suscripciones.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            # Admin cliente puede ver su propia suscripción
            return (
                request.user and
                request.user.is_authenticated and
                request.user.is_active and
                request.user.role in ['SUPER_ADMIN', 'ADMIN_CLIENTE']
            )
        
        # Solo super_admin puede modificar suscripciones
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role == 'SUPER_ADMIN'
        )
