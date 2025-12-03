#!/bin/bash
# =============================================================================
# Script de Despliegue para TemucoSoft POS en AWS EC2
# Evaluación 4 - Backend Django REST Framework
#
# Uso: 
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Ejecutar como usuario ubuntu en EC2 Ubuntu 22.04
# =============================================================================

set -e  # Detener en caso de error

echo "🚀 =============================================="
echo "   TemucoSoft POS - Script de Despliegue EC2"
echo "================================================"

# =============================================================================
# 1. ACTUALIZAR SISTEMA
# =============================================================================
echo ""
echo "📦 [1/10] Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# =============================================================================
# 2. INSTALAR DEPENDENCIAS DEL SISTEMA
# =============================================================================
echo ""
echo "📦 [2/10] Instalando dependencias del sistema..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    supervisor

# =============================================================================
# 3. CONFIGURAR POSTGRESQL
# =============================================================================
echo ""
echo "🐘 [3/10] Configurando PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear base de datos y usuario
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS temucosoft_db;
DROP USER IF EXISTS temucosoft_user;
CREATE USER temucosoft_user WITH PASSWORD 'TemucoSoft2024!';
CREATE DATABASE temucosoft_db OWNER temucosoft_user;
ALTER ROLE temucosoft_user SET client_encoding TO 'utf8';
ALTER ROLE temucosoft_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE temucosoft_user SET timezone TO 'America/Santiago';
GRANT ALL PRIVILEGES ON DATABASE temucosoft_db TO temucosoft_user;
EOF

echo "✅ PostgreSQL configurado"

# =============================================================================
# 4. CLONAR/ACTUALIZAR PROYECTO
# =============================================================================
echo ""
echo "📂 [4/10] Configurando proyecto..."
cd /home/ubuntu

# Si ya existe, actualizar; si no, clonar
if [ -d "evaluacion4-backend" ]; then
    echo "Actualizando proyecto existente..."
    cd evaluacion4-backend
    git pull origin main || git pull origin master
else
    echo "⚠️ NOTA: Debes copiar el proyecto manualmente o clonar desde GitHub"
    echo "   Ejemplo: git clone https://github.com/tu-usuario/evaluacion4-backend.git"
    echo "   O copiar con SCP desde tu máquina local"
    mkdir -p evaluacion4-backend
    cd evaluacion4-backend
fi

# =============================================================================
# 5. CREAR ENTORNO VIRTUAL E INSTALAR DEPENDENCIAS
# =============================================================================
echo ""
echo "🐍 [5/10] Configurando entorno Python..."
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# =============================================================================
# 6. CONFIGURAR VARIABLES DE ENTORNO
# =============================================================================
echo ""
echo "⚙️ [6/10] Configurando variables de entorno..."

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
cat > .env <<EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=temucosoft_db
DB_USER=temucosoft_user
DB_PASSWORD=TemucoSoft2024!
DB_HOST=localhost
DB_PORT=5432
EOF
fi

# Exportar variables
export $(cat .env | xargs)
export DJANGO_SETTINGS_MODULE=temucosoft.settings_production

# =============================================================================
# 7. MIGRAR BASE DE DATOS Y CARGAR DATOS
# =============================================================================
echo ""
echo "📊 [7/10] Migrando base de datos..."
python manage.py migrate --settings=temucosoft.settings_production

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --settings=temucosoft.settings_production

# Cargar datos de demostración
echo "📋 Cargando datos de demostración..."
python load_demo_data.py || echo "⚠️ load_demo_data.py no encontrado o ya ejecutado"

# =============================================================================
# 8. CONFIGURAR GUNICORN SERVICE
# =============================================================================
echo ""
echo "🦄 [8/10] Configurando Gunicorn..."

# Crear directorios de logs
sudo mkdir -p /var/log/gunicorn
sudo chown -R ubuntu:ubuntu /var/log/gunicorn

sudo mkdir -p /var/run/gunicorn
sudo chown -R ubuntu:ubuntu /var/run/gunicorn

sudo mkdir -p /var/log/django
sudo chown -R ubuntu:ubuntu /var/log/django

# Copiar archivo de servicio
sudo cp gunicorn.service /etc/systemd/system/gunicorn.service

# Recargar systemd
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo "✅ Gunicorn configurado"

# =============================================================================
# 9. CONFIGURAR NGINX
# =============================================================================
echo ""
echo "🌐 [9/10] Configurando Nginx..."

# Obtener IP pública de EC2
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "localhost")

# Actualizar configuración de Nginx con la IP
sed "s/CAMBIAR_POR_IP_EC2/$PUBLIC_IP/g" nginx.conf > /tmp/nginx_temucosoft.conf

# Copiar configuración
sudo cp /tmp/nginx_temucosoft.conf /etc/nginx/sites-available/temucosoft

# Crear enlace simbólico
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/temucosoft /etc/nginx/sites-enabled/

# Configurar permisos
sudo usermod -a -G ubuntu www-data
chmod 710 /home/ubuntu
chmod -R 755 /home/ubuntu/evaluacion4-backend/staticfiles 2>/dev/null || true

# Verificar y reiniciar Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Nginx configurado"

# =============================================================================
# 10. VERIFICAR SERVICIOS
# =============================================================================
echo ""
echo "✅ [10/10] Verificando servicios..."

echo ""
echo "Estado de PostgreSQL:"
sudo systemctl status postgresql --no-pager -l | head -5

echo ""
echo "Estado de Gunicorn:"
sudo systemctl status gunicorn --no-pager -l | head -5

echo ""
echo "Estado de Nginx:"
sudo systemctl status nginx --no-pager -l | head -5

# =============================================================================
# RESUMEN FINAL
# =============================================================================
echo ""
echo "🎉 =============================================="
echo "   ¡DESPLIEGUE COMPLETADO!"
echo "================================================"
echo ""
echo "📍 Accede a la aplicación:"
echo "   http://$PUBLIC_IP/"
echo ""
echo "📍 API Documentation:"
echo "   http://$PUBLIC_IP/swagger/"
echo "   http://$PUBLIC_IP/redoc/"
echo ""
echo "📍 Admin Django:"
echo "   http://$PUBLIC_IP/admin/"
echo ""
echo "🔑 Usuarios de prueba:"
echo "   admin / admin123 (Super Admin)"
echo "   admin_tecnoshop / admin123 (Admin Cliente)"
echo "   vendedor_tecnoshop / vendedor123 (Vendedor)"
echo ""
echo "📋 Comandos útiles:"
echo "   sudo systemctl restart gunicorn"
echo "   sudo systemctl restart nginx"
echo "   sudo journalctl -u gunicorn -f"
echo "   sudo tail -f /var/log/nginx/temucosoft_error.log"
echo ""
echo "================================================"
