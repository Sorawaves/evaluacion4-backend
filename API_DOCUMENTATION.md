# 🚀 API POS + E-commerce TemucoSoft S.A.

## 📋 Índice
1. [Autenticación JWT](#autenticacion)
2. [Endpoints CRUD](#endpoints-crud)
3. [Reportes](#reportes)
4. [Ejemplos de Uso](#ejemplos)
5. [Swagger/ReDoc](#documentacion)

---

## 🔐 Autenticación JWT {#autenticacion}

### Obtener Token
```bash
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLC...",
  "refresh": "eyJ0eXAiOiJKV1QiLC..."
}
```

### Usar Token
```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLC...
```

### Refrescar Token
```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLC..."
}
```

---

## 📦 Endpoints CRUD {#endpoints-crud}

Todos los endpoints bajo `/api/` requieren autenticación JWT salvo los marcados como **[Público]**.

### 🏢 Compañías (Companies)
- `GET /api/companies/` - Listar todas las compañías (solo SUPER_ADMIN)
- `POST /api/companies/` - Crear compañía (solo SUPER_ADMIN)
- `GET /api/companies/{id}/` - Detalle de compañía
- `PUT /api/companies/{id}/` - Actualizar compañía
- `DELETE /api/companies/{id}/` - Eliminar compañía

**Ejemplo POST:**
```json
{
  "rut": "76.123.456-7",
  "name": "Farmacia Santa Rosa",
  "address": "Av. Alemania 350, Temuco",
  "phone": "+56912345678",
  "email": "contacto@farmaciasantarosa.cl"
}
```

### 💳 Suscripciones (Subscriptions)
- `GET /api/subscriptions/` - Listar suscripciones
- `POST /api/subscriptions/` - Crear suscripción
- `GET /api/subscriptions/{id}/` - Detalle
- `PUT /api/subscriptions/{id}/` - Actualizar

**Ejemplo POST:**
```json
{
  "company": 1,
  "plan_name": "PREMIUM",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "active": true,
  "price": 299990.00
}
```

### 👥 Usuarios (Users)
- `GET /api/users/` - Listar usuarios de mi compañía
- `POST /api/users/` - Crear usuario
- `GET /api/users/me/` - Mi perfil actual
- `GET /api/users/{id}/` - Detalle usuario
- `PUT /api/users/{id}/` - Actualizar usuario

**Roles disponibles:**
- `SUPER_ADMIN` - Administrador TemucoSoft
- `ADMIN_CLIENTE` - Dueño de tienda/farmacia
- `GERENTE` - Gerente de sucursal
- `VENDEDOR` - Cajero/vendedor POS
- `CLIENTE_FINAL` - Cliente e-commerce

**Ejemplo POST:**
```json
{
  "username": "vendedor1",
  "email": "vendedor1@farmacia.cl",
  "password": "password123",
  "rut": "18.456.789-2",
  "role": "VENDEDOR",
  "company": 1,
  "branch": 1
}
```

### 🏪 Sucursales (Branches)
- `GET /api/branches/` - Listar mis sucursales
- `POST /api/branches/` - Crear sucursal
- `GET /api/branches/{id}/` - Detalle
- `PUT /api/branches/{id}/` - Actualizar

**Ejemplo POST:**
```json
{
  "company": 1,
  "name": "Sucursal Centro",
  "address": "Prat 450, Temuco",
  "phone": "+56912345679"
}
```

### 🚚 Proveedores (Suppliers)
- `GET /api/suppliers/` - Listar proveedores
- `POST /api/suppliers/` - Crear proveedor
- `GET /api/suppliers/{id}/` - Detalle
- `PUT /api/suppliers/{id}/` - Actualizar

**Ejemplo POST:**
```json
{
  "company": 1,
  "rut": "78.987.654-3",
  "name": "Distribuidora Farmacéutica S.A.",
  "contact_name": "Juan Pérez",
  "phone": "+56987654321",
  "email": "contacto@distribuidora.cl"
}
```

### 📦 Productos (Products)
- `GET /api/products/` **[Público para lectura]**
- `POST /api/products/` - Crear producto
- `GET /api/products/{id}/`
- `PUT /api/products/{id}/`
- `DELETE /api/products/{id}/`

**Filtros disponibles:**
- `?category=MEDICAMENTOS` - Filtrar por categoría
- `?search=paracetamol` - Búsqueda en nombre/descripción
- `?is_active=true` - Solo activos

**Ejemplo POST:**
```json
{
  "company": 1,
  "sku": "PARA500",
  "name": "Paracetamol 500mg x 20 tabletas",
  "description": "Analgésico antipirético",
  "category": "MEDICAMENTOS",
  "price": 2990.00,
  "cost": 1500.00,
  "is_active": true
}
```

### 📊 Inventario (Inventory)
- `GET /api/inventory/` - Stock por sucursal
- `POST /api/inventory/` - Ajustar stock
- `GET /api/inventory/{id}/`
- `PUT /api/inventory/{id}/`

**Ejemplo POST:**
```json
{
  "branch": 1,
  "product": 5,
  "stock": 150,
  "reorder_point": 30
}
```

### 🛒 Compras (Purchases)
- `GET /api/purchases/` - Historial de compras a proveedores
- `POST /api/purchases/` - Registrar compra
- `GET /api/purchases/{id}/`

**Ejemplo POST:**
```json
{
  "branch": 1,
  "supplier": 2,
  "product": 5,
  "quantity": 100,
  "unit_cost": 1450.00,
  "total_cost": 145000.00
}
```

### 💰 Ventas POS (Sales)
- `GET /api/sales/` - Historial de ventas POS
- `POST /api/sales/` - Registrar venta
- `GET /api/sales/{id}/`

**Métodos de pago:**
- `CASH` - Efectivo
- `CREDIT_CARD` - Tarjeta de crédito
- `DEBIT_CARD` - Tarjeta de débito
- `TRANSFER` - Transferencia

**Ejemplo POST:**
```json
{
  "branch": 1,
  "user": 3,
  "items": [
    {
      "product": 5,
      "quantity": 2,
      "unit_price": 2990.00
    }
  ],
  "payment_method": "CASH",
  "total_amount": 5980.00
}
```

### 🛍️ Pedidos E-commerce (Orders)
- `GET /api/orders/` - Mis pedidos (e-commerce)
- `POST /api/orders/` - Crear pedido desde carrito
- `GET /api/orders/{id}/`
- `PUT /api/orders/{id}/` - Actualizar estado

**Estados de pedido:**
- `PENDING` - Pendiente de pago
- `PAID` - Pagado
- `SHIPPED` - Enviado
- `DELIVERED` - Entregado
- `CANCELLED` - Cancelado

**Ejemplo POST:**
```json
{
  "customer_name": "María González",
  "customer_email": "maria@gmail.com",
  "items": [
    {
      "product": 8,
      "quantity": 3,
      "unit_price": 4990.00
    }
  ],
  "shipping_address": "Los Aromos 234, Temuco",
  "total_amount": 14970.00,
  "status": "PENDING"
}
```

### 🛒 Carrito (CartItems)
- `GET /api/cart/` - Ver mi carrito
- `POST /api/cart/` - Agregar producto al carrito
- `DELETE /api/cart/{id}/` - Eliminar del carrito
- `DELETE /api/cart/clear/` - Vaciar carrito

**Ejemplo POST:**
```json
{
  "product": 5,
  "quantity": 2
}
```

---

## 📊 Reportes {#reportes}

### Reporte de Stock
```bash
GET /api/reports/stock/?branch=1
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "results": [
    {
      "product_id": 5,
      "product_name": "Paracetamol 500mg",
      "branch_name": "Sucursal Centro",
      "stock": 45,
      "reorder_point": 30,
      "needs_restock": false
    }
  ]
}
```

### Reporte de Ventas
```bash
GET /api/reports/sales/?start_date=2025-01-01&end_date=2025-01-31&branch=1
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "results": [
    {
      "date": "2025-01-15",
      "total_sales": 245890.00,
      "sales_count": 32,
      "branch_name": "Sucursal Centro"
    }
  ]
}
```

### Reporte de Proveedores
```bash
GET /api/reports/suppliers/
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "results": [
    {
      "supplier_id": 2,
      "supplier_name": "Distribuidora Farmacéutica S.A.",
      "total_purchases": 12,
      "total_amount": 4567890.00,
      "last_purchase_date": "2025-01-20"
    }
  ]
}
```

---

## 🧪 Ejemplos de Uso {#ejemplos}

### Flujo Completo de Venta POS

#### 1. Login y obtener token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"vendedor1","password":"password123"}'
```

#### 2. Verificar stock
```bash
curl -X GET "http://localhost:8000/api/inventory/?product=5" \
  -H "Authorization: Bearer <token>"
```

#### 3. Registrar venta
```bash
curl -X POST http://localhost:8000/api/sales/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": 1,
    "items": [
      {"product": 5, "quantity": 2, "unit_price": 2990.00}
    ],
    "payment_method": "CASH",
    "total_amount": 5980.00
  }'
```

### Flujo E-commerce

#### 1. Agregar al carrito (sin login)
```bash
curl -X POST http://localhost:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"product": 8, "quantity": 1}'
```

#### 2. Ver carrito
```bash
curl -X GET http://localhost:8000/api/cart/
```

#### 3. Crear pedido
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Ana López",
    "customer_email": "ana@gmail.com",
    "shipping_address": "Av. España 567, Temuco",
    "items": [
      {"product": 8, "quantity": 1, "unit_price": 4990.00}
    ],
    "total_amount": 4990.00
  }'
```

---

## 📚 Documentación Interactiva {#documentacion}

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **JSON Schema**: http://localhost:8000/swagger.json

Puedes probar todos los endpoints directamente desde Swagger UI.

---

## 🔑 Usuarios de Prueba

```
SUPER_ADMIN:
- username: admin
- password: admin123

ADMIN_CLIENTE:
- username: admin_farmacia
- password: farmacia123

GERENTE:
- username: gerente1
- password: gerente123

VENDEDOR:
- username: vendedor1
- password: vendedor123
```

---

## ⚠️ Validaciones Implementadas

1. **RUT Chileno**: Validación con dígito verificador
2. **Fechas**: `end_date >= start_date` en suscripciones
3. **Numéricos**: Stock, precios, cantidades >= 0
4. **Textos**: Longitud mínima/máxima en nombres, direcciones

---

## 🎨 Templates Frontend

### Públicas
- `/` - Landing page
- `/login/` - Login
- `/shop/` - Catálogo de productos
- `/shop/product/{id}/` - Detalle producto
- `/cart/` - Carrito de compras
- `/checkout/` - Finalizar compra

### Privadas (requieren login)
- `/dashboard/` - Dashboard por rol
- `/inventory/` - Gestión de inventario
- `/suppliers/` - Proveedores
- `/sales/` - Historial ventas POS
- `/reports/` - Reportes

---

## 🐛 Errores Comunes

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Solución**: Agregar header `Authorization: Bearer <token>`

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```
**Solución**: Tu rol no tiene permisos. Verifica que tu usuario tenga el rol correcto.

### 400 Bad Request (RUT inválido)
```json
{
  "rut": ["RUT inválido. Formato correcto: 12.345.678-9"]
}
```

---

## 📞 Soporte

Para más información, revisar:
- `DEPLOYMENT.md` - Guía de despliegue en AWS EC2
- `INICIO_RAPIDO.md` - Instalación local
- Admin Django: http://localhost:8000/admin/
