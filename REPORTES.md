# 📊 Reportes del Sistema

## Descripción General

El sistema TemucoSoft POS + E-commerce ahora incluye **reportes HTML completos** con visualización profesional, filtros interactivos y capacidad de impresión.

## Reportes Disponibles

### 1. 📦 Reporte de Stock por Sucursal
**URL:** `/reportes/stock/`

**Características:**
- Vista completa del inventario por sucursal
- Indicadores de productos que requieren restock
- Filtros por sucursal y categoría
- Información de último restock
- Exportación a impresión

**Información mostrada:**
- Sucursal
- Producto (nombre y SKU)
- Categoría
- Stock actual
- Punto de reorden
- Estado (OK / Requiere Restock)
- Fecha del último restock

**Acceso:** Usuarios con rol ADMIN_CLIENTE, GERENTE o SUPER_ADMIN

---

### 2. 💰 Reporte de Ventas
**URL:** `/reportes/ventas/`

**Características:**
- Estadísticas generales (total ventas, monto total)
- Ventas agrupadas por día
- Detalle de las últimas 50 ventas
- Filtros por sucursal y rango de fechas
- Promedio por venta
- Exportación a impresión

**Información mostrada:**
- Resumen: Total de ventas y monto total
- Por día: Cantidad y total vendido
- Detalle: ID, fecha, sucursal, vendedor, método de pago, total

**Acceso:** Usuarios con rol ADMIN_CLIENTE, GERENTE o SUPER_ADMIN

---

### 3. 🚚 Reporte de Proveedores
**URL:** `/reportes/proveedores/`

**Características:**
- Listado completo de proveedores
- Estadísticas de compras por proveedor
- Historial de últimas 5 compras
- Información de contacto
- Estado (Activo/Inactivo)
- Exportación a impresión

**Información mostrada:**
- Datos del proveedor (RUT, nombre, contacto)
- Total de compras realizadas
- Monto total de compras
- Últimas compras (ID, fecha, total, sucursal)

**Acceso:** Usuarios con rol ADMIN_CLIENTE, GERENTE o SUPER_ADMIN

---

### 4. 🔄 Reporte de Movimientos de Inventario
**URL:** `/reportes/movimientos/`

**Características:**
- Historial de movimientos de stock
- Resumen por tipo de movimiento
- Filtros por tipo y rango de fechas
- Últimos 100 movimientos
- Indicadores visuales (entradas en verde, salidas en rojo)
- Exportación a impresión

**Tipos de movimiento:**
- COMPRA - Ingreso por compra a proveedor
- VENTA - Salida por venta
- AJUSTE_POSITIVO - Ajuste manual positivo
- AJUSTE_NEGATIVO - Ajuste manual negativo
- DEVOLUCION - Devolución de producto
- TRANSFERENCIA_IN - Transferencia entrada
- TRANSFERENCIA_OUT - Transferencia salida

**Información mostrada:**
- Fecha y hora
- Tipo de movimiento
- Producto y sucursal
- Cantidad (+ o -)
- Stock anterior y nuevo
- Usuario responsable
- Notas adicionales

**Acceso:** Usuarios con rol ADMIN_CLIENTE, GERENTE o SUPER_ADMIN

---

## Acceso a los Reportes

### Desde el Dashboard
Los reportes son accesibles desde la sección "Reportes" en el menú principal cuando estás autenticado con los roles adecuados.

### Desde la Página de Reportes
**URL:** `/reportes/`

Esta página muestra un resumen con:
- Stock bajo (productos que necesitan restock)
- Ventas del mes (cantidad y monto total)
- Proveedores activos
- Movimientos de inventario recientes

Desde aquí puedes acceder a cada reporte completo mediante botones.

---

## Características Técnicas

### Diseño Responsivo
- Diseño adaptativo para desktop, tablet y móvil
- Tablas con scroll horizontal en pantallas pequeñas
- Interfaz Bootstrap 5 con tema pastel personalizado

### Impresión
- Botón de impresión en cada reporte
- CSS optimizado para impresión (oculta elementos innecesarios)
- Layout limpio para documentos impresos

### Filtros
- Filtros GET para personalizar los reportes
- Botón de limpiar filtros
- URLs con parámetros para compartir vistas filtradas

### Rendimiento
- Consultas optimizadas con `select_related`
- Límites de registros para evitar sobrecarga
- Agregaciones en base de datos

---

## Diferencia con API REST

### Antes (JSON)
```
GET /api/reportes/stock/
→ Devuelve JSON puro
```

### Ahora (HTML)
```
GET /reportes/stock/
→ Devuelve vista HTML completa con tablas, gráficos y filtros
```

Los endpoints de la API REST (`/api/...`) siguen disponibles para integraciones externas y consumo programático.

---

## Seguridad

- **Autenticación requerida** - Todos los reportes requieren login
- **Control de acceso** - Solo usuarios con roles ADMIN_CLIENTE, GERENTE o SUPER_ADMIN
- **Filtrado por empresa** - Los usuarios solo ven datos de su propia empresa (excepto SUPER_ADMIN)
- **Validación de permisos** - Decorador `@login_required` en todas las vistas

---

## Próximas Mejoras Sugeridas

- [ ] Gráficos interactivos con Chart.js
- [ ] Exportación a PDF
- [ ] Exportación a Excel
- [ ] Reportes programados por email
- [ ] Dashboard con KPIs en tiempo real
- [ ] Comparativas mes a mes
- [ ] Reportes de rentabilidad por producto
- [ ] Análisis de tendencias de ventas

---

## Ejemplos de Uso

### Ver stock bajo en una sucursal específica
```
/reportes/stock/?branch=1
```

### Ver ventas del último mes
```
/reportes/ventas/?date_from=2025-11-01&date_to=2025-11-30
```

### Ver solo movimientos de compras
```
/reportes/movimientos/?tipo=COMPRA
```

---

**Documentación actualizada:** Diciembre 2025  
**Sistema:** TemucoSoft POS + E-commerce v1.0
