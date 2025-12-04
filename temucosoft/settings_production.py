"""
Configuración de producción para Django.
Evaluación 4 - Backend Django REST Framework.

USO: En EC2, configurar variable de entorno:
    export DJANGO_SETTINGS_MODULE=temucosoft.settings_production
    
O usar directamente:
    gunicorn --env DJANGO_SETTINGS_MODULE=temucosoft.settings_production temucosoft.wsgi:application
"""

# Importar configuración base
from .settings import *
import os

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD PARA PRODUCCIÓN
# =============================================================================

# ¡IMPORTANTE! Cambiar a False en producción
DEBUG = False

# Dominios permitidos - IP PÚBLICA DE EC2
ALLOWED_HOSTS = ['3.90.33.82', 'localhost', '127.0.0.1']

# CSRF Origins
CSRF_TRUSTED_ORIGINS = ['http://3.90.33.82']

# Clave secreta - usar variable de entorno en producción
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'cambiar-esta-clave-en-produccion-muy-importante')

# =============================================================================
# BASE DE DATOS POSTGRESQL
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'temucosoft_db'),
        'USER': os.environ.get('DB_USER', 'temucosoft_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'temuco2025'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# =============================================================================
# ARCHIVOS ESTÁTICOS
# =============================================================================

# Directorio donde collectstatic guardará los archivos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Archivos de media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# =============================================================================
# SEGURIDAD HTTPS/SSL
# =============================================================================

# Activar cuando tengas SSL configurado
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'
# SECURE_HSTS_SECONDS = 31536000  # 1 año
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Proxy de Nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# =============================================================================
# CORS - Orígenes permitidos
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    # CAMBIAR: Agregar dominios permitidos
    # "https://tu-dominio.com",
]

# =============================================================================
# LOGGING - Configuración de logs
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/temucosoft.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'pos_ecommerce': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# CACHE (Opcional - Redis)
# =============================================================================

# Si tienes Redis instalado:
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }

# Cache en memoria (simple, para empezar)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# =============================================================================
# EMAIL (Opcional - para notificaciones)
# =============================================================================

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

# =============================================================================
# CONFIGURACIÓN JWT PARA PRODUCCIÓN
# =============================================================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # Más corto en producción
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=12),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

print("✅ Configuración de PRODUCCIÓN cargada")
