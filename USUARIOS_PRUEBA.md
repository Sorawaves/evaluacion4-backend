# 📋 USUARIOS DE PRUEBA Y SUS CONFIGURACIONES

## 🔑 1. SUPER ADMIN

- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Email:** admin@temucosoft.cl
- **RUT:** 11111111-1
- **Rol:** SUPER_ADMIN
- **Empresa:** Ninguna (acceso a todas)

### Permisos:
- ✅ Gestión de todas las empresas
- ✅ Gestión de suscripciones
- ✅ Creación de usuarios para cualquier empresa
- ✅ Acceso total al Admin Django
- ✅ Acceso completo a la API
- ✅ Ver todos los reportes

---

## 🏢 2. EMPRESA: TecnoShop Ltda. (76543210-5)

**Plan:** Estándar

### 👔 Admin Cliente

- **Usuario:** `admin_tecnoshop`
- **Contraseña:** `admin123`
- **Email:** admin@tecnoshop.cl
- **RUT:** 22000001-1
- **Rol:** ADMIN_CLIENTE

#### Permisos:
- ✅ Gestión de productos
- ✅ Gestión de proveedores
- ✅ Gestión de sucursales (hasta 3)
- ✅ Gestión de inventario
- ✅ Ver suscripción
- ✅ Ver reportes
- ✅ Crear usuarios (hasta 5)
- ✅ Acceso a API

### 📊 Gerente

- **Usuario:** `gerente_tecnoshop`
- **Contraseña:** `gerente123`
- **Email:** gerente@tecnoshop.cl
- **RUT:** 33000001-1
- **Rol:** GERENTE

#### Permisos:
- ✅ Gestión de productos
- ✅ Gestión de proveedores
- ✅ Gestión de inventario
- ✅ Ver reportes
- ✅ Crear compras
- ❌ No puede crear usuarios
- ❌ No puede ver suscripción

### 🛒 Vendedor

- **Usuario:** `vendedor_tecnoshop`
- **Contraseña:** `vendedor123`
- **Email:** vendedor@tecnoshop.cl
- **RUT:** 44000001-1
- **Rol:** VENDEDOR

#### Permisos:
- ✅ POS (Punto de Venta)
- ✅ Ver productos
- ✅ Ver carrito de compras
- ❌ No puede gestionar inventario
- ❌ No puede ver reportes
- ❌ No puede crear compras

### 📦 Plan Estándar incluye:

- 3 sucursales máximo
- 5 usuarios máximo
- Acceso a API REST
- Reportes avanzados
- **Precio:** $19.990/mes

---

## 🏢 3. EMPRESA: MegaRetail S.A. (78901234-7)

**Plan:** Premium

### 👔 Admin Cliente

- **Usuario:** `admin_megaretail`
- **Contraseña:** `admin123`
- **Email:** admin@megaretail.cl
- **RUT:** 22000002-2
- **Rol:** ADMIN_CLIENTE
- **Permisos:** (Iguales que TecnoShop pero con límites del plan Premium)

### 📊 Gerente

- **Usuario:** `gerente_megaretail`
- **Contraseña:** `gerente123`
- **Email:** gerente@megaretail.cl
- **RUT:** 33000002-2
- **Rol:** GERENTE

### 🛒 Vendedor

- **Usuario:** `vendedor_megaretail`
- **Contraseña:** `vendedor123`
- **Email:** vendedor@megaretail.cl
- **RUT:** 44000002-2
- **Rol:** VENDEDOR

### 🌟 Plan Premium incluye:

- ♾️ Sucursales ilimitadas
- ♾️ Usuarios ilimitados
- ✅ Acceso a API REST
- ✅ Reportes avanzados
- ✅ Soporte 24/7
- **Precio:** $39.990/mes

---

## 📊 COMPARACIÓN DE PLANES

| Característica | Básico   |   Estándar | Premium |
|----------------|----------|------------|---------|
| **Precio**     |$9.990/mes | $19.990/mes | $39.990/mes |
| **Sucursales**  |   1    |     3     |   Ilimitadas  |
| **Productos**   |   100   |   500    |   Ilimitados  |
| **Usuarios**    |    2    |     5    |   Ilimitados  |
| **API REST**    |   ❌   |    ✅    |      ✅      |
| **Reportes**    |   ❌   |    ✅    |      ✅      |
| **Soporte**     | Email   |Prioritario|    24/7     |

---

## 🎯 ACCESOS RÁPIDOS

- **Login:** http://127.0.0.1:8000/login/
- **Dashboard:** http://127.0.0.1:8000/dashboard/
- **Admin Django:** http://127.0.0.1:8000/admin/
- **API REST:** http://127.0.0.1:8000/api/
- **Documentación API:** http://127.0.0.1:8000/swagger/
- **Catálogo Tienda:** http://127.0.0.1:8000/shop/

---

## 🚀 INICIO RÁPIDO

### 1. Cargar datos de prueba

```bash
python load_demo_data.py
```

### 2. Iniciar servidor

```bash
python manage.py runserver
```

### 3. Acceder al sistema

Visita http://127.0.0.1:8000/login/ y usa cualquiera de las credenciales listadas arriba.

---

## 📝 NOTAS IMPORTANTES

- Todos los usuarios tienen contraseñas simples para **propósitos de prueba únicamente**
- En producción, se deben usar contraseñas seguras y cambiarlas regularmente
- Los RUTs son ficticios y generados automáticamente
- Las empresas tienen datos de prueba incluyendo:
  - 2 sucursales por empresa
  - 20 productos por empresa
  - 3 proveedores por empresa
  - Inventario inicial de 100 unidades por producto
  - Compras y ventas de ejemplo

---

## 🔐 SEGURIDAD

**⚠️ ADVERTENCIA:** Estas credenciales son solo para desarrollo y testing. 

En un entorno de producción:
- Cambiar todas las contraseñas
- Implementar autenticación de dos factores
- Configurar políticas de contraseñas fuertes
- Habilitar HTTPS/SSL
- Configurar variables de entorno para credenciales sensibles
