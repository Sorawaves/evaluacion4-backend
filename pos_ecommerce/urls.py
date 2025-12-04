"""
URLs del sistema POS + E-commerce de TemucoSoft S.A.
Incluye todos los endpoints API y rutas de templates.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    # ViewSets API
    CompanyViewSet, SubscriptionViewSet, UserViewSet, BranchViewSet,
    SupplierViewSet, ProductViewSet, InventoryViewSet, PurchaseViewSet,
    SaleViewSet, OrderViewSet, CartItemViewSet, PaymentViewSet, InventoryMovementViewSet,
    # Reportes API
    stock_report, sales_report, supplier_report,
    # Vistas de Templates
    home, login_view, logout_view, dashboard, product_catalog, product_detail,
    cart_view, add_to_cart, checkout_view, process_order, inventory_view, suppliers_view,
    sales_view, reports_view, pos_view, branches_view, users_create_view,
    subscription_view, purchase_create_view, cart_clear_view, cart_remove_item_view,
    # Vistas SUPER_ADMIN
    superadmin_companies, superadmin_create_company, superadmin_edit_company,
    superadmin_company_users, superadmin_create_user, superadmin_edit_user, reset_password
)

# Router para endpoints API REST
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'users', UserViewSet, basename='user')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'inventory-movements', InventoryMovementViewSet, basename='inventory-movement')

urlpatterns = [
    # ========== API Endpoints ==========
    # Autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints CRUD (todos los ViewSets)
    path('api/', include(router.urls)),
    
    # Reportes API
    path('api/reportes/stock/', stock_report, name='report_stock'),
    path('api/reportes/ventas/', sales_report, name='report_sales'),
    path('api/reportes/proveedores/', supplier_report, name='report_suppliers'),
    
    # ========== Vistas de Templates (Frontend) ==========
    # Páginas públicas
    path('', home, name='home'),
    path('iniciar-sesion/', login_view, name='login'),
    path('cerrar-sesion/', logout_view, name='logout'),
    
    # Dashboard (requiere autenticación)
    path('panel/', dashboard, name='dashboard'),
    
    # E-commerce (catálogo público)
    path('tienda/', product_catalog, name='product_catalog'),
    path('tienda/producto/<int:pk>/', product_detail, name='product_detail'),
    path('carrito/', cart_view, name='cart'),
    path('carrito/agregar/', add_to_cart, name='cart_add'),
    path('carrito/vaciar/', cart_clear_view, name='cart_clear'),
    path('carrito/eliminar/<int:item_id>/', cart_remove_item_view, name='cart_remove_item'),
    path('pagar/', checkout_view, name='checkout'),
    path('pagar/procesar/', process_order, name='process_order'),
    
    # Gestión interna (requiere autenticación)
    path('inventario/', inventory_view, name='inventory'),
    path('proveedores/', suppliers_view, name='suppliers'),
    path('ventas/', sales_view, name='sales'),
    path('reportes/', reports_view, name='reports'),
    
    # Vistas específicas por rol
    path('pos/', pos_view, name='pos'),  # Vendedor
    path('sucursales/', branches_view, name='branches'),  # Admin Cliente
    path('usuarios/crear/', users_create_view, name='users_create'),  # Admin Cliente
    path('suscripcion/', subscription_view, name='subscription'),  # Admin Cliente
    path('compras/crear/', purchase_create_view, name='purchase_create'),  # Admin Cliente / Gerente
    
    # SUPER_ADMIN - Gestión de plataforma
    path('superadmin/empresas/', superadmin_companies, name='superadmin_companies'),
    path('superadmin/empresas/crear/', superadmin_create_company, name='superadmin_create_company'),
    path('superadmin/empresas/<int:company_id>/editar/', superadmin_edit_company, name='superadmin_edit_company'),
    path('superadmin/empresas/<int:company_id>/usuarios/', superadmin_company_users, name='superadmin_company_users'),
    path('superadmin/empresas/<int:company_id>/usuarios/crear/', superadmin_create_user, name='superadmin_create_user'),
    path('superadmin/usuarios/<int:user_id>/editar/', superadmin_edit_user, name='superadmin_edit_user'),
    path('superadmin/usuarios/<str:username>/resetear-clave/', reset_password, name='reset_password'),
]
