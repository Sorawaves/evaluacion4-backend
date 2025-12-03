"""
Serializers para el sistema POS + E-commerce de TemucoSoft S.A.
Incluye validaciones integradas y serializers anidados para respuestas completas.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Company, Subscription, Branch, Supplier, Product, Inventory,
    Purchase, PurchaseItem, Sale, SaleItem, Order, OrderItem, CartItem, Payment
)
from .validators import (
    validar_rut_chileno,
    validar_fecha_no_futura,
    validar_precio_positivo,
    validar_cantidad_positiva
)

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """Serializer para empresas/clientes (tenants)"""
    subscription_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'rut', 'address', 'phone', 'email',
            'is_active', 'subscription_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subscription_status(self, obj):
        try:
            return obj.subscription.is_valid()
        except:
            return False
    
    def validate_rut(self, value):
        validar_rut_chileno(value)
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para suscripciones"""
    plan_name_display = serializers.CharField(source='get_plan_name_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'company', 'company_name', 'plan_name', 'plan_name_display',
            'start_date', 'end_date', 'active', 'max_branches', 'max_users',
            'has_api_access', 'has_reports', 'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    {'end_date': 'La fecha de fin debe ser posterior a la fecha de inicio'}
                )
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuarios del sistema"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'rut', 'company', 'company_name',
            'phone', 'is_active', 'password', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    def validate_rut(self, value):
        validar_rut_chileno(value)
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios (incluye password requerido)"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'rut', 'company', 'phone', 'password', 'password_confirm'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden'})
        return data
    
    def validate_rut(self, value):
        validar_rut_chileno(value)
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class BranchSerializer(serializers.ModelSerializer):
    """Serializer para sucursales"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'id', 'company', 'company_name', 'name', 'address',
            'phone', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer para proveedores"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'company', 'company_name', 'name', 'rut',
            'contact_name', 'contact_email', 'contact_phone', 'address',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_rut(self, value):
        validar_rut_chileno(value)
        return value


class ProductSerializer(serializers.ModelSerializer):
    """Serializer para productos"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    margin = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'company', 'company_name', 'sku', 'name', 'description',
            'category', 'category_display', 'price', 'cost', 'margin',
            'is_active', 'image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_margin(self, obj):
        return obj.get_margin()
    
    def validate_price(self, value):
        validar_precio_positivo(value)
        return value
    
    def validate_cost(self, value):
        validar_precio_positivo(value)
        return value


class InventorySerializer(serializers.ModelSerializer):
    """Serializer para inventario"""
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    needs_restock = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'branch', 'branch_name', 'product', 'product_name', 'product_sku',
            'stock', 'reorder_point', 'needs_restock', 'last_restock_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_restock_date']
    
    def get_needs_restock(self, obj):
        return obj.needs_restock()


class PurchaseItemSerializer(serializers.ModelSerializer):
    """Serializer para items de compra"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_cost', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    
    def validate_quantity(self, value):
        validar_cantidad_positiva(value)
        return value
    
    def validate_unit_cost(self, value):
        validar_precio_positivo(value)
        return value


class PurchaseSerializer(serializers.ModelSerializer):
    """Serializer para compras a proveedores"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    items = PurchaseItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'company', 'supplier', 'supplier_name', 'branch', 'branch_name',
            'user', 'user_name', 'purchase_date', 'total_amount', 'notes',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_amount']
    
    def validate_purchase_date(self, value):
        validar_fecha_no_futura(value)
        return value


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer para items de venta"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    
    def validate_quantity(self, value):
        validar_cantidad_positiva(value)
        return value
    
    def validate_unit_price(self, value):
        validar_precio_positivo(value)
        return value


class SaleSerializer(serializers.ModelSerializer):
    """Serializer para ventas POS"""
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    items = SaleItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'branch', 'branch_name', 'user', 'user_name',
            'payment_method', 'payment_method_display', 'total_amount',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_amount']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer para items de orden"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    
    def validate_quantity(self, value):
        validar_cantidad_positiva(value)
        return value
    
    def validate_unit_price(self, value):
        validar_precio_positivo(value)
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Serializer para órdenes de e-commerce"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'company', 'company_name', 'user', 'user_name',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'status', 'status_display', 'total_amount', 'shipping_cost',
            'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_amount']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para items del carrito"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.URLField(source='product.image_url', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_price', 'product_image',
            'quantity', 'subtotal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    
    def validate_quantity(self, value):
        validar_cantidad_positiva(value)
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos"""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sale_info = serializers.SerializerMethodField()
    order_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'sale', 'order', 'sale_info', 'order_info',
            'amount', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'transaction_id', 'reference',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_sale_info(self, obj):
        if obj.sale:
            return f"Venta #{obj.sale.id}"
        return None
    
    def get_order_info(self, obj):
        if obj.order:
            return f"Orden #{obj.order.id}"
        return None
    
    def validate_amount(self, value):
        validar_precio_positivo(value)
        return value
