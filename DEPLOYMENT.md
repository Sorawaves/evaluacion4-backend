# 🚀 Guía de Despliegue en AWS EC2

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos)
2. [Configuración EC2](#ec2)
3. [Instalación de Dependencias](#dependencias)
4. [PostgreSQL](#postgresql)
5. [Configuración Gunicorn](#gunicorn)
6. [Configuración Nginx](#nginx)
7. [SSL con Let's Encrypt](#ssl)
8. [Verificación](#verificacion)

---

## ✅ Requisitos Previos {#requisitos}

- Cuenta AWS con acceso a EC2
- Instancia EC2 (recomendado: t2.small o superior)
- Sistema operativo: Ubuntu 22.04 LTS
- Dominio configurado (opcional para SSL)

---

## 🖥️ Configuración EC2 {#ec2}

### 1. Crear instancia EC2

```bash
# En AWS Console:
1. Launch Instance
2. Seleccionar Ubuntu Server 22.04 LTS
3. Tipo: t2.small (1 vCPU, 2 GB RAM)
4. Security Group:
   - SSH (22) - Tu IP
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
   - Custom TCP (8000) - 0.0.0.0/0 (solo desarrollo)
5. Crear par de claves (.pem)
6. Launch
```

### 2. Conectar a la instancia

```bash
chmod 400 tu-key.pem
ssh -i "tu-key.pem" ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com
```

---

## 📦 Instalación de Dependencias {#dependencias}

### 1. Actualizar sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Python y herramientas

```bash
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y libpq-dev postgresql postgresql-contrib
sudo apt install -y nginx curl git
```

### 3. Clonar proyecto

```bash
cd /home/ubuntu
git clone https://github.com/tu-usuario/evaluacion4-backend.git
cd evaluacion4-backend
```

### 4. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

---

## 🐘 PostgreSQL {#postgresql}

### 1. Configurar base de datos

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE temucosoft_db;
CREATE USER temucosoft_user WITH PASSWORD 'tu_password_seguro';
ALTER ROLE temucosoft_user SET client_encoding TO 'utf8';
ALTER ROLE temucosoft_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE temucosoft_user SET timezone TO 'America/Santiago';
GRANT ALL PRIVILEGES ON DATABASE temucosoft_db TO temucosoft_user;
\q
```

### 2. Configurar Django para PostgreSQL

Editar el archivo de configuración `temucosoft/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'temucosoft_db',
        'USER': 'temucosoft_user',
        'PASSWORD': 'tu_password_seguro',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configuración de producción
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'ec2-XX-XX-XX-XX.compute-1.amazonaws.com']

# Archivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')
STATIC_URL = '/static/'

# Variables de entorno (recomendado usar python-decouple)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'tu-secret-key-aqui')
```

### 3. Migrar base de datos

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Cargar datos de prueba (opcional)

```bash
python load_demo_data.py
```

---

## 🦄 Configuración Gunicorn {#gunicorn}

### 1. Crear archivo de configuración Gunicorn

`/home/ubuntu/evaluacion4-backend/gunicorn_config.py`:

```python
import multiprocessing

# Bind
bind = "0.0.0.0:8000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "temucosoft_pos"

# Daemon
daemon = False
pidfile = "/var/run/gunicorn.pid"
```

### 2. Crear directorio de logs

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown -R ubuntu:ubuntu /var/log/gunicorn
```

### 3. Crear servicio systemd para Gunicorn

`/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for TemucoSoft POS
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/evaluacion4-backend
Environment="PATH=/home/ubuntu/evaluacion4-backend/venv/bin"
ExecStart=/home/ubuntu/evaluacion4-backend/venv/bin/gunicorn \
          --config /home/ubuntu/evaluacion4-backend/gunicorn_config.py \
          temucosoft.wsgi:application  # WSGI del proyecto Django

[Install]
WantedBy=multi-user.target
```

### 4. Activar y arrancar Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

### 5. Verificar logs

```bash
sudo journalctl -u gunicorn -f
tail -f /var/log/gunicorn/error.log
```

---

## 🌐 Configuración Nginx {#nginx}

### 1. Crear configuración de sitio

`/etc/nginx/sites-available/temucosoft`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com ec2-XX-XX-XX-XX.compute-1.amazonaws.com;

    client_max_body_size 20M;

    # Archivos estáticos
    location /static/ {
        alias /home/ubuntu/evaluacion4-backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Archivos de media
    location /media/ {
        alias /home/ubuntu/evaluacion4-backend/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Proxy a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
}
```

### 2. Activar sitio

```bash
sudo ln -s /etc/nginx/sites-available/temucosoft /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Eliminar sitio default
sudo nginx -t  # Verificar sintaxis
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3. Configurar permisos

```bash
sudo usermod -a -G ubuntu www-data
chmod 710 /home/ubuntu
chmod -R 755 /home/ubuntu/evaluacion4-backend/staticfiles
```

---

## 🔒 SSL con Let's Encrypt {#ssl}

### 1. Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtener certificado

```bash
sudo certbot --nginx -d tu-dominio.com
```

### 3. Renovación automática

```bash
sudo certbot renew --dry-run
sudo systemctl status certbot.timer
```

---

## ✅ Verificación {#verificacion}

### 1. Verificar servicios

```bash
# PostgreSQL
sudo systemctl status postgresql

# Gunicorn
sudo systemctl status gunicorn

# Nginx
sudo systemctl status nginx
```

### 2. Verificar logs

```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 3. Probar endpoints

```bash
# Health check
curl http://tu-dominio.com/

# API
curl http://tu-dominio.com/api/products/

# Swagger
curl http://tu-dominio.com/swagger/

# Admin
curl http://tu-dominio.com/admin/
```

### 4. Verificar conectividad PostgreSQL

```bash
psql -U temucosoft_user -d temucosoft_db -h localhost
\dt  # Listar tablas
\q
```

---

## 🔄 Comandos Útiles

### Reiniciar servicios

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Ver logs en tiempo real

```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Actualizar código

```bash
cd /home/ubuntu/evaluacion4-backend
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## 🐛 Troubleshooting

### Error: Bad Gateway 502

```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status gunicorn
sudo systemctl restart gunicorn

# Verificar logs
sudo journalctl -u gunicorn -n 50
```

### Error: Permission Denied

```bash
# Verificar permisos
ls -la /home/ubuntu/evaluacion4-backend/staticfiles
sudo chmod -R 755 /home/ubuntu/evaluacion4-backend/staticfiles
sudo chown -R ubuntu:www-data /home/ubuntu/evaluacion4-backend
```

### Error: Database Connection

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# Verificar credenciales en settings.py
```

### Error: Static Files Not Loading

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Verificar configuración Nginx
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 Monitoreo

### Instalar herramientas de monitoreo (opcional)

```bash
# htop para monitorear recursos
sudo apt install -y htop

# netstat para conexiones
sudo apt install -y net-tools

# Verificar uso de recursos
htop
free -h
df -h
```

---

## 🔐 Seguridad

### Firewall UFW

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### Fail2Ban (protección contra ataques)

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📝 Checklist de Deployment

- [ ] Instancia EC2 creada y configurada
- [ ] PostgreSQL instalado y configurado
- [ ] Código clonado y dependencias instaladas
- [ ] Migraciones aplicadas
- [ ] Superusuario creado
- [ ] Archivos estáticos recolectados
- [ ] Gunicorn configurado como servicio
- [ ] Nginx configurado y corriendo
- [ ] SSL configurado (si aplica)
- [ ] Firewall configurado
- [ ] Variables de entorno configuradas
- [ ] DEBUG = False en settings.py
- [ ] ALLOWED_HOSTS configurado
- [ ] SECRET_KEY en variable de entorno
- [ ] Logs funcionando correctamente

---

## 📞 Contacto y Soporte

Para más información:
- Documentación API: `/swagger/`
- Admin Django: `/admin/`
- Logs: `/var/log/gunicorn/`, `/var/log/nginx/`
