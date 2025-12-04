"""
Administración de Django para el sistema POS + E-commerce.
Configura todos los modelos en el panel administrativo.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Company, Subscription, User, Branch, Supplier, Product, Inventory, InventoryMovement,
    Purchase, PurchaseItem, Sale, SaleItem, Order, OrderItem, CartItem, Payment
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Administración de empresas/clientes"""
    list_display = ['name', 'rut', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'rut', 'email']
    ordering = ['name']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Administración de suscripciones"""
    list_display = ['company', 'plan_name', 'start_date', 'end_date', 'active']
    list_filter = ['plan_name', 'active', 'start_date']
    search_fields = ['company__name']
    ordering = ['-start_date']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administración de usuarios personalizados"""
    list_display = ['username', 'email', 'role', 'company', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'company']
    search_fields = ['username', 'email', 'rut', 'first_name', 'last_name']
    ordering = ['username']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('role', 'company', 'rut', 'phone')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('role', 'company', 'rut', 'phone', 'email')
        }),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """Administración de sucursales"""
    list_display = ['name', 'company', 'address', 'phone', 'is_active']
    list_filter = ['company', 'is_active', 'created_at']
    search_fields = ['name', 'address', 'company__name']
    ordering = ['company', 'name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Administración de proveedores"""
    list_display = ['name', 'rut', 'company', 'contact_name', 'is_active']
    list_filter = ['company', 'is_active', 'created_at']
    search_fields = ['name', 'rut', 'contact_name']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administración de productos"""
    list_display = ['sku', 'name', 'company', 'category', 'price', 'cost', 'is_active']
    list_filter = ['company', 'category', 'is_active', 'created_at']
    search_fields = ['sku', 'name', 'description']
    ordering = ['name']
    
    def get_profit_margin(self, obj):
        """Mostrar margen de ganancia"""
        if obj.cost > 0:
            return f"{((obj.price - obj.cost) / obj.cost * 100):.2f}%"
        return "N/A"
    get_profit_margin.short_description = 'Margen'


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Administración de inventario"""
    list_display = ['product', 'branch', 'stock', 'reorder_point', 'needs_restock_display', 'last_restock_date']
    list_filter = ['branch', 'branch__company', 'updated_at']
    search_fields = ['product__name', 'product__sku', 'branch__name']
    ordering = ['stock']
    
    def needs_restock_display(self, obj):
        """Indicador visual de restock necesario"""
        return "⚠️ Sí" if obj.needs_restock() else "✅ No"
    needs_restock_display.short_description = 'Requiere restock'


class PurchaseItemInline(admin.TabularInline):
    """Inline para items de compra"""
    model = PurchaseItem
    extra = 1
    fields = ['product', 'quantity', 'unit_cost']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Administración de compras"""
    list_display = ['id', 'company', 'supplier', 'branch', 'purchase_date', 'total_amount']
    list_filter = ['company', 'supplier', 'branch', 'purchase_date']
    search_fields = ['supplier__name', 'notes']
    ordering = ['-purchase_date']
    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    """Administración de items de compra"""
    list_display = ['purchase', 'product', 'quantity', 'unit_cost', 'get_subtotal']
    list_filter = ['purchase__supplier', 'product']
    search_fields = ['product__name', 'purchase__id']
    ordering = ['-purchase__purchase_date']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


class SaleItemInline(admin.TabularInline):
    """Inline para items de venta"""
    model = SaleItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Administración de ventas POS"""
    list_display = ['id', 'branch', 'user', 'payment_method', 'total_amount', 'created_at']
    list_filter = ['branch', 'payment_method', 'created_at', 'branch__company']
    search_fields = ['user__username', 'notes']
    ordering = ['-created_at']
    inlines = [SaleItemInline]
    readonly_fields = ['created_at']


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    """Administración de items de venta"""
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'get_subtotal']
    list_filter = ['sale__branch', 'product']
    search_fields = ['product__name', 'sale__id']
    ordering = ['-sale__created_at']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


class OrderItemInline(admin.TabularInline):
    """Inline para items de orden"""
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Administración de órdenes de e-commerce"""
    list_display = ['id', 'company', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'company', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'customer_phone']
    ordering = ['-created_at']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Administración de items de orden"""
    list_display = ['order', 'product', 'quantity', 'unit_price', 'get_subtotal']
    list_filter = ['order__status', 'product']
    search_fields = ['product__name', 'order__customer_name']
    ordering = ['-order__created_at']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Administración de items del carrito"""
    list_display = ['user', 'session_key', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name', 'session_key']
    ordering = ['-created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Administración de pagos"""
    list_display = ['id', 'get_related', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'reference']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def get_related(self, obj):
        if obj.sale:
            return f"Venta #{obj.sale.id}"
        elif obj.order:
            return f"Orden #{obj.order.id}"
        return "N/A"
    get_related.short_description = 'Relacionado a'


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    """Administración de movimientos de inventario"""
    list_display = ['id', 'get_product', 'get_branch', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'user', 'created_at']
    list_filter = ['movement_type', 'inventory__branch', 'inventory__branch__company', 'created_at']
    search_fields = ['inventory__product__name', 'inventory__product__sku', 'notes', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['previous_stock', 'new_stock', 'created_at']
    
    def get_product(self, obj):
        return obj.inventory.product.name
    get_product.short_description = 'Producto'
    
    def get_branch(self, obj):
        return obj.inventory.branch.name
    get_branch.short_description = 'Sucursal'
