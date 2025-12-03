"""
Modelos para el sistema POS + E-commerce de TemucoSoft S.A.
Cumple con normalización 3NF y requisitos de evaluación.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from .validators import (
    validar_rut_chileno,
    validar_fecha_no_futura,
    validar_precio_positivo,
    validar_stock_no_negativo,
    validar_cantidad_positiva,
    validar_texto_no_vacio
)


class Company(models.Model):
    """
    Modelo para empresas/clientes (tenants) del sistema.
    Cada empresa cliente tiene su propia cuenta.
    """
    name = models.CharField(max_length=200, validators=[validar_texto_no_vacio])
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut_chileno])
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rut})"


class Subscription(models.Model):
    """
    Modelo para suscripciones/planes de las empresas.
    Controla el acceso a funcionalidades según el plan contratado.
    """
    PLAN_CHOICES = [
        ('BASICO', 'Básico'),
        ('ESTANDAR', 'Estándar'),
        ('PREMIUM', 'Premium'),
    ]
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='subscription')
    plan_name = models.CharField(max_length=10, choices=PLAN_CHOICES, default='BASICO')
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    max_branches = models.IntegerField(default=1)  # Límite según plan
    max_users = models.IntegerField(default=3)
    has_api_access = models.BooleanField(default=False)
    has_reports = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
    
    def __str__(self):
        return f"{self.company.name} - Plan {self.get_plan_name_display()}"
    
    def is_valid(self):
        """Verifica si la suscripción está activa y vigente"""
        today = timezone.now().date()
        return self.active and self.start_date <= today <= self.end_date
    
    def clean(self):
        """Validación personalizada"""
        from django.core.exceptions import ValidationError
        if self.end_date <= self.start_date:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio')


class User(AbstractUser):
    """
    Usuario custom con roles para el sistema.
    Extiende AbstractUser de Django para incluir campos personalizados.
    """
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN_CLIENTE', 'Admin Cliente'),
        ('GERENTE', 'Gerente'),
        ('VENDEDOR', 'Vendedor'),
        ('CLIENTE_FINAL', 'Cliente Final'),
    ]
    
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='VENDEDOR')
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut_chileno])
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        help_text='Empresa a la que pertenece (null para super_admin)'
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_super_admin(self):
        return self.role == 'SUPER_ADMIN'
    
    def is_admin_cliente(self):
        return self.role == 'ADMIN_CLIENTE'
    
    def is_gerente(self):
        return self.role == 'GERENTE'
    
    def is_vendedor(self):
        return self.role == 'VENDEDOR'


class Branch(models.Model):
    """
    Modelo para sucursales de las empresas.
    Cada empresa puede tener múltiples sucursales según su plan.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=200, validators=[validar_texto_no_vacio])
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        unique_together = ['company', 'name']
        ordering = ['company', 'name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Supplier(models.Model):
    """
    Modelo para proveedores.
    Los proveedores surten productos a las empresas.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=200, validators=[validar_texto_no_vacio])
    rut = models.CharField(max_length=12, validators=[validar_rut_chileno])
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        unique_together = ['company', 'rut']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rut})"


class Product(models.Model):
    """
    Modelo para productos.
    Productos que se venden en el sistema POS y e-commerce.
    """
    CATEGORY_CHOICES = [
        ('ELECTRONICOS', 'Electrónicos'),
        ('ROPA', 'Ropa'),
        ('ALIMENTOS', 'Alimentos'),
        ('HOGAR', 'Hogar'),
        ('SALUD', 'Salud y Belleza'),
        ('DEPORTES', 'Deportes'),
        ('LIBROS', 'Libros'),
        ('JUGUETES', 'Juguetes'),
        ('OTROS', 'Otros'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200, validators=[validar_texto_no_vacio])
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTROS')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), validar_precio_positivo]
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), validar_precio_positivo]
    )
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    def get_margin(self):
        """Calcula el margen de ganancia"""
        if self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return 0


class Inventory(models.Model):
    """
    Modelo para inventario por sucursal.
    Relación entre productos y sucursales con control de stock.
    """
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), validar_stock_no_negativo]
    )
    reorder_point = models.IntegerField(
        default=10,
        help_text='Punto de reorden: cuando el stock llega a este nivel, reordenar'
    )
    last_restock_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = ['branch', 'product']
        ordering = ['branch', 'product']
    
    def __str__(self):
        return f"{self.branch.name} - {self.product.name}: {self.stock} unidades"
    
    def needs_restock(self):
        """Verifica si necesita reabastecimiento"""
        return self.stock <= self.reorder_point
    
    def add_stock(self, quantity):
        """Agrega stock"""
        self.stock += quantity
        self.last_restock_date = timezone.now()
        self.save()
    
    def remove_stock(self, quantity):
        """Quita stock"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False


class Purchase(models.Model):
    """
    Modelo para compras a proveedores.
    Registra entradas de stock desde proveedores.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='purchases')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchases')
    purchase_date = models.DateTimeField(default=timezone.now, validators=[validar_fecha_no_futura])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"Compra #{self.id} - {self.supplier.name} - {self.purchase_date.strftime('%d/%m/%Y')}"
    
    def calculate_total(self):
        """Calcula el total de la compra"""
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class PurchaseItem(models.Model):
    """
    Modelo para items de una compra.
    Detalle de productos en cada compra.
    """
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1), validar_cantidad_positiva])
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[validar_precio_positivo])
    
    class Meta:
        verbose_name = 'Item de Compra'
        verbose_name_plural = 'Items de Compra'
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def get_subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.unit_cost


class Sale(models.Model):
    """
    Modelo para ventas POS (punto de venta presencial).
    Registra ventas realizadas en sucursales.
    """
    PAYMENT_METHOD_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='sales')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, validators=[validar_fecha_no_futura])
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Venta POS'
        verbose_name_plural = 'Ventas POS'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Venta #{self.id} - {self.branch.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def calculate_total(self):
        """Calcula el total de la venta"""
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class SaleItem(models.Model):
    """
    Modelo para items de una venta.
    Detalle de productos en cada venta POS.
    """
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1), validar_cantidad_positiva])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validar_precio_positivo])
    
    class Meta:
        verbose_name = 'Item de Venta'
        verbose_name_plural = 'Items de Venta'
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def get_subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.unit_price


class Order(models.Model):
    """
    Modelo para órdenes de e-commerce.
    Compras online realizadas por clientes finales.
    """
    STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # Datos del cliente (para compras sin registro)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.CharField(max_length=300)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDIENTE')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Orden E-commerce'
        verbose_name_plural = 'Órdenes E-commerce'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Orden #{self.id} - {self.customer_name} - {self.get_status_display()}"
    
    def calculate_total(self):
        """Calcula el total de la orden"""
        subtotal = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = subtotal + self.shipping_cost
        self.save()
        return self.total_amount


class OrderItem(models.Model):
    """
    Modelo para items de una orden.
    Detalle de productos en cada orden de e-commerce.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1), validar_cantidad_positiva])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validar_precio_positivo])
    
    class Meta:
        verbose_name = 'Item de Orden'
        verbose_name_plural = 'Items de Orden'
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def get_subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.unit_price


class CartItem(models.Model):
    """
    Modelo para items del carrito de compras.
    Carrito temporal antes de convertirse en orden.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, help_text='Para usuarios no autenticados')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1), validar_cantidad_positiva])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
    
    def __str__(self):
        owner = self.user.username if self.user else f"Session: {self.session_key}"
        return f"{owner} - {self.product.name} x{self.quantity}"
    
    def get_subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.product.price


class Payment(models.Model):
    """
    Modelo para pagos (simplificado).
    Registra pagos de ventas POS y órdenes e-commerce.
    """
    PAYMENT_STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido'),
        ('REEMBOLSADO', 'Reembolsado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('WEBPAY', 'WebPay'),
    ]
    
    # Puede estar relacionado a una venta POS o una orden e-commerce
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), validar_precio_positivo]
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='PENDIENTE')
    
    # Información de transacción
    transaction_id = models.CharField(max_length=100, blank=True, help_text='ID de transacción externo')
    reference = models.CharField(max_length=200, blank=True, help_text='Referencia del pago')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.sale:
            return f"Pago #{self.id} - Venta #{self.sale.id} - ${self.amount}"
        elif self.order:
            return f"Pago #{self.id} - Orden #{self.order.id} - ${self.amount}"
        return f"Pago #{self.id} - ${self.amount}"
    
    def is_completed(self):
        """Verifica si el pago está completado"""
        return self.status == 'COMPLETADO'
