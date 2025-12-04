"""
Views y ViewSets para el sistema POS + E-commerce de TemucoSoft S.A.
Implementa todos los endpoints API REST y vistas de templates requeridos.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import (
    Company, Subscription, User, Branch, Supplier, Product, Inventory, InventoryMovement,
    Purchase, PurchaseItem, Sale, SaleItem, Order, OrderItem, CartItem, Payment
)
from .serializers import (
    CompanySerializer, SubscriptionSerializer, UserSerializer, UserCreateSerializer,
    BranchSerializer, SupplierSerializer, ProductSerializer, InventorySerializer,
    PurchaseSerializer, PurchaseItemSerializer, SaleSerializer, SaleItemSerializer,
    OrderSerializer, OrderItemSerializer, CartItemSerializer, PaymentSerializer,
    InventoryMovementSerializer
)
from .permissions import (
    IsSuperAdmin, IsAdminCliente, IsGerente, IsVendedor,
    IsSuperAdminOrAdminCliente, IsAdminClienteOrGerente,
    IsAdminClienteOrGerenteOrVendedor, IsAuthenticatedOrReadOnly,
    CanCreateSale, CanViewReports, CanManageSubscription
)


# ============================================================================
# API ViewSets
# ============================================================================

class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para empresas/clientes (tenants).
    Solo super_admin puede crear y modificar empresas.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'rut', 'email']
    ordering_fields = ['name', 'created_at']


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para suscripciones.
    Super_admin gestiona, admin_cliente solo puede ver la suya.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [CanManageSubscription]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'plan_name', 'active']
    ordering_fields = ['start_date', 'end_date']
    
    def get_queryset(self):
        if self.request.user.role == 'SUPER_ADMIN':
            return Subscription.objects.all()
        elif self.request.user.company:
            return Subscription.objects.filter(company=self.request.user.company)
        return Subscription.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def activate(self, request, pk=None):
        """Activar una suscripción"""
        subscription = self.get_object()
        subscription.active = True
        subscription.save()
        return Response({'status': 'Suscripción activada'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperAdmin])
    def deactivate(self, request, pk=None):
        """Desactivar una suscripción"""
        subscription = self.get_object()
        subscription.active = False
        subscription.save()
        return Response({'status': 'Suscripción desactivada'})


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para usuarios del sistema.
    Super_admin y admin_cliente pueden crear usuarios.
    """
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'company', 'is_active']
    search_fields = ['username', 'email', 'rut', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSuperAdminOrAdminCliente]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.role == 'SUPER_ADMIN':
            return User.objects.all()
        elif self.request.user.company:
            return User.objects.filter(company=self.request.user.company)
        return User.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtener información del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class BranchViewSet(viewsets.ModelViewSet):
    """
    ViewSet para sucursales.
    Admin_cliente y gerente pueden gestionar sucursales.
    """
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminClienteOrGerente]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'is_active']
    search_fields = ['name', 'address']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        if self.request.user.role == 'SUPER_ADMIN':
            return Branch.objects.all()
        elif self.request.user.company:
            return Branch.objects.filter(company=self.request.user.company)
        return Branch.objects.none()
    
    @action(detail=True, methods=['get'], permission_classes=[IsAdminClienteOrGerente])
    def inventory(self, request, pk=None):
        """Obtener inventario de una sucursal"""
        branch = self.get_object()
        inventory = Inventory.objects.filter(branch=branch)
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet para proveedores.
    Admin_cliente y gerente pueden gestionar proveedores.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminClienteOrGerente]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'is_active']
    search_fields = ['name', 'rut', 'contact_name']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        if self.request.user.role == 'SUPER_ADMIN':
            return Supplier.objects.all()
        elif self.request.user.company:
            return Supplier.objects.filter(company=self.request.user.company)
        return Supplier.objects.none()


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para productos.
    Lectura pública para e-commerce, escritura para admin_cliente y gerente.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'category', 'is_active']
    search_fields = ['sku', 'name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    
    def get_queryset(self):
        # Para e-commerce, mostrar solo productos activos
        if self.action == 'list' and not self.request.user.is_authenticated:
            return Product.objects.filter(is_active=True)
        
        if self.request.user.is_authenticated:
            if self.request.user.role == 'SUPER_ADMIN':
                return Product.objects.all()
            elif self.request.user.company:
                return Product.objects.filter(company=self.request.user.company)
        
        return Product.objects.filter(is_active=True)


class InventoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para inventario.
    Admin_cliente y gerente pueden gestionar inventario.
    """
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminClienteOrGerente]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['branch', 'product']
    search_fields = ['product__name', 'product__sku']
    ordering_fields = ['stock', 'updated_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return Inventory.objects.all()
        elif user.company:
            return Inventory.objects.filter(branch__company=user.company)
        return Inventory.objects.none()
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminClienteOrGerente])
    def adjust(self, request):
        """
        Ajustar stock manualmente (ingreso o salida).
        Payload: {branch_id, product_id, quantity, action: 'add'|'remove'}
        """
        branch_id = request.data.get('branch')
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 0))
        action_type = request.data.get('action', 'add')
        
        try:
            inventory = Inventory.objects.get(branch_id=branch_id, product_id=product_id)
            
            if action_type == 'add':
                inventory.add_stock(quantity)
                message = f'Se agregaron {quantity} unidades al stock'
            elif action_type == 'remove':
                if inventory.remove_stock(quantity):
                    message = f'Se quitaron {quantity} unidades del stock'
                else:
                    return Response(
                        {'error': 'Stock insuficiente'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'error': 'Acción inválida. Use "add" o "remove"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(inventory)
            return Response({
                'message': message,
                'inventory': serializer.data
            })
        
        except Inventory.DoesNotExist:
            return Response(
                {'error': 'Inventario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class PurchaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para compras a proveedores.
    Admin_cliente y gerente pueden registrar compras.
    """
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAdminClienteOrGerente]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'supplier', 'branch']
    search_fields = ['supplier__name', 'notes']
    ordering_fields = ['purchase_date', 'total_amount']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return Purchase.objects.all()
        elif user.company:
            return Purchase.objects.filter(company=user.company)
        return Purchase.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para ventas POS.
    Admin_cliente, gerente y vendedor pueden registrar ventas.
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [CanCreateSale]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['branch', 'user', 'payment_method']
    ordering_fields = ['created_at', 'total_amount']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Sale.objects.all()
        
        # Filtrar por empresa
        if user.role == 'SUPER_ADMIN':
            pass  # Ver todas
        elif user.company:
            queryset = queryset.filter(branch__company=user.company)
        else:
            return Sale.objects.none()
        
        # Filtros por query params
        branch_id = self.request.query_params.get('branch')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para órdenes de e-commerce.
    Admin_cliente y gerente gestionan todas las órdenes.
    Clientes ven solo sus órdenes.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'status', 'user']
    search_fields = ['customer_name', 'customer_email']
    ordering_fields = ['created_at', 'total_amount', 'status']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return Order.objects.all()
        elif user.role in ['ADMIN_CLIENTE', 'GERENTE']:
            return Order.objects.filter(company=user.company)
        else:
            # Clientes finales ven solo sus órdenes
            return Order.objects.filter(user=user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminClienteOrGerente])
    def update_status(self, request, pk=None):
        """Actualizar estado de una orden"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Estado inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para items del carrito de compras.
    Los usuarios gestionan su propio carrito.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]  # Permitir carritos sin autenticación
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(user=self.request.user)
        else:
            # Para usuarios no autenticados, usar session_key
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            return CartItem.objects.filter(session_key=session_key)
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Agregar producto al carrito"""
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {'error': 'Se requiere product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener o crear session key para usuarios no autenticados
        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Convertir carrito en orden"""
        cart_items = self.get_queryset()
        
        if not cart_items.exists():
            return Response(
                {'error': 'El carrito está vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear orden
        order_data = {
            'company': cart_items.first().product.company,
            'customer_name': request.data.get('customer_name'),
            'customer_email': request.data.get('customer_email'),
            'customer_phone': request.data.get('customer_phone'),
            'customer_address': request.data.get('customer_address'),
            'shipping_cost': request.data.get('shipping_cost', 0),
        }
        
        if request.user.is_authenticated:
            order_data['user'] = request.user
        
        order = Order.objects.create(**order_data)
        
        # Crear items de la orden
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
        
        # Calcular total
        order.calculate_total()
        
        # Vaciar carrito
        cart_items.delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post', 'delete'])
    def clear(self, request):
        """Vaciar el carrito"""
        self.get_queryset().delete()
        return Response({'message': 'Carrito vaciado'})


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pagos.
    Registra pagos de ventas POS y órdenes e-commerce.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'sale', 'order']
    search_fields = ['transaction_id', 'reference']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return Payment.objects.all()
        elif user.company:
            # Filtrar pagos de su empresa
            return Payment.objects.filter(
                Q(sale__branch__company=user.company) |
                Q(order__company=user.company)
            )
        return Payment.objects.none()
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marcar pago como completado"""
        payment = self.get_object()
        payment.status = 'COMPLETADO'
        payment.save()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Marcar pago como reembolsado"""
        payment = self.get_object()
        payment.status = 'REEMBOLSADO'
        payment.save()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


class InventoryMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de movimientos de inventario.
    Registra entradas, salidas y ajustes de stock.
    
    Tipos de movimiento:
    - COMPRA: Ingreso por compra de proveedor
    - VENTA: Salida por venta
    - AJUSTE_POSITIVO: Ajuste manual positivo
    - AJUSTE_NEGATIVO: Ajuste manual negativo
    - DEVOLUCION: Devolución de producto
    - TRANSFERENCIA_IN: Transferencia entrada desde otra sucursal
    - TRANSFERENCIA_OUT: Transferencia salida hacia otra sucursal
    """
    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['movement_type', 'inventory', 'inventory__branch', 'inventory__product']
    search_fields = ['inventory__product__name', 'inventory__product__sku', 'notes']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return InventoryMovement.objects.all()
        elif user.company:
            return InventoryMovement.objects.filter(
                inventory__branch__company=user.company
            )
        return InventoryMovement.objects.none()
    
    def perform_create(self, serializer):
        """Al crear, asignar el usuario actual"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Obtener movimientos filtrados por producto"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'Se requiere product_id'}, status=400)
        
        movements = self.get_queryset().filter(inventory__product_id=product_id)
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        """Obtener movimientos filtrados por sucursal"""
        branch_id = request.query_params.get('branch_id')
        if not branch_id:
            return Response({'error': 'Se requiere branch_id'}, status=400)
        
        movements = self.get_queryset().filter(inventory__branch_id=branch_id)
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumen de movimientos por tipo"""
        queryset = self.get_queryset()
        
        # Filtros opcionales
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        summary = queryset.values('movement_type').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        ).order_by('movement_type')
        
        return Response({
            'summary': list(summary),
            'total_movements': queryset.count()
        })


# ============================================================================
# Reportes (Vistas HTML)
# ============================================================================

@login_required
def stock_report(request):
    """
    Reporte de stock por sucursal.
    GET /reportes/stock/?branch=<id>
    """
    branch_id = request.GET.get('branch')
    category = request.GET.get('category')
    user = request.user
    
    # Filtrar inventario
    inventory = Inventory.objects.select_related('branch', 'product').all()
    
    if user.role != 'SUPER_ADMIN' and user.company:
        inventory = inventory.filter(branch__company=user.company)
    
    if branch_id:
        inventory = inventory.filter(branch_id=branch_id)
    
    if category:
        inventory = inventory.filter(product__category=category)
    
    # Construir reporte
    report_data = []
    for inv in inventory:
        report_data.append({
            'sucursal': inv.branch.name,
            'producto': inv.product.name,
            'sku': inv.product.sku,
            'categoria': inv.product.get_category_display(),
            'stock_actual': inv.stock,
            'punto_reorden': inv.reorder_point,
            'requiere_restock': inv.needs_restock(),
            'ultimo_restock': inv.last_restock_date.strftime('%d/%m/%Y %H:%M') if inv.last_restock_date else None,
            'inventory_obj': inv  # Para template
        })
    
    context = {
        'titulo': 'Reporte de Stock por Sucursal',
        'fecha_generacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'total_registros': len(report_data),
        'datos': report_data
    }
    
    # Renderizar HTML
    return render(request, 'reportes/stock_report.html', context)


@login_required
def sales_report(request):
    """
    Reporte de ventas por período.
    GET /reportes/ventas/?branch=<id>&date_from=<date>&date_to=<date>
    """
    branch_id = request.GET.get('branch')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    user = request.user
    
    # Filtrar ventas
    sales = Sale.objects.select_related('branch', 'user').all()
    
    if user.role != 'SUPER_ADMIN' and user.company:
        sales = sales.filter(branch__company=user.company)
    
    if branch_id:
        sales = sales.filter(branch_id=branch_id)
    if date_from:
        sales = sales.filter(created_at__gte=date_from)
    if date_to:
        sales = sales.filter(created_at__lte=date_to)
    
    # Calcular estadísticas
    stats = sales.aggregate(
        total_ventas=Count('id'),
        monto_total=Sum('total_amount')
    )
    
    # Agrupar por día usando TruncDate
    from django.db.models.functions import TruncDate
    daily_sales = sales.annotate(
        dia=TruncDate('created_at')
    ).values('dia').annotate(
        cantidad=Count('id'),
        total=Sum('total_amount')
    ).order_by('dia')
    
    # Detalle de ventas
    ventas_detalle = []
    for sale in sales[:50]:  # Limitar a 50 para no sobrecargar
        ventas_detalle.append({
            'id': sale.id,
            'fecha': sale.created_at.strftime('%d/%m/%Y %H:%M'),
            'sucursal': sale.branch.name,
            'vendedor': sale.user.username if sale.user else 'N/A',
            'metodo_pago': sale.get_payment_method_display(),
            'total': float(sale.total_amount)
        })
    
    context = {
        'titulo': 'Reporte de Ventas',
        'fecha_generacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'estadisticas': {
            'total_ventas': stats['total_ventas'] or 0,
            'monto_total': float(stats['monto_total'] or 0)
        },
        'ventas_por_dia': [
            {
                'dia': item['dia'].strftime('%d/%m/%Y') if item['dia'] else None,
                'cantidad': item['cantidad'],
                'total': float(item['total'] or 0)
            }
            for item in daily_sales
        ],
        'detalle_ventas': ventas_detalle
    }
    
    # Renderizar HTML
    return render(request, 'reportes/ventas_report.html', context)


@login_required
def supplier_report(request):
    """
    Reporte de proveedores con productos asociados y últimos pedidos.
    GET /reportes/proveedores/
    """
    user = request.user
    
    suppliers = Supplier.objects.all()
    if user.role != 'SUPER_ADMIN' and user.company:
        suppliers = suppliers.filter(company=user.company)
    
    report_data = []
    for supplier in suppliers:
        last_purchases = Purchase.objects.filter(
            supplier=supplier
        ).select_related('branch').order_by('-purchase_date')[:5]
        
        # Contar total de compras y monto
        purchase_stats = Purchase.objects.filter(supplier=supplier).aggregate(
            total_compras=Count('id'),
            monto_total=Sum('total_amount')
        )
        
        report_data.append({
            'id': supplier.id,
            'nombre': supplier.name,
            'rut': supplier.rut,
            'contacto': supplier.contact_name,
            'email': supplier.contact_email,
            'telefono': supplier.contact_phone,
            'activo': supplier.is_active,
            'total_compras': purchase_stats['total_compras'] or 0,
            'monto_total_compras': float(purchase_stats['monto_total'] or 0),
            'ultimas_compras': [
                {
                    'id': p.id,
                    'fecha': p.purchase_date.strftime('%d/%m/%Y'),
                    'total': float(p.total_amount),
                    'sucursal': p.branch.name
                }
                for p in last_purchases
            ]
        })
    
    context = {
        'titulo': 'Reporte de Proveedores',
        'fecha_generacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'total_proveedores': len(report_data),
        'datos': report_data
    }
    
    # Renderizar HTML
    return render(request, 'reportes/proveedores_report.html', context)


@login_required
def inventory_movements_report(request):
    """
    Reporte de movimientos de inventario.
    GET /reportes/movimientos/?tipo=<tipo>&date_from=<date>&date_to=<date>
    """
    user = request.user
    tipo = request.GET.get('tipo')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Filtrar movimientos
    movements = InventoryMovement.objects.select_related(
        'inventory__product', 'inventory__branch', 'user'
    ).all()
    
    if user.role != 'SUPER_ADMIN' and user.company:
        movements = movements.filter(inventory__branch__company=user.company)
    
    if tipo:
        movements = movements.filter(movement_type=tipo)
    if date_from:
        movements = movements.filter(created_at__gte=date_from)
    if date_to:
        movements = movements.filter(created_at__lte=date_to)
    
    # Ordenar por fecha descendente y limitar
    movements = movements.order_by('-created_at')[:100]
    
    # Resumen por tipo
    all_movements = InventoryMovement.objects.all()
    if user.role != 'SUPER_ADMIN' and user.company:
        all_movements = all_movements.filter(inventory__branch__company=user.company)
    
    resumen_tipos = all_movements.values('movement_type').annotate(
        cantidad=Count('id'),
        total_cantidad=Sum('quantity')
    ).order_by('movement_type')
    
    # Mapear tipos a nombres legibles
    tipo_choices = dict(InventoryMovement.MOVEMENT_TYPE_CHOICES)
    resumen_tipos_data = [
        {
            'tipo': item['movement_type'],
            'tipo_display': tipo_choices.get(item['movement_type'], item['movement_type']),
            'cantidad': item['cantidad'],
            'total_cantidad': item['total_cantidad'] or 0
        }
        for item in resumen_tipos
    ]
    
    # Preparar datos de movimientos
    movimientos_data = [
        {
            'fecha': mov.created_at.strftime('%d/%m/%Y %H:%M'),
            'tipo': mov.movement_type,
            'tipo_display': mov.get_movement_type_display(),
            'producto': mov.inventory.product.name,
            'sucursal': mov.inventory.branch.name,
            'cantidad': mov.quantity,
            'stock_anterior': mov.previous_stock,
            'stock_nuevo': mov.new_stock,
            'usuario': mov.user.username if mov.user else 'Sistema',
            'notas': mov.notes
        }
        for mov in movements
    ]
    
    context = {
        'titulo': 'Reporte de Movimientos de Inventario',
        'fecha_generacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'total_movimientos': len(movimientos_data),
        'resumen_tipos': resumen_tipos_data,
        'movimientos': movimientos_data
    }
    
    return render(request, 'reportes/movimientos_report.html', context)


# ============================================================================
# Vistas de Templates (Frontend con Bootstrap)
# ============================================================================

def home(request):
    """Vista principal / landing page"""
    context = {
        'titulo': 'TemucoSoft POS & E-commerce',
        'descripcion': 'Sistema modular de Punto de Venta y Comercio Electrónico'
    }
    return render(request, 'inicio.html', context)


def login_view(request):
    """Vista de login con procesamiento de formulario"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'iniciar_sesion.html')
    
    return render(request, 'iniciar_sesion.html')


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard personalizado según el rol del usuario"""
    user = request.user
    context = {'user': user}
    
    if user.role == 'SUPER_ADMIN':
        context['companies_count'] = Company.objects.count()
        context['active_subscriptions'] = Subscription.objects.filter(active=True).count()
    
    elif user.role in ['ADMIN_CLIENTE', 'GERENTE']:
        if user.company:
            context['products_count'] = Product.objects.filter(company=user.company).count()
            context['branches_count'] = Branch.objects.filter(company=user.company).count()
            context['low_stock'] = Inventory.objects.filter(
                branch__company=user.company,
                stock__lte=F('reorder_point')
            ).count()
    
    elif user.role == 'VENDEDOR':
        context['sales_today'] = Sale.objects.filter(
            user=user,
            created_at__date=timezone.now().date()
        ).count()
    
    return render(request, 'panel.html', context)


def product_catalog(request):
    """Catálogo de productos para e-commerce"""
    # Filtrar productos activos de empresas activas
    products = Product.objects.filter(is_active=True, company__is_active=True)
    
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    # Aplicar filtros
    if category:
        products = products.filter(category=category)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    context = {
        'products': products,
        'categories': Product.CATEGORY_CHOICES,
        'selected_category': category,
        'search_query': search,
    }
    return render(request, 'shop/catalogo.html', context)


def product_detail(request, pk):
    """Detalle de un producto"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    context = {'product': product}
    return render(request, 'shop/producto_detalle.html', context)


def cart_view(request):
    """Vista del carrito de compras"""
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = CartItem.objects.filter(session_key=session_key)
    
    total = sum(item.get_subtotal() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'shop/carrito.html', context)


def add_to_cart(request):
    """Agregar producto al carrito (vista de template)"""
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            if request.user.is_authenticated:
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                
                cart_item, created = CartItem.objects.get_or_create(
                    session_key=session_key,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
            
            messages.success(request, f'{product.name} agregado al carrito')
        except Product.DoesNotExist:
            messages.error(request, 'Producto no encontrado')
        except Exception as e:
            messages.error(request, f'Error al agregar al carrito: {str(e)}')
    
    return redirect('cart')


def cart_clear_view(request):
    """Vaciar el carrito completamente"""
    if request.method == 'POST':
        if request.user.is_authenticated:
            CartItem.objects.filter(user=request.user).delete()
        else:
            session_key = request.session.session_key
            if session_key:
                CartItem.objects.filter(session_key=session_key).delete()
        messages.success(request, 'Carrito vaciado')
    return redirect('cart')


def cart_remove_item_view(request, item_id):
    """Eliminar un item específico del carrito"""
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                item = CartItem.objects.get(id=item_id, user=request.user)
            else:
                session_key = request.session.session_key
                item = CartItem.objects.get(id=item_id, session_key=session_key)
            item.delete()
            messages.success(request, 'Producto eliminado del carrito')
        except CartItem.DoesNotExist:
            messages.error(request, 'Item no encontrado')
    return redirect('cart')


def checkout_view(request):
    """Vista de checkout"""
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        cart_items = CartItem.objects.filter(session_key=session_key) if session_key else CartItem.objects.none()
    
    if not cart_items.exists():
        return redirect('cart')
    
    total = sum(item.get_subtotal() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'shop/pagar.html', context)


def process_order(request):
    """Procesar orden de compra"""
    if request.method == 'POST':
        # Obtener items del carrito
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            session_key = request.session.session_key
            cart_items = CartItem.objects.filter(session_key=session_key) if session_key else CartItem.objects.none()
        
        if not cart_items.exists():
            messages.error(request, 'El carrito está vacío')
            return redirect('cart')
        
        try:
            # Calcular total
            subtotal = sum(item.get_subtotal() for item in cart_items)
            shipping_cost = 5000
            total = subtotal + shipping_cost
            
            # Obtener la primera empresa con productos (o la del usuario si está autenticado)
            company = request.user.company if request.user.is_authenticated and request.user.company else cart_items.first().product.company
            
            # Crear orden
            order = Order.objects.create(
                company=company,
                user=request.user if request.user.is_authenticated else None,
                customer_name=request.POST.get('full_name'),
                customer_email=request.POST.get('email'),
                customer_phone=request.POST.get('phone'),
                customer_address=f"{request.POST.get('address')}, {request.POST.get('city')}",
                status='PENDIENTE',
                total_amount=total,
                shipping_cost=shipping_cost,
                notes=f"Método de pago: {request.POST.get('payment_method')}"
            )
            
            # Crear items de la orden
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price
                )
            
            # Limpiar carrito
            cart_items.delete()
            
            messages.success(request, f'¡Orden #{order.id} creada exitosamente! Te contactaremos pronto.')
            return redirect('product_catalog')
            
        except Exception as e:
            messages.error(request, f'Error al procesar orden: {str(e)}')
            return redirect('checkout')
    
    return redirect('checkout')


@login_required
def inventory_view(request):
    """Vista de inventario por sucursal"""
    if request.user.company:
        inventory = Inventory.objects.filter(branch__company=request.user.company).select_related('product', 'branch')
        branches = Branch.objects.filter(company=request.user.company)
        products = Product.objects.filter(company=request.user.company)
    else:
        inventory = Inventory.objects.none()
        branches = Branch.objects.none()
        products = Product.objects.none()
    
    context = {
        'inventory': inventory,
        'branches': branches,
        'products': products
    }
    return render(request, 'inventario.html', context)


@login_required
def suppliers_view(request):
    """Vista de proveedores"""
    if request.user.company:
        suppliers = Supplier.objects.filter(company=request.user.company)
    else:
        suppliers = Supplier.objects.none()
    
    context = {'suppliers': suppliers}
    return render(request, 'proveedores.html', context)


@login_required
def sales_view(request):
    """Vista de ventas POS"""
    if request.user.company:
        sales = Sale.objects.filter(branch__company=request.user.company).order_by('-created_at')[:50]
    else:
        sales = Sale.objects.none()
    
    context = {'sales': sales}
    return render(request, 'ventas.html', context)


@login_required
def reports_view(request):
    """Vista de reportes - Solo para ADMIN_CLIENTE y GERENTE"""
    context = {}
    
    # Solo los usuarios con empresa pueden ver reportes (respeto a privacidad)
    if request.user.role in ['ADMIN_CLIENTE', 'GERENTE']:
        if request.user.company:
            # Reporte de stock bajo
            low_stock = Inventory.objects.filter(
                branch__company=request.user.company,
                stock__lte=F('reorder_point')
            )
            
            # Ventas del mes
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
            monthly_sales = Sale.objects.filter(
                branch__company=request.user.company,
                created_at__gte=month_start
            ).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            )
            
            # Proveedores activos
            suppliers_count = Supplier.objects.filter(
                company=request.user.company,
                is_active=True
            ).count()
            
            # Movimientos de inventario recientes
            inventory_movements = InventoryMovement.objects.filter(
                inventory__branch__company=request.user.company
            ).select_related('inventory__product', 'inventory__branch')[:10]
            
            context['low_stock'] = low_stock
            context['monthly_sales'] = monthly_sales
            context['suppliers_count'] = suppliers_count
            context['inventory_movements'] = inventory_movements
    
    # SUPER_ADMIN puede ver todo
    elif request.user.role == 'SUPER_ADMIN':
        low_stock = Inventory.objects.filter(stock__lte=F('reorder_point'))
        
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        monthly_sales = Sale.objects.filter(
            created_at__gte=month_start
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        suppliers_count = Supplier.objects.filter(is_active=True).count()
        inventory_movements = InventoryMovement.objects.all().select_related(
            'inventory__product', 'inventory__branch'
        )[:10]
        
        context['low_stock'] = low_stock
        context['monthly_sales'] = monthly_sales
        context['suppliers_count'] = suppliers_count
        context['inventory_movements'] = inventory_movements
    
    return render(request, 'reportes.html', context)


@login_required
def pos_view(request):
    """Vista POS (Punto de Venta) para vendedores"""
    products = Product.objects.none()
    
    if request.user.role == 'VENDEDOR' and request.user.company:
        products = Product.objects.filter(
            company=request.user.company,
            is_active=True
        ).select_related('company')
    
    context = {'products': products}
    return render(request, 'pos.html', context)


@login_required
def branches_view(request):
    """Vista de sucursales para admin_cliente"""
    if request.method == 'POST':
        # Crear nueva sucursal
        if request.user.company:
            try:
                Branch.objects.create(
                    company=request.user.company,
                    name=request.POST.get('name'),
                    address=request.POST.get('address'),
                    phone=request.POST.get('phone', ''),
                    is_active=request.POST.get('is_active') == 'on'
                )
                messages.success(request, 'Sucursal creada exitosamente')
            except Exception as e:
                messages.error(request, f'Error al crear sucursal: {str(e)}')
        return redirect('branches')
    
    branches = Branch.objects.none()
    
    if request.user.role in ['ADMIN_CLIENTE', 'SUPER_ADMIN']:
        if request.user.role == 'SUPER_ADMIN':
            branches = Branch.objects.all()
        else:
            branches = Branch.objects.filter(company=request.user.company)
    
    context = {'branches': branches}
    return render(request, 'sucursales.html', context)


@login_required
def users_create_view(request):
    """Vista para crear usuarios (solo admin_cliente)"""
    if request.user.role not in ['ADMIN_CLIENTE', 'SUPER_ADMIN']:
        messages.error(request, 'No tienes permisos para crear usuarios')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        # Validar que el usuario no exista
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'usuarios_crear.html')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            rut=request.POST.get('rut', ''),
            phone=request.POST.get('phone', ''),
            is_active=request.POST.get('is_active') == 'on'
        )
        
        # Asignar empresa
        if request.user.role == 'SUPER_ADMIN':
            company_id = request.POST.get('company')
            if company_id:
                user.company_id = company_id
                user.save()
        else:
            user.company = request.user.company
            user.save()
        
        messages.success(request, f'Usuario {username} creado exitosamente')
        return redirect('dashboard')
    
    companies = Company.objects.filter(is_active=True) if request.user.role == 'SUPER_ADMIN' else []
    context = {'companies': companies}
    return render(request, 'usuarios_crear.html', context)


@login_required
def subscription_view(request):
    """Vista de suscripción para admin_cliente"""
    subscription = None
    current_users = 0
    current_branches = 0
    users_percentage = 0
    branches_percentage = 0
    
    if request.user.role in ['ADMIN_CLIENTE', 'SUPER_ADMIN'] and request.user.company:
        try:
            subscription = Subscription.objects.get(company=request.user.company)
            current_users = User.objects.filter(company=request.user.company, is_active=True).count()
            current_branches = Branch.objects.filter(company=request.user.company, is_active=True).count()
            
            # Calcular porcentajes para las barras de progreso
            if subscription.max_users > 0:
                users_percentage = min(100, (current_users / subscription.max_users) * 100)
            if subscription.max_branches > 0:
                branches_percentage = min(100, (current_branches / subscription.max_branches) * 100)
        except Subscription.DoesNotExist:
            messages.warning(request, 'No hay información de suscripción disponible')
    
    context = {
        'subscription': subscription,
        'current_users': current_users,
        'current_branches': current_branches,
        'users_percentage': users_percentage,
        'branches_percentage': branches_percentage
    }
    return render(request, 'suscripcion.html', context)


@login_required
def purchase_create_view(request):
    """Vista para crear compras"""
    if request.user.role not in ['ADMIN_CLIENTE', 'GERENTE']:
        messages.error(request, 'No tienes permisos para crear compras')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Crear la compra
        branch_id = request.POST.get('branch')
        supplier_id = request.POST.get('supplier')
        purchase_date = request.POST.get('purchase_date')
        total_amount = request.POST.get('total_amount', 0)
        
        try:
            purchase = Purchase.objects.create(
                company=request.user.company,
                branch_id=branch_id,
                supplier_id=supplier_id,
                user=request.user,
                purchase_date=purchase_date,
                total_amount=total_amount,
                notes=request.POST.get('notes', '')
            )
            
            # Crear items de compra
            products = request.POST.getlist('product[]')
            quantities = request.POST.getlist('quantity[]')
            prices = request.POST.getlist('unit_price[]')
            
            for product_id, quantity, price in zip(products, quantities, prices):
                if product_id and quantity and price:
                    PurchaseItem.objects.create(
                        purchase=purchase,
                        product_id=product_id,
                        quantity=int(quantity),
                        unit_cost=float(price)  # Usar unit_cost no unit_price
                    )
                    
                    # Actualizar inventario
                    try:
                        inventory = Inventory.objects.get(
                            branch_id=branch_id,
                            product_id=product_id
                        )
                        inventory.add_stock(int(quantity))
                    except Inventory.DoesNotExist:
                        # Crear inventario si no existe
                        inventory = Inventory.objects.create(
                            branch_id=branch_id,
                            product_id=product_id,
                            stock=int(quantity),
                            reorder_point=10
                        )
            
            messages.success(request, f'Compra #{purchase.id} registrada exitosamente')
            return redirect('inventory')
        except Exception as e:
            messages.error(request, f'Error al crear compra: {str(e)}')
    
    branches = Branch.objects.filter(company=request.user.company) if request.user.company else []
    suppliers = Supplier.objects.filter(company=request.user.company) if request.user.company else []
    products = Product.objects.filter(company=request.user.company, is_active=True) if request.user.company else []
    
    context = {
        'branches': branches,
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'compras_crear.html', context)


# ============================================
# VISTAS SUPER_ADMIN - Gestión de Plataforma
# ============================================

@login_required
def superadmin_companies(request):
    """Vista de gestión de empresas clientes - Solo SUPER_ADMIN"""
    if request.user.role != 'SUPER_ADMIN':
        return redirect('dashboard')
    
    companies = Company.objects.annotate(
        user_count=Count('users')
    ).select_related('subscription')
    
    active_companies = companies.filter(is_active=True).count()
    active_subscriptions = Subscription.objects.filter(active=True).count()
    total_users = User.objects.filter(company__isnull=False).count()
    
    context = {
        'companies': companies,
        'companies_count': companies.count(),
        'active_companies': active_companies,
        'active_subscriptions': active_subscriptions,
        'total_users': total_users,
    }
    return render(request, 'superadmin/empresas.html', context)


@login_required
def superadmin_create_company(request):
    """Crear nueva empresa cliente con suscripción y admin - Solo SUPER_ADMIN"""
    if request.user.role != 'SUPER_ADMIN':
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Crear empresa
            company = Company.objects.create(
                rut=request.POST['rut'],
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                is_active=True
            )
            
            # Crear suscripción
            Subscription.objects.create(
                company=company,
                plan_name=request.POST['plan_name'],
                active=True
            )
            
            # Crear admin de la empresa
            User.objects.create_user(
                username=request.POST['admin_username'],
                email=request.POST['admin_email'],
                password=request.POST['admin_password'],
                role='ADMIN_CLIENTE',
                company=company
            )
            
            messages.success(request, f'Empresa {company.name} creada exitosamente con su administrador.')
        except Exception as e:
            messages.error(request, f'Error al crear empresa: {str(e)}')
    
    return redirect('superadmin_companies')


@login_required
def superadmin_edit_company(request, company_id):
    """Editar empresa cliente - Solo SUPER_ADMIN"""
    if request.user.role != 'SUPER_ADMIN':
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            company = Company.objects.get(id=company_id)
            company.name = request.POST['name']
            company.email = request.POST['email']
            company.phone = request.POST.get('phone', '')
            company.address = request.POST.get('address', '')
            company.is_active = request.POST.get('is_active') == '1'
            company.save()
            
            # Actualizar plan de suscripción si existe
            if hasattr(company, 'subscription'):
                company.subscription.plan_name = request.POST['plan_name']
                company.subscription.save()
            
            messages.success(request, f'Empresa {company.name} actualizada exitosamente.')
        except Company.DoesNotExist:
            messages.error(request, 'Empresa no encontrada.')
        except Exception as e:
            messages.error(request, f'Error al actualizar empresa: {str(e)}')
    
    return redirect('superadmin_companies')


@login_required
def superadmin_company_users(request, company_id):
    """Vista de usuarios de una empresa específica - Solo SUPER_ADMIN"""
    if request.user.role != 'SUPER_ADMIN':
        return redirect('dashboard')
    
    try:
        company = Company.objects.get(id=company_id)
        users = User.objects.filter(company=company).select_related('company')
        
        total_users = users.count()
        admin_count = users.filter(role='ADMIN_CLIENTE').count()
        active_count = users.filter(is_active=True).count()
        
        # Obtener límite del plan
        plan_limit = 0
        if hasattr(company, 'subscription'):
            plan_limits = {
                'BASICO': 5,
                'ESTANDAR': 20,
                'PREMIUM': 100
            }
            plan_limit = plan_limits.get(company.subscription.plan_name, 0)
        
        context = {
            'company': company,
            'users': users,
            'total_users': total_users,
            'plan_limit': plan_limit,
            'admin_count': admin_count,
            'active_count': active_count,
        }
        return render(request, 'superadmin/empresa_usuarios.html', context)
    except Company.DoesNotExist:
        messages.error(request, 'Empresa no encontrada.')
        return redirect('superadmin_companies')


@login_required
def superadmin_create_user(request, company_id):
    """Crear nuevo usuario para una empresa - Solo SUPER_ADMIN"""
    if request.user.role != 'SUPER_ADMIN':
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            company = Company.objects.get(id=company_id)
            
            User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password'],
                rut=request.POST.get('rut', ''),
                role=request.POST['role'],
                company=company,
                is_active=True
            )
            
            messages.success(request, f'Usuario {request.POST["username"]} creado exitosamente.')
        except Company.DoesNotExist:
            messages.error(request, 'Empresa no encontrada.')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    return redirect('superadmin_company_users', company_id=company_id)


@login_required
def superadmin_edit_user(request, user_id):
    """Editar usuario de empresa - Solo SUPER_ADMIN"""
    if request.user.role != 'SUPER_ADMIN':
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            company_id = user.company.id
            
            user.email = request.POST['email']
            user.rut = request.POST.get('rut', '')
            user.role = request.POST['role']
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()
            
            messages.success(request, f'Usuario {user.username} actualizado exitosamente.')
            return redirect('superadmin_company_users', company_id=company_id)
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('superadmin_companies')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
            return redirect('superadmin_companies')
    
    return redirect('superadmin_companies')


@login_required
def reset_password(request, username):
    """Reset password de usuario a 'admin123' - AJAX endpoint - Solo SUPER_ADMIN"""
    if request.user.role != 'SUPER_ADMIN':
        return JsonResponse({'success': False, 'message': 'No autorizado'}, status=403)
    
    if request.method == 'POST':
        try:
            user = User.objects.get(username=username)
            user.set_password('admin123')
            user.save()
            return JsonResponse({'success': True, 'message': 'Contraseña reseteada a admin123'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
