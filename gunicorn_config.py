"""
Configuración de Gunicorn para producción.
Evaluación 4 - Backend Django REST Framework.

Uso:
    gunicorn -c gunicorn_config.py temucosoft.wsgi:application
"""
import multiprocessing

# =============================================================================
# BINDING - Dirección y puerto donde escucha Gunicorn
# =============================================================================
bind = "0.0.0.0:8000"  # Escucha en todas las interfaces, puerto 8000

# =============================================================================
# WORKERS - Procesos de trabajo para manejar peticiones
# =============================================================================
# Fórmula recomendada: (2 x CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Tipo de worker (sync es el estándar)
worker_class = "sync"

# Conexiones máximas por worker
worker_connections = 1000

# Timeout para requests (segundos)
timeout = 30

# Tiempo de keep-alive (segundos)
keepalive = 2

# Threads por worker (para worker_class = gthread)
threads = 1

# =============================================================================
# LOGGING - Configuración de logs
# =============================================================================
# Archivo de log de acceso
accesslog = "/var/log/gunicorn/access.log"

# Archivo de log de errores
errorlog = "/var/log/gunicorn/error.log"

# Nivel de log: debug, info, warning, error, critical
loglevel = "info"

# Formato de log de acceso
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# =============================================================================
# PROCESS NAMING - Nombre del proceso
# =============================================================================
proc_name = "temucosoft_pos"

# =============================================================================
# SERVER MECHANICS - Configuración del servidor
# =============================================================================
# No ejecutar en modo daemon (systemd lo maneja)
daemon = False

# Archivo PID
pidfile = "/var/run/gunicorn/gunicorn.pid"

# Usuario y grupo (opcional, comentar si no aplica)
# user = "ubuntu"
# group = "www-data"

# Máscara de archivos
umask = 0o007

# =============================================================================
# SSL - Configuración SSL (opcional, Nginx maneja SSL)
# =============================================================================
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# =============================================================================
# HOOKS - Funciones de callback
# =============================================================================
def on_starting(server):
    """Se ejecuta cuando el servidor inicia."""
    print("🚀 Iniciando servidor Gunicorn TemucoSoft POS...")

def on_reload(server):
    """Se ejecuta cuando el servidor se recarga."""
    print("🔄 Recargando servidor Gunicorn...")

def worker_int(worker):
    """Se ejecuta cuando un worker recibe SIGINT."""
    print(f"⚠️ Worker {worker.pid} interrumpido")

def worker_abort(worker):
    """Se ejecuta cuando un worker recibe SIGABRT."""
    print(f"❌ Worker {worker.pid} abortado")
