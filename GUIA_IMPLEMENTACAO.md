# Guia Rápido de Implementação
## Arquitetura Django + Angular + Celery + Redis

Este guia fornece passos práticos para implementar a arquitetura completa descrita em `ARQUITETURA_COMPLETA.md`.

---

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Acesso à VPS Hostinger
- Domínio configurado (opcional, para SSL)

---

## 🚀 Passos de Implementação

### 1. Configurar Variáveis de Ambiente

```bash
# Copiar template de variáveis de ambiente
cp env.example .env

# Editar .env com suas configurações
nano .env
```

**Importante**: 
- Altere `SECRET_KEY` para uma chave segura
- Altere todas as senhas padrão
- Configure `ALLOWED_HOSTS` com seu domínio/IP

### 2. Atualizar Dependências do Backend

```bash
cd backend
pip install -r requirements.txt
```

Ou se estiver usando Docker, as dependências serão instaladas automaticamente no build.

### 3. Atualizar Settings.py do Django

Adicione as seguintes configurações ao `backend/django_licitacao360/settings.py`:

#### 3.1. Storage Configuration

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Storage
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

# Limites de Upload
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_PERMISSIONS = 0o640

# Storage Backend
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
if STORAGE_BACKEND == "s3":
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_FILE_OVERWRITE = False
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
```

#### 3.2. Celery Configuration

```python
# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"
CELERY_ENABLE_UTC = True

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_TASK_ROUTES = {
    "certificados.tasks.process_pdf": {"queue": "certificados"},
    "certificados.tasks.generate_thumbnail": {"queue": "certificados"},
    "certificados.tasks.limpar_arquivos_orfaos": {"queue": "certificados"},
}

CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", "3600"))
CELERY_TASK_SOFT_TIME_LIMIT = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "300"))
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = int(os.getenv("CELERY_MAX_TASKS_PER_CHILD", "1000"))
```

#### 3.3. Installed Apps

```python
INSTALLED_APPS = [
    # ... apps existentes ...
    'django_celery_beat',  # Adicionar
    'django_celery_results',  # Opcional
    # ... outros apps ...
]
```

#### 3.4. Logging (Opcional)

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
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
}
```

### 4. Criar Estrutura de Diretórios

```bash
mkdir -p backend/media/certificados
mkdir -p certbot/www
```

### 5. Build e Start dos Containers

```bash
# Build das imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

### 6. Executar Migrações do Celery Beat

```bash
# Entrar no container do backend
docker-compose exec backend python manage.py migrate

# Ou executar diretamente
docker-compose exec backend python manage.py migrate django_celery_beat
```

### 7. Verificar Funcionamento

#### 7.1. Verificar Celery Worker

```bash
# Ver logs do worker
docker-compose logs celery_worker

# Testar task de debug
docker-compose exec backend python manage.py shell
```

No shell do Django:
```python
from django_licitacao360.celery import debug_task
result = debug_task.delay()
print(result.get())
```

#### 7.2. Verificar Redis

```bash
docker-compose exec redis redis-cli ping
# Deve retornar: PONG
```

#### 7.3. Verificar Flower

Acesse: `http://localhost:5555/flower` (ou via túnel SSH se em produção)

Login: usuário e senha configurados no `.env`

### 8. Configurar Nginx para Media Files

Atualize `nginx/nginx.conf` conforme exemplo em `ARQUITETURA_COMPLETA.md`, especialmente a seção `/media/`:

```nginx
location /media/ {
    proxy_pass http://backend_upstream/api/files/serve/;
    proxy_set_header X-Original-URI $request_uri;
    # ... outras configurações
}
```

### 9. Criar View para Servir Arquivos

Crie o arquivo `backend/django_licitacao360/apps/core/files/views.py` conforme exemplo em `ARQUITETURA_COMPLETA.md` e adicione a URL:

```python
# backend/django_licitacao360/urls.py
from django_licitacao360.apps.core.files.views import serve_file

urlpatterns = [
    # ... outras URLs ...
    path("api/files/serve/", serve_file, name="serve_file"),
]
```

### 10. Testar Upload e Processamento

1. Fazer upload de um PDF via API
2. Verificar que a task foi enfileirada no Celery
3. Verificar processamento no Flower
4. Verificar metadados atualizados no banco

---

## 🔧 Comandos Úteis

### Gerenciamento de Containers

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart celery_worker

# Ver logs de um serviço
docker-compose logs -f celery_worker

# Executar comando no container
docker-compose exec backend python manage.py shell
docker-compose exec celery_worker celery -A django_licitacao360 inspect active
```

### Celery

```bash
# Listar tasks ativas
docker-compose exec celery_worker celery -A django_licitacao360 inspect active

# Listar workers registrados
docker-compose exec celery_worker celery -A django_licitacao360 inspect registered

# Limpar fila (CUIDADO: remove todas as tasks pendentes)
docker-compose exec celery_worker celery -A django_licitacao360 purge

# Ver estatísticas
docker-compose exec celery_worker celery -A django_licitacao360 stats
```

### Backup

```bash
# Backup do banco de dados
docker-compose exec db pg_dump -U postgres appdb > backup_$(date +%Y%m%d).sql

# Backup do volume de media
docker run --rm \
  -v licitacao360_media_volume:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/media_$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🐛 Troubleshooting

### Celery Worker não inicia

1. Verificar conexão com Redis:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

2. Verificar logs:
   ```bash
   docker-compose logs celery_worker
   ```

3. Verificar variáveis de ambiente:
   ```bash
   docker-compose exec celery_worker env | grep CELERY
   ```

### Tasks não são processadas

1. Verificar se worker está registrado:
   ```bash
   docker-compose exec celery_worker celery -A django_licitacao360 inspect registered
   ```

2. Verificar filas:
   ```bash
   docker-compose exec celery_worker celery -A django_licitacao360 inspect active_queues
   ```

3. Testar task manualmente:
   ```python
   from certificados.tasks import process_pdf
   process_pdf.delay(certificado_id=1)
   ```

### Erro de permissão em arquivos

```bash
# Ajustar permissões do volume de media
docker-compose exec backend chmod -R 755 /app/media
docker-compose exec backend chown -R 1000:1000 /app/media
```

### Nginx não serve arquivos de media

1. Verificar configuração do proxy
2. Verificar que a view `serve_file` está funcionando
3. Verificar logs do Nginx:
   ```bash
   docker-compose logs nginx
   ```

---

## 📚 Próximos Passos

1. Implementar modelo de Certificados (se ainda não existir)
2. Criar tasks de processamento conforme `ARQUITETURA_COMPLETA.md`
3. Configurar agendamentos no Celery Beat
4. Implementar validação de uploads
5. Configurar monitoramento e alertas
6. Configurar backups automatizados

---

## 📖 Documentação Adicional

- `ARQUITETURA_COMPLETA.md` - Documentação completa da arquitetura
- `ARQUITETURA_DJANGO_ANGULAR.md` - Documentação original (referência)

---

**Última atualização**: 2024

