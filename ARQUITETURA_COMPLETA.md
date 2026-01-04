# Arquitetura Completa: Django + Angular + Docker + Celery
## Sistema Escalável e Seguro para VPS Hostinger

---

## 📋 Índice

1. [Visão Geral da Arquitetura](#visão-geral)
2. [Análise do Estado Atual](#análise-estado-atual)
3. [Docker Compose Completo](#docker-compose-completo)
4. [Configuração Django (settings.py)](#configuração-django)
5. [Configuração Celery](#configuração-celery)
6. [Exemplos de Tasks Assíncronas](#exemplos-tasks)
7. [Configuração Nginx](#configuração-nginx)
8. [Estrutura de Storage](#estrutura-storage)
9. [Segurança e Boas Práticas](#segurança)
10. [Fluxo Completo Upload → Processamento](#fluxo-completo)
11. [Migração para S3/MinIO](#migração-s3)
12. [Monitoramento e Observabilidade](#monitoramento)
13. [Checklist de Implementação](#checklist)

---

## 🎯 Visão Geral da Arquitetura {#visão-geral}

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (Porta 80/443)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Angular    │  │  /api/* →    │  │  /media/* →  │      │
│  │   (SPA)      │  │  Django API  │  │  Django Auth │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐   ┌──────▼──────┐
│   Django     │   │     Redis      │   │  PostgreSQL │
│   (Gunicorn) │   │   (Broker)     │   │   (DB)      │
└───────┬──────┘   └────────┬────────┘   └─────────────┘
        │                   │
        │         ┌─────────┼─────────┐
        │         │         │         │
    ┌───▼───┐ ┌───▼───┐ ┌──▼───┐ ┌───▼───┐
    │Celery │ │Celery │ │Celery│ │Flower │
    │Worker │ │ Beat  │ │Queue │ │Monitor│
    └───┬───┘ └───────┘ └──────┘ └───────┘
        │
        │
┌───────▼──────────────────────────────────────┐
│         Media Volume (Shared)                  │
│  media/                                       │
│    certificados/                              │
│      usuario_id/                              │
│        ano/                                   │
│          arquivo.pdf                          │
└───────────────────────────────────────────────┘
```

### Stack Tecnológico

- **Backend**: Django 6.0+ com Django REST Framework
- **Frontend**: Angular (SPA) servido via Nginx
- **Banco de Dados**: PostgreSQL 18
- **Cache/Broker**: Redis 7
- **Processamento Assíncrono**: Celery 5.x
- **Web Server**: Nginx (reverse proxy + static files)
- **Monitoramento**: Flower (Celery)
- **Containerização**: Docker Compose
- **Autenticação**: JWT (djangorestframework-simplejwt)

---

## 🔍 Análise do Estado Atual {#análise-estado-atual}

### ✅ O que já existe:
- Docker Compose básico (backend, db, nginx)
- Django com DRF e JWT configurado
- Nginx com SSL e proxy reverso
- PostgreSQL configurado

### ❌ O que falta implementar:
- Redis (broker para Celery)
- Celery Worker e Beat
- Flower (monitoramento)
- Configuração de Media Storage
- Tasks assíncronas para processamento de PDFs
- Volume compartilhado para media
- Configuração de Celery no Django
- Endpoint protegido para download de arquivos

---

## 🐳 Docker Compose Completo {#docker-compose-completo}

### Arquivo: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # ============================================
  # PostgreSQL Database
  # ============================================
  db:
    image: postgres:18-alpine
    container_name: postgres_licitacao
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-appdb}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    # Non-root user (opcional, requer ajuste de permissões)
    # user: "999:999"

  # ============================================
  # Redis (Broker e Result Backend)
  # ============================================
  redis:
    image: redis:7-alpine
    container_name: redis_licitacao
    restart: unless-stopped
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    # Non-root user
    # user: "999:999"

  # ============================================
  # Django Backend (API)
  # ============================================
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: licitacao360_backend
    restart: unless-stopped
    command: >
      sh -c "
        python manage.py makemigrations --noinput &&
        python manage.py migrate --noinput &&
        python manage.py collectstatic --noinput &&
        gunicorn django_licitacao360.wsgi:application
          --bind 0.0.0.0:8000
          --timeout 600
          --workers ${GUNICORN_WORKERS:-2}
          --threads ${GUNICORN_THREADS:-4}
          --access-logfile -
          --error-logfile -
          --log-level info
      "
    volumes:
      - ./backend:/app
      - media_volume:/app/media
      - static_volume:/app/staticfiles
    environment:
      # Database
      - POSTGRES_DB=${POSTGRES_DB:-appdb}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      
      # Django
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG:-False}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1}
      
      # Storage
      - STORAGE_BACKEND=${STORAGE_BACKEND:-local}
      - MAX_UPLOAD_MB=${MAX_UPLOAD_MB:-20}
      
      # Celery
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
      
      # JWT
      - JWT_ACCESS_TOKEN_LIFETIME=${JWT_ACCESS_TOKEN_LIFETIME:-15}
      - JWT_REFRESH_TOKEN_LIFETIME=${JWT_REFRESH_TOKEN_LIFETIME:-7}
      
      # Superuser (apenas primeira execução)
      - DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}
      - DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
      - DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app_network
    # Non-root user (requer ajuste de permissões)
    # user: "1000:1000"

  # ============================================
  # Celery Worker
  # ============================================
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: celery_worker_licitacao
    restart: unless-stopped
    command: >
      celery -A django_licitacao360 worker
      --loglevel=info
      --concurrency=${CELERY_WORKER_CONCURRENCY:-4}
      --max-tasks-per-child=${CELERY_MAX_TASKS_PER_CHILD:-1000}
      --time-limit=${CELERY_TASK_TIME_LIMIT:-3600}
      --soft-time-limit=${CELERY_TASK_SOFT_TIME_LIMIT:-300}
      --queues=certificados,default
    volumes:
      - ./backend:/app
      - media_volume:/app/media
    environment:
      # Database
      - POSTGRES_DB=${POSTGRES_DB:-appdb}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      
      # Django
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG:-False}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost}
      
      # Storage
      - STORAGE_BACKEND=${STORAGE_BACKEND:-local}
      
      # Celery
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - backend
      - redis
      - db
    networks:
      - app_network
    # Non-root user
    # user: "1000:1000"

  # ============================================
  # Celery Beat (Scheduler)
  # ============================================
  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: celery_beat_licitacao
    restart: unless-stopped
    command: >
      celery -A django_licitacao360 beat
      --loglevel=info
      --scheduler=django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./backend:/app
    environment:
      # Database
      - POSTGRES_DB=${POSTGRES_DB:-appdb}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      
      # Django
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG:-False}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost}
      
      # Celery
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - backend
      - redis
      - db
    networks:
      - app_network
    # Non-root user
    # user: "1000:1000"

  # ============================================
  # Flower (Celery Monitoring)
  # ============================================
  flower:
    image: mher/flower:2.0
    container_name: flower_licitacao
    restart: unless-stopped
    command: >
      flower
      --port=5555
      --broker=${CELERY_BROKER_URL:-redis://redis:6379/0}
      --broker_api=${CELERY_BROKER_URL:-redis://redis:6379/0}
      --basic_auth=${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-flower123}
      --url_prefix=/flower
      --persistent=True
      --db=/flower/flower.db
    volumes:
      - flower_data:/flower
    ports:
      # Expor apenas internamente ou via túnel SSH
      - "127.0.0.1:5555:5555"
    networks:
      - app_network
    depends_on:
      - redis
      - celery_worker

  # ============================================
  # Nginx (Reverse Proxy + Angular)
  # ============================================
  nginx:
    image: nginx:alpine
    container_name: licitacao_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      # Frontend Angular
      - ./frontend-licitacao/dist/frontend/browser:/usr/share/nginx/html:ro
      
      # Nginx Configuration
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      
      # SSL Certificates (Let's Encrypt)
      - /etc/letsencrypt:/etc/letsencrypt:ro
      
      # ACME Challenge
      - ./certbot/www:/var/www/certbot:ro
      
      # Django Static Files
      - static_volume:/static:ro
    depends_on:
      - backend
    networks:
      - app_network

# ============================================
# Volumes
# ============================================
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  media_volume:
    driver: local
  static_volume:
    driver: local
  flower_data:
    driver: local

# ============================================
# Networks
# ============================================
networks:
  app_network:
    driver: bridge
```

### Arquivo: `.env` (Template)

```bash
# ============================================
# Database
# ============================================
POSTGRES_DB=appdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_seguro_aqui

# ============================================
# Django
# ============================================
SECRET_KEY=sua-chave-secreta-super-segura-aqui-gerada-aleatoriamente
DEBUG=False
ALLOWED_HOSTS=licitacao360.com,www.licitacao360.com,72.60.52.231

# ============================================
# Storage
# ============================================
STORAGE_BACKEND=local
MAX_UPLOAD_MB=20

# Para migração futura S3:
# STORAGE_BACKEND=s3
# AWS_S3_REGION_NAME=us-east-1
# AWS_STORAGE_BUCKET_NAME=licitacao360-media
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret

# ============================================
# Celery
# ============================================
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_WORKER_CONCURRENCY=4
CELERY_MAX_TASKS_PER_CHILD=1000
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=300

# ============================================
# Gunicorn
# ============================================
GUNICORN_WORKERS=2
GUNICORN_THREADS=4

# ============================================
# JWT
# ============================================
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# ============================================
# Flower
# ============================================
FLOWER_USER=admin
FLOWER_PASSWORD=senha_segura_flower

# ============================================
# Django Superuser (primeira execução)
# ============================================
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=senha_super_segura_admin
DJANGO_SUPERUSER_EMAIL=admin@licitacao360.com
```

---

## ⚙️ Configuração Django (settings.py) {#configuração-django}

### Adições necessárias ao `settings.py`:

```python
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# Storage Configuration
# ============================================
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

# Limites de Upload
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_PERMISSIONS = 0o640

# Storage Backend (preparado para S3/MinIO)
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")

if STORAGE_BACKEND == "s3":
    # Configuração S3 (futura migração)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_CUSTOM_DOMAIN = None
    AWS_DEFAULT_ACL = "private"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
else:
    # Storage Local (padrão)
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# ============================================
# Celery Configuration
# ============================================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"
CELERY_ENABLE_UTC = True

# Celery Beat Scheduler (persistente)
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Task Routes (filas específicas)
CELERY_TASK_ROUTES = {
    "certificados.tasks.process_pdf": {"queue": "certificados"},
    "certificados.tasks.generate_thumbnail": {"queue": "certificados"},
    "certificados.tasks.limpar_arquivos_orfaos": {"queue": "certificados"},
}

# Task Time Limits
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", "3600"))  # 1 hora
CELERY_TASK_SOFT_TIME_LIMIT = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "300"))  # 5 min

# Worker Settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = int(os.getenv("CELERY_MAX_TASKS_PER_CHILD", "1000"))

# ============================================
# REST Framework Configuration
# ============================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}

# ============================================
# JWT Configuration
# ============================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ============================================
# Logging Configuration
# ============================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ============================================
# Installed Apps (adicionar)
# ============================================
INSTALLED_APPS = [
    # ... apps existentes ...
    "django_celery_beat",  # Para agendamentos persistentes
    "django_celery_results",  # Opcional: resultados persistentes
    # ... outros apps ...
]
```

---

## 🔄 Configuração Celery {#configuração-celery}

### Arquivo: `backend/django_licitacao360/celery.py`

```python
"""
Configuração do Celery para o projeto Licitacao360
"""
import os
from celery import Celery

# Configurar o módulo de settings padrão do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_licitacao360.settings")

app = Celery("licitacao360")

# Usar configurações do Django com namespace CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-descobrir tasks em todos os apps instalados
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Task de debug para testar a configuração do Celery
    """
    print(f"Request: {self.request!r}")
```

### Arquivo: `backend/django_licitacao360/__init__.py`

```python
"""
Garantir que o Celery seja carregado quando o Django iniciar
"""
from .celery import app as celery_app

__all__ = ("celery_app",)
```

---

## 📦 Exemplos de Tasks Assíncronas {#exemplos-tasks}

### Estrutura de Diretórios

```
backend/
  django_licitacao360/
    apps/
      certificados/  # Novo app (exemplo)
        __init__.py
        models.py
        serializers.py
        views.py
        tasks.py      # Tasks Celery
        urls.py
```

### Arquivo: `backend/django_licitacao360/apps/certificados/models.py`

```python
"""
Modelo de exemplo para Certificados
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import uuid
import os

User = get_user_model()


def certificado_upload_path(instance, filename):
    """
    Gera o caminho de upload: certificados/usuario_id/ano/uuid.pdf
    """
    ano = instance.ano or instance.criado_em.year
    return os.path.join(
        "certificados",
        str(instance.usuario.id),
        str(ano),
        f"{uuid.uuid4()}.pdf"
    )


class Certificado(models.Model):
    """
    Modelo para armazenar certificados em PDF
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificados"
    )
    nome_original = models.CharField(max_length=255)
    arquivo = models.FileField(
        upload_to=certificado_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])]
    )
    tamanho = models.PositiveIntegerField(help_text="Tamanho em bytes")
    ano = models.IntegerField(null=True, blank=True)
    
    # Metadados processados assincronamente
    checksum_md5 = models.CharField(max_length=32, blank=True)
    paginas = models.PositiveIntegerField(null=True, blank=True)
    processado_em = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["usuario", "ano"]),
            models.Index(fields=["checksum_md5"]),
        ]
    
    def __str__(self):
        return f"{self.nome_original} - {self.usuario.username}"
```

### Arquivo: `backend/django_licitacao360/apps/certificados/tasks.py`

```python
"""
Tasks Celery para processamento assíncrono de certificados
"""
import hashlib
import logging
from pathlib import Path
from celery import shared_task
from django.core.files.storage import default_storage
from django.utils import timezone
from PyPDF2 import PdfReader
from .models import Certificado

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(FileNotFoundError, IOError),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
    queue="certificados"
)
def process_pdf(self, certificado_id: int):
    """
    Processa um PDF assincronamente:
    - Calcula hash MD5
    - Extrai número de páginas
    - Atualiza metadados no banco
    """
    try:
        certificado = Certificado.objects.get(pk=certificado_id)
        logger.info(f"Iniciando processamento do certificado {certificado_id}")
        
        # Obter caminho do arquivo
        if not certificado.arquivo:
            raise FileNotFoundError(f"Arquivo não encontrado para certificado {certificado_id}")
        
        arquivo_path = certificado.arquivo.path
        
        # Validar existência do arquivo
        if not Path(arquivo_path).exists():
            raise FileNotFoundError(f"Arquivo físico não encontrado: {arquivo_path}")
        
        # Calcular hash MD5
        hash_md5 = hashlib.md5()
        with open(arquivo_path, "rb") as pdf_file:
            for chunk in iter(lambda: pdf_file.read(8192), b""):
                hash_md5.update(chunk)
        
        checksum = hash_md5.hexdigest()
        
        # Extrair número de páginas
        try:
            reader = PdfReader(arquivo_path)
            num_paginas = len(reader.pages)
        except Exception as e:
            logger.warning(f"Erro ao ler PDF {certificado_id}: {e}")
            num_paginas = None
        
        # Atualizar certificado
        certificado.checksum_md5 = checksum
        certificado.paginas = num_paginas
        certificado.processado_em = timezone.now()
        certificado.save(update_fields=["checksum_md5", "paginas", "processado_em"])
        
        logger.info(
            f"Certificado {certificado_id} processado: "
            f"MD5={checksum[:8]}..., páginas={num_paginas}"
        )
        
        return {
            "certificado_id": certificado_id,
            "checksum_md5": checksum,
            "paginas": num_paginas,
        }
        
    except Certificado.DoesNotExist:
        logger.error(f"Certificado {certificado_id} não encontrado")
        raise
    except Exception as e:
        logger.error(f"Erro ao processar certificado {certificado_id}: {e}", exc_info=True)
        raise


@shared_task(
    queue="certificados",
    time_limit=300,
    soft_time_limit=240
)
def generate_thumbnail(certificado_id: int):
    """
    Gera miniatura do PDF (primeira página)
    Requer: pdf2image ou Ghostscript
    """
    try:
        certificado = Certificado.objects.get(pk=certificado_id)
        
        # Implementação com pdf2image
        # from pdf2image import convert_from_path
        # images = convert_from_path(certificado.arquivo.path, first_page=1, last_page=1)
        # thumbnail_path = ...
        # certificado.thumbnail.save(...)
        
        logger.info(f"Thumbnail gerado para certificado {certificado_id}")
        
    except Exception as e:
        logger.error(f"Erro ao gerar thumbnail {certificado_id}: {e}", exc_info=True)
        raise


@shared_task(
    queue="certificados",
    time_limit=3600
)
def limpar_arquivos_orfaos():
    """
    Remove arquivos órfãos do filesystem
    Executado periodicamente via Celery Beat
    """
    logger.info("Iniciando limpeza de arquivos órfãos")
    
    from django.conf import settings
    import os
    
    media_root = Path(settings.MEDIA_ROOT)
    certificados_dir = media_root / "certificados"
    
    if not certificados_dir.exists():
        logger.info("Diretório de certificados não existe")
        return
    
    # Coletar todos os arquivos no filesystem
    arquivos_fs = set()
    for root, dirs, files in os.walk(certificados_dir):
        for file in files:
            arquivos_fs.add(Path(root) / file)
    
    # Coletar todos os arquivos referenciados no banco
    certificados = Certificado.objects.exclude(arquivo="")
    arquivos_db = set()
    for cert in certificados:
        if cert.arquivo:
            try:
                arquivos_db.add(Path(cert.arquivo.path).resolve())
            except:
                pass
    
    # Encontrar órfãos
    orfaos = arquivos_fs - arquivos_db
    
    # Remover órfãos
    removidos = 0
    for arquivo_orfao in orfaos:
        try:
            arquivo_orfao.unlink()
            removidos += 1
            logger.info(f"Arquivo órfão removido: {arquivo_orfao}")
        except Exception as e:
            logger.error(f"Erro ao remover {arquivo_orfao}: {e}")
    
    logger.info(f"Limpeza concluída: {removidos} arquivos órfãos removidos")
    return {"removidos": removidos}


@shared_task(
    queue="certificados"
)
def revalidar_certificados():
    """
    Revalida certificados periodicamente
    Executado via Celery Beat
    """
    logger.info("Iniciando revalidação de certificados")
    
    # Exemplo: revalidar certificados antigos
    from datetime import timedelta
    limite = timezone.now() - timedelta(days=365)
    
    certificados_antigos = Certificado.objects.filter(
        criado_em__lt=limite,
        processado_em__isnull=True
    )
    
    count = 0
    for cert in certificados_antigos:
        process_pdf.delay(cert.id)
        count += 1
    
    logger.info(f"{count} certificados enfileirados para revalidação")
    return {"enfileirados": count}
```

### Configuração de Agendamentos (Celery Beat)

Adicionar ao `settings.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "limpar_arquivos_orfaos": {
        "task": "certificados.tasks.limpar_arquivos_orfaos",
        "schedule": crontab(hour=2, minute=0),  # Diariamente às 2h
    },
    "revalidar_certificados": {
        "task": "certificados.tasks.revalidar_certificados",
        "schedule": crontab(day_of_week="sunday", hour=3, minute=30),  # Domingos às 3:30
    },
}
```

---

## 🌐 Configuração Nginx {#configuração-nginx}

### Arquivo: `nginx/nginx.conf`

```nginx
# Upstream para Django
upstream backend_upstream {
    server licitacao360_backend:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# Resolver DNS interno do Docker
resolver 127.0.0.11 valid=30s;

# ============================================
# HTTP → HTTPS Redirect
# ============================================
server {
    listen 80;
    server_name licitacao360.com www.licitacao360.com;

    # ACME Challenge (Let's Encrypt)
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect para HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# ============================================
# HTTPS - Produção
# ============================================
server {
    listen 443 ssl http2;
    server_name licitacao360.com www.licitacao360.com;

    # SSL Certificates
    ssl_certificate     /etc/letsencrypt/live/licitacao360.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/licitacao360.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Upload Limits
    client_max_body_size 25m;
    client_body_buffer_size 128k;
    client_body_timeout 60s;

    # ============================================
    # Frontend Angular (SPA)
    # ============================================
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache para assets estáticos
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # ============================================
    # Django API
    # ============================================
    location /api/ {
        proxy_pass http://backend_upstream;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # Não passar cabeçalhos desnecessários
        proxy_redirect off;
    }

    # ============================================
    # Django Admin
    # ============================================
    location /admin {
        proxy_pass http://backend_upstream;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ============================================
    # Media Files (PROTEGIDO - via Django)
    # ============================================
    location /media/ {
        # IMPORTANTE: Não servir diretamente do filesystem
        # Sempre passar pelo Django para autenticação/autorização
        proxy_pass http://backend_upstream/api/files/serve/;
        proxy_http_version 1.1;
        
        # Passar URI original para Django
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Original-URI $request_uri;
        
        # Timeouts maiores para downloads
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        
        # Não cachear arquivos de mídia
        proxy_cache off;
        add_header Cache-Control "private, no-cache, no-store, must-revalidate";
    }

    # ============================================
    # Static Files (Django)
    # ============================================
    location /static/ {
        alias /static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # ============================================
    # Flower (Monitoramento Celery)
    # Apenas via túnel SSH ou VPN
    # ============================================
    location /flower {
        # Descomentar apenas se necessário acesso externo
        # proxy_pass http://flower:5555;
        # proxy_set_header Host $host;
        # proxy_set_header X-Real-IP $remote_addr;
        # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # proxy_set_header X-Forwarded-Proto $scheme;
        
        # Por segurança, retornar 403
        return 403;
    }

    # ============================================
    # Error Pages
    # ============================================
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }

    # ============================================
    # Gzip Compression
    # ============================================
    gzip on;
    gzip_vary on;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
}
```

---

## 📁 Estrutura de Storage {#estrutura-storage}

### Organização de Arquivos

```
media/
├── certificados/
│   ├── 1/                    # usuario_id
│   │   ├── 2024/
│   │   │   ├── uuid-1.pdf
│   │   │   └── uuid-2.pdf
│   │   └── 2025/
│   │       └── uuid-3.pdf
│   └── 2/
│       └── 2024/
│           └── uuid-4.pdf
└── outros/                    # Outros tipos de arquivo
    └── ...
```

### View de Download Protegido

### Arquivo: `backend/django_licitacao360/apps/certificados/views.py`

```python
"""
Views para certificados com download protegido
"""
from django.http import FileResponse, Http404
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Certificado
from .serializers import CertificadoSerializer


class CertificadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar certificados
    """
    queryset = Certificado.objects.all()
    serializer_class = CertificadoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Usuários só veem seus próprios certificados
        Admins veem todos
        """
        user = self.request.user
        if user.is_staff:
            return Certificado.objects.all()
        return Certificado.objects.filter(usuario=user)
    
    @action(
        detail=True,
        methods=["get"],
        url_path="download",
        permission_classes=[IsAuthenticated]
    )
    def download(self, request, pk=None):
        """
        Endpoint protegido para download de arquivos
        """
        certificado = self.get_object()
        
        # Verificar permissões
        if not request.user.is_staff and certificado.usuario != request.user:
            return Response(
                {"detail": "Você não tem permissão para acessar este arquivo."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar existência do arquivo
        if not certificado.arquivo:
            raise Http404("Arquivo não encontrado")
        
        try:
            # Abrir arquivo via storage
            file = default_storage.open(certificado.arquivo.name, "rb")
            
            # Registrar auditoria (opcional)
            # AuditoriaLog.objects.create(
            #     usuario=request.user,
            #     acao="download",
            #     certificado=certificado
            # )
            
            # Retornar FileResponse
            response = FileResponse(
                file,
                content_type="application/pdf",
                as_attachment=True,
                filename=certificado.nome_original
            )
            
            # Headers de segurança
            response["X-Content-Type-Options"] = "nosniff"
            response["Content-Disposition"] = f'attachment; filename="{certificado.nome_original}"'
            
            return response
            
        except FileNotFoundError:
            raise Http404("Arquivo não encontrado no storage")
        except Exception as e:
            return Response(
                {"detail": f"Erro ao servir arquivo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### View Genérica para Servir Arquivos

### Arquivo: `backend/django_licitacao360/apps/core/files/views.py`

```python
"""
View genérica para servir arquivos de mídia com autenticação
"""
from django.http import FileResponse, Http404
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import os


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def serve_file(request):
    """
    Serve arquivos de mídia após validação de autenticação
    URL esperada: /api/files/serve/?path=media/certificados/1/2024/uuid.pdf
    """
    file_path = request.GET.get("path")
    
    if not file_path:
        return Response(
            {"detail": "Parâmetro 'path' é obrigatório"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar que o caminho está dentro de MEDIA_ROOT
    from django.conf import settings
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    full_path = os.path.abspath(os.path.join(media_root, file_path))
    
    if not full_path.startswith(media_root):
        return Response(
            {"detail": "Caminho inválido"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verificar existência
    if not default_storage.exists(file_path):
        raise Http404("Arquivo não encontrado")
    
    try:
        file = default_storage.open(file_path, "rb")
        filename = os.path.basename(file_path)
        
        response = FileResponse(
            file,
            content_type="application/pdf",  # Ajustar conforme necessário
            as_attachment=False  # Exibir no navegador
        )
        
        response["X-Content-Type-Options"] = "nosniff"
        return response
        
    except Exception as e:
        return Response(
            {"detail": f"Erro ao servir arquivo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### URL Configuration

```python
# backend/django_licitacao360/urls.py
from django.urls import path, include
from django_licitacao360.apps.core.files.views import serve_file

urlpatterns = [
    # ... outras URLs ...
    path("api/files/serve/", serve_file, name="serve_file"),
    path("api/certificados/", include("django_licitacao360.apps.certificados.urls")),
]
```

---

## 🔒 Segurança e Boas Práticas {#segurança}

### 1. Containers Non-Root

```yaml
# No docker-compose.yml, adicionar user após criar usuário no Dockerfile
user: "1000:1000"
```

### 2. Validação de Uploads

```python
# serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError
import magic

class CertificadoSerializer(serializers.ModelSerializer):
    arquivo = serializers.FileField()
    
    def validate_arquivo(self, value):
        # Validar tamanho
        max_size = 20 * 1024 * 1024  # 20MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Arquivo muito grande. Tamanho máximo: {max_size / 1024 / 1024}MB"
            )
        
        # Validar MIME type
        mime = magic.Magic(mime=True)
        file_mime = mime.from_buffer(value.read(1024))
        value.seek(0)  # Resetar ponteiro
        
        if file_mime != "application/pdf":
            raise serializers.ValidationError("Apenas arquivos PDF são permitidos")
        
        # Validar extensão
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Extensão deve ser .pdf")
        
        return value
```

### 3. Rate Limiting

```python
# settings.py
REST_FRAMEWORK = {
    # ... outras configurações ...
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "upload": "10/hour",  # Limite específico para uploads
    },
}
```

### 4. Secrets Management

- Usar variáveis de ambiente via `.env`
- Nunca commitar `.env` no Git
- Usar secrets managers em produção (AWS Secrets Manager, HashiCorp Vault)

### 5. Backup Strategy

```bash
# Script de backup (backup.sh)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
docker exec postgres_licitacao pg_dump -U postgres appdb > "backup_db_${DATE}.sql"

# Backup Media Volume
docker run --rm \
  -v licitacao360_media_volume:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/media_${DATE}.tar.gz -C /data .

# Limpar backups antigos (manter últimos 30 dias)
find backups/ -name "*.sql" -mtime +30 -delete
find backups/ -name "*.tar.gz" -mtime +30 -delete
```

---

## 🔄 Fluxo Completo Upload → Processamento {#fluxo-completo}

### 1. Upload de Arquivo

```
Cliente (Angular)
    ↓ POST /api/certificados/ (multipart/form-data)
    ↓ Headers: Authorization: Bearer <token>
Nginx
    ↓ Proxy para Django
Django ViewSet
    ↓ Validação (tamanho, MIME type, autenticação)
    ↓ Salvar arquivo em media/certificados/usuario_id/ano/uuid.pdf
    ↓ Criar registro no banco (Certificado)
    ↓ Enfileirar task: process_pdf.delay(certificado.id)
    ↓ Retornar 201 Created com dados do certificado
```

### 2. Processamento Assíncrono

```
Celery Worker (recebe task)
    ↓ process_pdf(certificado_id)
    ↓ Ler arquivo do media_volume compartilhado
    ↓ Calcular hash MD5
    ↓ Extrair número de páginas (PyPDF2)
    ↓ Atualizar registro no banco
    ↓ (Opcional) Enfileirar generate_thumbnail.delay()
```

### 3. Download de Arquivo

```
Cliente (Angular)
    ↓ GET /api/certificados/{id}/download/
    ↓ Headers: Authorization: Bearer <token>
Nginx
    ↓ Proxy para Django (/api/files/serve/)
Django View
    ↓ Verificar autenticação e permissões
    ↓ Validar que usuário tem acesso ao arquivo
    ↓ Abrir arquivo via storage.open()
    ↓ Retornar FileResponse
```

---

## ☁️ Migração para S3/MinIO {#migração-s3}

### Preparação

1. **Instalar dependências**:
```bash
pip install django-storages boto3
```

2. **Atualizar `requirements.txt`**:
```
django-storages[boto3]
boto3
```

3. **Configurar variáveis de ambiente**:
```bash
STORAGE_BACKEND=s3
AWS_S3_REGION_NAME=us-east-1
AWS_STORAGE_BUCKET_NAME=licitacao360-media
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

4. **Migrar arquivos existentes**:
```python
# management/commands/migrate_to_s3.py
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from certificados.models import Certificado
import os

class Command(BaseCommand):
    def handle(self, *args, **options):
        for cert in Certificado.objects.all():
            if cert.arquivo:
                # Upload para S3
                with open(cert.arquivo.path, 'rb') as f:
                    default_storage.save(cert.arquivo.name, f)
                self.stdout.write(f"Migrado: {cert.arquivo.name}")
```

### Vantagens da Abordagem

- **Zero refatoração**: Código continua usando `FileField` e `storage.open()`
- **Migração gradual**: Pode manter local e S3 simultaneamente
- **Testável**: Fácil testar localmente antes de migrar

---

## 📊 Monitoramento e Observabilidade {#monitoramento}

### 1. Health Checks

```python
# views.py
from django.http import JsonResponse
from django.db import connection
from redis import Redis
import os

def health_check(request):
    """
    Endpoint de health check para Docker/Kubernetes
    """
    checks = {
        "status": "healthy",
        "database": "ok",
        "redis": "ok",
        "celery": "ok",
    }
    
    # Verificar banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"
    
    # Verificar Redis
    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
        r = Redis.from_url(redis_url)
        r.ping()
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"
    
    status_code = 200 if checks["status"] == "healthy" else 503
    return JsonResponse(checks, status=status_code)
```

### 2. Logging Estruturado

```python
# Já configurado no settings.py com JSON formatter
import logging
logger = logging.getLogger(__name__)

logger.info("Upload realizado", extra={
    "usuario_id": request.user.id,
    "arquivo_tamanho": file.size,
    "certificado_id": certificado.id
})
```

### 3. Métricas Prometheus (Opcional)

```python
# pip install django-prometheus
INSTALLED_APPS = [
    # ...
    "django_prometheus",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    # ... outros middlewares ...
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

# URL: /metrics
```

---

## ✅ Checklist de Implementação {#checklist}

### Fase 1: Infraestrutura Base
- [ ] Atualizar `docker-compose.yml` com Redis, Celery Worker, Celery Beat, Flower
- [ ] Criar arquivo `.env` com todas as variáveis necessárias
- [ ] Configurar volumes: `media_volume`, `redis_data`, `flower_data`
- [ ] Testar build e start dos containers

### Fase 2: Configuração Django
- [ ] Adicionar configurações de Storage ao `settings.py`
- [ ] Adicionar configurações de Celery ao `settings.py`
- [ ] Criar `celery.py` no projeto Django
- [ ] Atualizar `__init__.py` para carregar Celery
- [ ] Instalar dependências: `celery`, `redis`, `django-celery-beat`, `PyPDF2`

### Fase 3: Tasks Assíncronas
- [ ] Criar app `certificados` (ou usar existente)
- [ ] Criar modelo `Certificado` com estrutura de storage
- [ ] Criar `tasks.py` com tasks de processamento
- [ ] Configurar agendamentos no `CELERY_BEAT_SCHEDULE`
- [ ] Testar tasks manualmente

### Fase 4: API e Views
- [ ] Criar `CertificadoViewSet` com upload
- [ ] Implementar validação de arquivos (tamanho, MIME type)
- [ ] Criar endpoint de download protegido
- [ ] Criar view genérica `serve_file` para Nginx
- [ ] Configurar URLs

### Fase 5: Nginx
- [ ] Atualizar `nginx.conf` com proxy para `/media/`
- [ ] Configurar limites de upload (`client_max_body_size`)
- [ ] Testar proxy reverso
- [ ] Configurar SSL (Let's Encrypt)

### Fase 6: Segurança
- [ ] Implementar rate limiting
- [ ] Configurar containers non-root (opcional)
- [ ] Revisar permissões de arquivos
- [ ] Configurar CORS adequadamente
- [ ] Implementar auditoria de downloads

### Fase 7: Monitoramento
- [ ] Configurar health checks
- [ ] Acessar Flower e verificar tasks
- [ ] Configurar logs estruturados
- [ ] Testar agendamentos do Celery Beat

### Fase 8: Testes
- [ ] Testar upload de PDF
- [ ] Verificar processamento assíncrono
- [ ] Testar download protegido
- [ ] Verificar limpeza de órfãos
- [ ] Testar revalidação periódica

### Fase 9: Documentação
- [ ] Documentar endpoints da API
- [ ] Criar guia de deploy
- [ ] Documentar variáveis de ambiente
- [ ] Criar runbook de operações

### Fase 10: Produção
- [ ] Configurar backups automatizados
- [ ] Configurar monitoramento de alertas
- [ ] Revisar configurações de segurança
- [ ] Testar disaster recovery
- [ ] Documentar procedimentos de escalabilidade

---

## 📚 Referências e Recursos

- [Django Storage Documentation](https://docs.djangoproject.com/en/stable/topics/files/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Nginx Reverse Proxy](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)

---

## 🎯 Conclusão

Esta arquitetura fornece uma base sólida, escalável e segura para o sistema Licitacao360, com:

✅ **Storage local** pronto para migração S3/MinIO  
✅ **Processamento assíncrono** robusto com Celery  
✅ **Segurança** em todas as camadas  
✅ **Monitoramento** integrado  
✅ **Escalabilidade** horizontal  
✅ **Manutenibilidade** através de código limpo e documentado  

Siga o checklist de implementação para garantir uma migração suave e bem-sucedida.

---

**Última atualização**: 2024  
**Versão**: 1.0  
**Autor**: Arquitetura de Software

