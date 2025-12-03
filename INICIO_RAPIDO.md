# 🚀 INICIO RÁPIDO - 5 Pasos

## 1️⃣ Crear y activar entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2️⃣ Instalar dependencias

```powershell
pip install -r requirements.txt
```

## 3️⃣ Crear base de datos

```powershell
python manage.py migrate
```

## 4️⃣ Cargar datos de ejemplo

```powershell
python load_demo_data.py
```

## 5️⃣ Iniciar servidor

```powershell
python manage.py runserver
```

---

## 📍 URLs Importantes

- **Homepage**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **Swagger**: http://localhost:8000/swagger/
- **API**: http://localhost:8000/api/

---

## 🔑 Credenciales

**Usuario**: `admin`  
**Contraseña**: `admin123`

---

## 📚 Documentación Completa

Lee los siguientes archivos para más información:

- `README.md` - Documentación principal
- `API_DOCUMENTATION.md` - Guía completa de la API
- `DEPLOYMENT.md` - Deployment en AWS EC2
- `PROYECTO_COMPLETADO.md` - Verificación de cumplimiento
- `INDICE.md` - Índice de toda la documentación

---

**¡Listo! Tu proyecto Django REST Framework está funcionando** 🎉
