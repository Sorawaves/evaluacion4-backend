"""
Script para cargar datos de prueba en el sistema POS + E-commerce.
Crea empresas, usuarios, productos, sucursales, inventario y transacciones de ejemplo.

Ejecutar con: python load_demo_data.py
"""
import os
import django
import sys
from decimal import Decimal
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'temucosoft.settings')
django.setup()

from django.contrib.auth import get_user_model
from pos_ecommerce.models import (
    Company, Subscription, Branch, Supplier, Product, Inventory,
    Purchase, PurchaseItem, Sale, SaleItem, Order, OrderItem
)

User = get_user_model()


def create_companies():
    """Crear empresas de ejemplo"""
    print("Creando empresas...")
    
    companies_data = [
        {
            'name': 'TecnoShop Ltda.',
            'rut': '76543210-5',
            'email': 'contacto@tecnoshop.cl',
            'phone': '+56912345678',
            'address': 'Av. Prat 123, Temuco'
        },
        {
            'name': 'MegaRetail S.A.',
            'rut': '78901234-7',
            'email': 'info@megaretail.cl',
            'phone': '+56987654321',
            'address': 'Manuel Bulnes 456, Temuco'
        }
    ]
    
    companies = []
    for data in companies_data:
        company, created = Company.objects.get_or_create(
            rut=data['rut'],
            defaults=data
        )
        companies.append(company)
        if created:
            print(f"  ✓ Creada: {company.name}")
    
    return companies


def create_subscriptions(companies):
    """Crear suscripciones para las empresas"""
    print("\nCreando suscripciones...")
    
    # Configuración de planes según home.html
    plan_configs = {
        'ESTANDAR': {
            'max_branches': 3,
            'max_users': 5,
            'has_api_access': True,
            'has_reports': True
        },
        'PREMIUM': {
            'max_branches': 999,  # Ilimitado
            'max_users': 999,  # Ilimitado
            'has_api_access': True,
            'has_reports': True
        }
    }
    
    plans = ['ESTANDAR', 'PREMIUM']
    
    for i, company in enumerate(companies):
        plan = plans[i % len(plans)]
        config = plan_configs[plan]
        
        subscription, created = Subscription.objects.get_or_create(
            company=company,
            defaults={
                'plan_name': plan,
                'start_date': datetime.now().date(),
                'end_date': (datetime.now() + timedelta(days=365)).date(),
                'active': True,
                **config
            }
        )
        if created:
            print(f"  ✓ Suscripción {plan} creada para {company.name}")
            print(f"    - Sucursales: {config['max_branches']}")
            print(f"    - Usuarios: {config['max_users']}")
            print(f"    - API: {'Sí' if config['has_api_access'] else 'No'}")
            print(f"    - Reportes: {'Sí' if config['has_reports'] else 'No'}")


def create_users(companies):
    """Crear usuarios del sistema"""
    print("\nCreando usuarios...")
    
    # Super Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@temucosoft.cl',
            password='admin123',
            role='SUPER_ADMIN',
            rut='11111111-1'
        )
        print(f"  ✓ Super Admin: {admin.username}")
    
    # Mapeo de nombres cortos para empresas
    company_names = {
        'TecnoShop Ltda.': 'tecnoshop',
        'MegaRetail S.A.': 'megaretail'
    }
    
    # Admin Cliente para cada empresa
    users = []
    for company in companies:
        short_name = company_names.get(company.name, company.name.lower().replace(' ', ''))
        
        # Admin Cliente
        username = f"admin_{short_name}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"admin@{short_name}.cl",
                password='admin123',
                role='ADMIN_CLIENTE',
                company=company,
                rut=f'{22000000 + company.id}-{company.id}'
            )
            users.append(user)
            print(f"  ✓ Admin Cliente: {user.username} ({company.name})")
        
        # Gerente
        username = f"gerente_{short_name}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"gerente@{short_name}.cl",
                password='gerente123',
                role='GERENTE',
                company=company,
                rut=f'{33000000 + company.id}-{company.id}'
            )
            users.append(user)
            print(f"  ✓ Gerente: {user.username} ({company.name})")
        
        # Vendedor
        username = f"vendedor_{short_name}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"vendedor@{short_name}.cl",
                password='vendedor123',
                role='VENDEDOR',
                company=company,
                rut=f'{44000000 + company.id}-{company.id}'
            )
            users.append(user)
            print(f"  ✓ Vendedor: {user.username} ({company.name})")
    
    return users


def create_branches(companies):
    """Crear sucursales"""
    print("\nCreando sucursales...")
    
    branches = []
    for company in companies:
        branch_data = [
            {'name': 'Sucursal Centro', 'address': f'Centro, Temuco - {company.name}', 'phone': '+56911111111'},
            {'name': 'Sucursal Norte', 'address': f'Sector Norte, Temuco - {company.name}', 'phone': '+56922222222'}
        ]
        
        for data in branch_data:
            branch, created = Branch.objects.get_or_create(
                company=company,
                name=data['name'],
                defaults=data
            )
            branches.append(branch)
            if created:
                print(f"  ✓ {branch.name} ({company.name})")
    
    return branches


def create_suppliers(companies):
    """Crear proveedores"""
    print("\nCreando proveedores...")
    
    suppliers = []
    supplier_names = ['Distribuidora Nacional S.A.', 'Importadora del Sur Ltda.', 'Mayorista Regional']
    
    for company in companies:
        for i, name in enumerate(supplier_names):
            rut = f'{85000000 + i}-{i+1}'
            supplier, created = Supplier.objects.get_or_create(
                company=company,
                rut=rut,
                defaults={
                    'name': f'{name} - {company.name}',
                    'contact_name': f'Contacto {i+1}',
                    'contact_email': f'proveedor{i+1}@{company.rut[:8]}.cl',
                    'contact_phone': f'+56956{i}00000',
                    'address': f'Dirección Proveedor {i+1}'
                }
            )
            suppliers.append(supplier)
            if created:
                print(f"  ✓ {supplier.name}")
    
    return suppliers


def create_products(companies):
    """Crear productos"""
    print("\nCreando productos...")
    
    products_data = [
        # Electrónicos
        {'sku': 'NOTEBOOK-001', 'name': 'Notebook HP 15"', 'category': 'ELECTRONICOS', 'price': 599990, 'cost': 450000},
        {'sku': 'MOUSE-001', 'name': 'Mouse Logitech Inalámbrico', 'category': 'ELECTRONICOS', 'price': 19990, 'cost': 12000},
        {'sku': 'TECLADO-001', 'name': 'Teclado Mecánico RGB', 'category': 'ELECTRONICOS', 'price': 49990, 'cost': 35000},
        {'sku': 'CELULAR-001', 'name': 'Smartphone Samsung Galaxy', 'category': 'ELECTRONICOS', 'price': 399990, 'cost': 280000},
        
        # Ropa
        {'sku': 'POLERA-001', 'name': 'Polera Algodón Unisex', 'category': 'ROPA', 'price': 12990, 'cost': 8000},
        {'sku': 'JEANS-001', 'name': 'Jeans Clásico Azul', 'category': 'ROPA', 'price': 29990, 'cost': 18000},
        {'sku': 'CHAQUETA-001', 'name': 'Chaqueta Impermeable', 'category': 'ROPA', 'price': 45990, 'cost': 30000},
        
        # Alimentos
        {'sku': 'CAFE-001', 'name': 'Café Premium 500g', 'category': 'ALIMENTOS', 'price': 8990, 'cost': 6000},
        {'sku': 'CHOCOLATE-001', 'name': 'Chocolate Artesanal 200g', 'category': 'ALIMENTOS', 'price': 5990, 'cost': 3500},
        {'sku': 'GALLETAS-001', 'name': 'Galletas Integrales 300g', 'category': 'ALIMENTOS', 'price': 3990, 'cost': 2000},
        
        # Hogar
        {'sku': 'LAMPARA-001', 'name': 'Lámpara LED Escritorio', 'category': 'HOGAR', 'price': 34990, 'cost': 22000},
        {'sku': 'ALMOHADA-001', 'name': 'Almohada Viscoelástica', 'category': 'HOGAR', 'price': 19990, 'cost': 12000},
        {'sku': 'SABANAS-001', 'name': 'Juego de Sábanas 2 plazas', 'category': 'HOGAR', 'price': 24990, 'cost': 15000},
        
        # Deportes
        {'sku': 'BALON-001', 'name': 'Balón Fútbol Profesional', 'category': 'DEPORTES', 'price': 24990, 'cost': 16000},
        {'sku': 'MANCUERNA-001', 'name': 'Mancuerna 5kg (par)', 'category': 'DEPORTES', 'price': 29990, 'cost': 20000},
        {'sku': 'COLCHONETA-001', 'name': 'Colchoneta Yoga Premium', 'category': 'DEPORTES', 'price': 19990, 'cost': 12000},
        
        # Salud y Belleza
        {'sku': 'SHAMPOO-001', 'name': 'Shampoo Reparador 400ml', 'category': 'SALUD', 'price': 8990, 'cost': 5000},
        {'sku': 'CREMA-001', 'name': 'Crema Facial Hidratante', 'category': 'SALUD', 'price': 15990, 'cost': 9000},
        
        # Libros
        {'sku': 'LIBRO-001', 'name': 'Libro Bestseller Ficción', 'category': 'LIBROS', 'price': 14990, 'cost': 8000},
        {'sku': 'LIBRO-002', 'name': 'Manual de Programación Python', 'category': 'LIBROS', 'price': 24990, 'cost': 15000},
    ]
    
    products = []
    for company in companies:
        for data in products_data:
            product, created = Product.objects.get_or_create(
                company=company,
                sku=f"{company.rut[:8]}-{data['sku']}",
                defaults={
                    'name': data['name'],
                    'category': data['category'],
                    'description': f"Producto de calidad: {data['name']}. Disponible para venta en sucursales y tienda online.",
                    'price': Decimal(data['price']),
                    'cost': Decimal(data['cost'])
                }
            )
            products.append(product)
            if created:
                print(f"  ✓ {product.name} ({company.name})")
    
    return products


def create_inventory(branches, products):
    """Crear inventario inicial"""
    print("\nCreando inventario...")
    
    count = 0
    for branch in branches:
        # Filtrar productos de la misma empresa
        company_products = [p for p in products if p.company == branch.company]
        
        for product in company_products:
            inventory, created = Inventory.objects.get_or_create(
                branch=branch,
                product=product,
                defaults={
                    'stock': 100,
                    'reorder_point': 20
                }
            )
            if created:
                count += 1
    
    print(f"  ✓ {count} registros de inventario creados")


def create_purchases(branches, suppliers):
    """Crear compras de ejemplo"""
    print("\nCreando compras...")
    
    from django.utils import timezone
    
    for branch in branches:
        # Obtener proveedor de la misma empresa
        company_suppliers = [s for s in suppliers if s.company == branch.company]
        if not company_suppliers:
            continue
        
        supplier = company_suppliers[0]
        
        # Obtener gerente
        gerente = User.objects.filter(company=branch.company, role='GERENTE').first()
        if not gerente:
            continue
        
        # Crear compra
        purchase = Purchase.objects.create(
            company=branch.company,
            supplier=supplier,
            branch=branch,
            user=gerente,
            purchase_date=timezone.now().date()
        )
        
        # Agregar items
        products = Product.objects.filter(company=branch.company)[:5]
        for product in products:
            PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                quantity=50,
                unit_cost=product.cost
            )
        
        purchase.calculate_total()
        print(f"  ✓ Compra #{purchase.id} en {branch.name} por ${purchase.total_amount}")


def create_sales(branches):
    """Crear ventas de ejemplo"""
    print("\nCreando ventas...")
    
    for branch in branches:
        vendedor = User.objects.filter(company=branch.company, role='VENDEDOR').first()
        if not vendedor:
            continue
        
        # Crear venta
        sale = Sale.objects.create(
            branch=branch,
            user=vendedor,
            payment_method='EFECTIVO'
        )
        
        # Agregar items
        products = Product.objects.filter(company=branch.company)[:3]
        for product in products:
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=2,
                unit_price=product.price
            )
        
        sale.calculate_total()
        print(f"  ✓ Venta #{sale.id} en {branch.name} por ${sale.total_amount}")


def create_orders(companies):
    """Crear órdenes de e-commerce"""
    print("\nCreando órdenes de e-commerce...")
    
    for company in companies:
        order = Order.objects.create(
            company=company,
            customer_name='Cliente E-commerce',
            customer_email='cliente@example.com',
            customer_phone='+56987654321',
            customer_address='Dirección de entrega 123',
            shipping_cost=Decimal('5000'),
            status='PENDIENTE'
        )
        
        # Agregar productos
        products = Product.objects.filter(company=company)[:4]
        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                unit_price=product.price
            )
        
        order.calculate_total()
        print(f"  ✓ Orden #{order.id} para {company.name} por ${order.total_amount}")


def main():
    """Función principal para cargar todos los datos"""
    print("=" * 60)
    print("CARGANDO DATOS DE PRUEBA - SISTEMA POS + E-COMMERCE")
    print("=" * 60)
    
    try:
        companies = create_companies()
        create_subscriptions(companies)
        users = create_users(companies)
        branches = create_branches(companies)
        suppliers = create_suppliers(companies)
        products = create_products(companies)
        create_inventory(branches, products)
        create_purchases(branches, suppliers)
        create_sales(branches)
        create_orders(companies)
        
        print("\n" + "=" * 60)
        print("✅ DATOS CARGADOS EXITOSAMENTE")
        print("=" * 60)
        print("\nCredenciales de acceso:")
        print("  🔑 Super Admin: admin / admin123")
        print("\n  🏢 TecnoShop:")
        print("    👔 Admin: admin_tecnoshop / admin123")
        print("    📊 Gerente: gerente_tecnoshop / gerente123")
        print("    🛒 Vendedor: vendedor_tecnoshop / vendedor123")
        print("\n  🏢 MegaRetail:")
        print("    👔 Admin: admin_megaretail / admin123")
        print("    📊 Gerente: gerente_megaretail / gerente123")
        print("    🛒 Vendedor: vendedor_megaretail / vendedor123")
        print("\n🌐 Acceder al sistema:")
        print("  Login: http://localhost:8000/login/")
        print("  Admin Django: http://localhost:8000/admin/")
        print("  API REST: http://localhost:8000/api/")
        print("  Documentación: http://localhost:8000/swagger/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
