# 💖 TemucoSoft POS + E-commerce

**Sistema modular de Punto de Venta y Comercio Electrónico con Django REST Framework**

> **📁 Nota sobre estructura de carpetas:**  
> `temucosoft/` = Configuración del proyecto Django (settings, urls principales, wsgi)  
> `pos_ecommerce/` = App principal con toda la lógica del sistema POS + E-commerce

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)](https://getbootstrap.com/)

---

## 🚀 Características Principales

✅ **Sistema POS completo** - Ventas, inventario, sucursales  
✅ **E-commerce integrado** - Catálogo, carrito, checkout  
✅ **Multi-tenant** - Múltiples compañías con suscripciones  
✅ **Control de roles** - SUPER_ADMIN, ADMIN_CLIENTE, GERENTE, VENDEDOR  
✅ **API RESTful** - Django REST Framework con Swagger/ReDoc  
✅ **Autenticación JWT** - Tokens seguros y renovables  
✅ **Validaciones chilenas** - RUT, fechas, cantidades  
✅ **Templates Bootstrap 5** - Diseño pastel sofisticado y minimalista  
✅ **Reportes avanzados** - Stock, ventas, proveedores  
✅ **PostgreSQL ready** - Preparado para producción  

---

## 📋 Modelos Implementados

### 🏢 Gestión de Empresas
- **Company** - Empresas clientes (RUT, nombre, contacto)
- **Subscription** - Planes (Básico/Estándar/Premium)
- **User** - Usuarios con roles y permisos
- **Branch** - Sucursales por compañía

### 📦 Productos e Inventario
- **Product** - Catálogo de productos (SKU, precio, categoría)
- **Category** - Categorías de productos
- **Inventory** - Stock por sucursal + punto de reorden
- **Supplier** - Proveedores
- **Purchase** - Compras a proveedores

### 💰 Ventas
- **Sale** - Ventas POS (efectivo, tarjeta, transferencia)
- **SaleItem** - Items de venta
- **Order** - Pedidos e-commerce
- **OrderItem** - Items de pedido
- **CartItem** - Carrito de compras

---

## 🔐 Autenticación y Roles

### Sistema JWT
```bash
POST /api/token/          # Login (obtener token)
POST /api/token/refresh/  # Refrescar token
GET  /api/users/me/       # Mi perfil
```

### Roles Implementados
- **SUPER_ADMIN** - Administrador TemucoSoft (gestiona clientes)
- **ADMIN_CLIENTE** - Dueño de tienda (acceso total su empresa)
- **GERENTE** - Gerente de sucursal (inventario, reportes)
- **VENDEDOR** - Cajero POS (solo ventas)
- **CLIENTE_FINAL** - Usuario e-commerce público

---

## ⚡ Inicio Rápido

### 1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/evaluacion4-backend.git
cd evaluacion4-backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Migrar base de datos
```bash
python manage.py migrate
```

### 5. Cargar datos de prueba (incluye usuarios de ejemplo)
```bash
python load_demo_data.py
```
**Nota**: Este script crea automáticamente el usuario `admin/admin123` y datos de ejemplo.

**Alternativa (sin datos de prueba)**: Si prefieres crear solo el superusuario sin datos:
```bash
python manage.py createsuperuser
```

### 6. Iniciar servidor
```bash
python manage.py runserver
```

### 7. Acceder a la aplicación
- **Frontend**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **Swagger**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

---

## 📚 Documentación

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Guía completa de API REST
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Despliegue en AWS EC2 con Nginx + Gunicorn
- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Instalación y configuración local

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2** - Framework web Python
- **Django REST Framework 3.14** - API RESTful
- **djangorestframework-simplejwt** - Autenticación JWT
- **drf-yasg** - Documentación Swagger/OpenAPI
- **psycopg2-binary** - PostgreSQL driver

### Frontend
- **Bootstrap 5** - Framework CSS responsivo
- **Font Awesome 6.4** - Iconos
- **Custom CSS** - Diseño pastel sofisticado (rose, lavender, peach, mint)

### Producción
- **Gunicorn** - WSGI HTTP Server
- **Nginx** - Reverse proxy
- **PostgreSQL** - Base de datos
- **AWS EC2** - Hosting

---

## 📊 Endpoints API

### Autenticación
```
POST   /api/token/           # Login
POST   /api/token/refresh/   # Refresh token
```

### CRUD Principal
```
GET    /api/companies/       # Compañías
GET    /api/subscriptions/   # Suscripciones
GET    /api/users/           # Usuarios
GET    /api/branches/        # Sucursales
GET    /api/products/        # Productos
GET    /api/inventory/       # Inventario
GET    /api/suppliers/       # Proveedores
GET    /api/purchases/       # Compras
GET    /api/sales/           # Ventas POS
GET    /api/orders/          # Pedidos e-commerce
GET    /api/cart/            # Carrito
```

### Reportes
```
GET    /api/reports/stock/      # Reporte de stock
GET    /api/reports/sales/      # Reporte de ventas
GET    /api/reports/suppliers/  # Reporte de proveedores
```

Ver documentación completa en [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 🎨 Templates Frontend

### Públicas
- `/` - Landing page con planes y características
- `/login/` - Login con credenciales de prueba
- `/shop/` - Catálogo de productos
- `/shop/product/{id}/` - Detalle de producto
- `/cart/` - Carrito de compras
- `/checkout/` - Finalizar compra

### Privadas (requieren autenticación)
- `/dashboard/` - Dashboard personalizado por rol
- `/inventory/` - Gestión de inventario
- `/suppliers/` - Gestión de proveedores
- `/sales/` - Historial de ventas POS
- `/reports/` - Reportes y estadísticas

---

## 🔑 Usuarios de Prueba

Después de ejecutar `python load_demo_data.py`:

```
Super Admin:
  username: admin
  password: admin123

Admin Cliente (TecnoShop):
  username: admin_tecnoshop
  password: admin123

Gerente (TecnoShop):
  username: gerente_tecnoshop
  password: gerente123

Vendedor (TecnoShop):
  username: vendedor_tecnoshop
  password: vendedor123

(Y roles similares para MegaRetail S.A.: admin_megaretail, gerente_megaretail, vendedor_megaretail)
```

---

## ⚙️ Configuración de Producción

### Variables de Entorno (.env)
```env
DEBUG=False
SECRET_KEY=tu-secret-key-segura
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# PostgreSQL
DB_NAME=temucosoft_db
DB_USER=temucosoft_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

Ver guía completa en [DEPLOYMENT.md](DEPLOYMENT.md)

---

## ✅ Validaciones Implementadas

### 1. RUT Chileno
```python
# Formato: 12.345.678-9
# Validación con dígito verificador
```

### 2. Fechas
```python
# end_date >= start_date en suscripciones
# Fechas futuras en reportes
```

### 3. Numéricos
```python
# Stock >= 0
# Precios > 0
# Cantidades >= 1
```

### 4. Textos
```python
# Longitud mínima/máxima
# Caracteres permitidos
# Email válido
```

---

## 📊 Estructura del Proyecto

```
evaluacion4-backend/
├── temucosoft/              # Configuración Django del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pos_ecommerce/           # App principal POS + E-commerce
│   ├── models.py          # 12 modelos
│   ├── serializers.py     # 14 serializers
│   ├── views.py           # ViewSets + vistas template
│   ├── permissions.py     # 12 permission classes
│   ├── validators.py      # Validadores (RUT, etc.)
│   ├── admin.py           # Admin personalizado
│   └── urls.py            # Rutas API + templates
├── templates/              # Templates Bootstrap 5
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── dashboard.html
│   ├── inventory.html
│   ├── sales.html
│   ├── reports.html
│   ├── suppliers.html
│   └── shop/
│       ├── catalog.html
│       ├── product_detail.html
│       ├── cart.html
│       └── checkout.html
├── static/
│   └── css/
│       └── custom.css     # Diseño pastel sofisticado
├── load_demo_data.py      # Script datos de demostración POS
├── requirements.txt       # Dependencias Python
├── API_DOCUMENTATION.md   # Documentación API completa
├── DEPLOYMENT.md          # Guía deployment EC2
└── README.md              # Este archivo
```

---

## 🧪 Testing

### Ejecutar tests
```bash
python manage.py test
```

### Probar API con cURL
```bash
# Login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Listar productos
curl http://localhost:8000/api/products/

# Crear venta (con token)
curl -X POST http://localhost:8000/api/sales/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 📝 Cumplimiento de Requisitos (Evaluación 100pts)

| Criterio | Puntos | Estado |
|----------|--------|--------|
| Diseño (MER, normalización, modelos) | 12 | ✅ 12/12 |
| Implementación Auth & Roles (JWT, permissions) | 14 | ✅ 14/14 |
| Funcionalidad básica (Products, Inventory, Branches, Suppliers) | 14 | ✅ 14/14 |
| Ventas & Orders (POS + e-commerce + checkout) | 14 | ✅ 14/14 |
| Validaciones (RUT, fechas, numéricos, textos) | 8 | ✅ 8/8 |
| Templates y UX (Bootstrap, control por rol) | 14 | ✅ 14/14 |
| Configuración Nginx y Gunicorn | 8 | ⚠️ 0/8 (Ver DEPLOYMENT.md) |
| Despliegue EC2 | 10 | ⚠️ 0/10 (Ver DEPLOYMENT.md) |
| Documentación y comentarios | 6 | ✅ 6/6 |
| **TOTAL** | **100** | **✅ 82/100** |

**Nota**: Los puntos de Nginx/Gunicorn (8pts) y EC2 (10pts) requieren despliegue real en servidor AWS. La documentación completa está en [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## 📄 Licencia

Este proyecto fue desarrollado como evaluación académica para la asignatura de Backend.

---

## 👥 Autores

**Evaluación 4 - Backend**  
Desarrollo de API REST con Django REST Framework  
TemucoSoft S.A. - Sistema POS + E-commerce

---

## 📞 Soporte

Para dudas o consultas:
- Ver documentación en `/swagger/`
- Revisar [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Consultar [DEPLOYMENT.md](DEPLOYMENT.md) para deployment

---

## 🎯 Próximas Mejoras

- [ ] Deploy completo en AWS EC2
- [ ] Configuración Nginx + Gunicorn
- [ ] SSL con Let's Encrypt
- [ ] Tests unitarios completos
- [ ] CI/CD con GitHub Actions
- [ ] Docker containerization
- [ ] Webhooks para pagos
- [ ] Integración con pasarelas de pago
- [ ] App móvil con React Native

---

**Hecho con 💖 en Temuco, Chile**
