## Arquitetura Django + Angular em VPS Hostinger

Esta proposta estabelece um blueprint escalável e seguro para um backend Django/DRF com SPA Angular hospedados em uma VPS Hostinger. O objetivo é suportar uploads de certificados em PDF, processamento assíncrono com Celery/Redis, versionamento com Docker Compose e preparar o terreno para futura migração para S3/MinIO sem refatorações profundas.

---

### Visão Geral
- **Services**: Django API + Celery worker/beat + PostgreSQL + Redis + Flower + frontend Angular servido por Nginx atuando também como proxy reverso para a API.
- **Volumes**: `media_volume` (compartilhado entre Django e Celery) e `static_volume` (coletado pelo `collectstatic`). Volumes persistentes adicionais para PostgreSQL e Redis.
- **Rede**: rede interna `backend` para comunicação entre containers; Nginx exposto publicamente em `80/443`.
- **Autenticação**: API protegida por JWT (ex.: `djangorestframework-simplejwt`). Uploads e downloads exigem token válido.
- **Logs**: todo container loga para stdout/stderr (coletável por Stackdriver/ELK). Django configurado com `JSONLogger` ou `logging.config.dictConfig`.

---

### Storage local pronto para S3/MinIO
- Estrutura local sob `MEDIA_ROOT`:

```text
media/
  certificados/
    <usuario_id>/
      <ano>/
        <arquivo>.pdf
```

- Somente metadados no banco (nome original, hash, tamanho, `FileField` apontando para o caminho). PDFs ficam no filesystem.
- `MEDIA_URL=/media/`, mas o acesso público é sempre mediado por uma view autenticada que lê o arquivo e responde via `FileResponse`.
- Variável `STORAGE_BACKEND` controla backend de arquivos:
  - `local` (default) usa FileSystemStorage.
  - `s3` troca para `storages.backends.s3boto3.S3Boto3Storage` com credenciais pré-configuradas. Migração exige apenas alterar `.env`.

---

### docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    user: "999:999"
    env_file: .env
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks: [backend]

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    user: "999:999"
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis_data:/data
    networks: [backend]

  celery_worker:
    build:
      context: ./backend
      target: production
    command: celery -A config worker -l info --concurrency=4
    env_file: .env
    user: "1000:1000"
    depends_on: [django, redis]
    volumes:
      - media_volume:/app/media
    networks: [backend]

  celery_beat:
    build:
      context: ./backend
      target: production
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env
    user: "1000:1000"
    depends_on: [django, redis]
    networks: [backend]

  flower:
    image: mher/flower:2.0
    command: >
      flower --port=5555 --url_prefix=/flower
             --basic_auth=${FLOWER_USER}:${FLOWER_PASSWORD}
             --broker=${CELERY_BROKER_URL}
             --persist
    env_file: .env
    networks: [backend]
    expose:
      - "5555"

volumes:
  media_volume:
  static_volume:
  postgres_data:
  redis_data:

networks:
  backend:
    driver: bridge
```

**Notas importantes**
- `angular` container usa Dockerfile multi-stage (Node para build, Nginx alpine sem root) com reverse proxy:
  - `location /api/` → `proxy_pass http://django:8000/`.
  - `location /media/` → chama endpoint Django (`/api/files/serve/`) ao invés de ler o filesystem diretamente (ver seção Download seguro).
- SSL via certificados Let’s Encrypt montados como volume opcional (ex.: `/etc/letsencrypt:/etc/letsencrypt:ro`).
- `.env` compartilhado define URLs do broker, credenciais do banco, chaves JWT e limites de upload (`MAX_UPLOAD_MB=20`).

---

### Django `settings.py`

```python
from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_PERMISSIONS = 0o640

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
if STORAGE_BACKEND == "s3":
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_FILE_OVERWRITE = False
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_ROUTES = {
    "certificados.tasks.process_pdf": {"queue": "certificados"},
    "certificados.tasks.generate_thumbnail": {"queue": "certificados"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
```

---

### `celery.py`

```python
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("licitacao360")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
```

Executáveis no container:
- `celery -A config worker -l info`
- `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

---

### Exemplo de Tasks (certificados/tasks.py)

```python
import hashlib
from pathlib import Path
from PyPDF2 import PdfReader
from celery import shared_task
from django.core.files import File
from django.utils import timezone
from .models import Certificado

def _open_pdf(certificado: Certificado) -> Path:
    return Path(certificado.arquivo.path)

@shared_task(bind=True, autoretry_for=(FileNotFoundError,), retry_backoff=True)
def process_pdf(self, certificado_id: int):
    certificado = Certificado.objects.get(pk=certificado_id)
    pdf_path = _open_pdf(certificado)

    reader = PdfReader(pdf_path)
    hash_md5 = hashlib.md5()
    with open(pdf_path, "rb") as pdf_file:
        for chunk in iter(lambda: pdf_file.read(8192), b""):
            hash_md5.update(chunk)

    certificado.checksum_md5 = hash_md5.hexdigest()
    certificado.paginas = len(reader.pages)
    certificado.processado_em = timezone.now()
    certificado.save(update_fields=["checksum_md5", "paginas", "processado_em"])

@shared_task
def generate_thumbnail(certificado_id: int):
    certificado = Certificado.objects.get(pk=certificado_id)
    # chamar lib externa (ex.: Ghostscript) e armazenar PNG em FileField/thumbnail
```

`celery_beat` agenda rotinas como limpeza de órfãos e revalidação:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
  "limpar_arquivos_orfaos": {
    "task": "certificados.tasks.limpar_arquivos_orfaos",
    "schedule": crontab(hour="2", minute="0"),
  },
  "revalidar_certificados": {
    "task": "certificados.tasks.revalidar_certificados",
    "schedule": crontab(day_of_week="sun", hour="3", minute="30"),
  },
}
```

---

### Upload e Download seguro
1. **Upload (`POST /api/certificados/`)**
   - Endpoint DRF com `parser_classes=[MultiPartParser]`.
   - Validar `Content-Type` (via `python-magic` ou `PyPDF2`) e tamanho (`request.data["arquivo"].size`).
   - Salvar arquivo no caminho `certificados/<usuario_id>/<ano>/<uuid>.pdf`.
   - Enfileirar `process_pdf.delay(certificado.id)` e `generate_thumbnail.delay(certificado.id)` após `serializer.save()`.
2. **Download (`GET /api/certificados/<id>/arquivo/`)**
   - Verificar permissões (owner/admin).
   - Abrir arquivo via `storage.open()` e retornar `FileResponse`.
   - Registrar auditoria (quem baixou, quando).
3. **Limpeza de órfãos**
   - Task varre `MEDIA_ROOT/certificados` e remove arquivos sem registro no banco.

---

### Nginx (no container Angular)

```nginx
user nginx;
worker_processes auto;
events { worker_connections 1024; }

http {
  client_max_body_size 25m;
  upstream django_api { server django:8000; }

  server {
    listen 80;
    server_name _;

    location / {
      root /usr/share/nginx/html;
      try_files $uri /index.html;
    }

    location /api/ {
      proxy_pass http://django_api/;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_read_timeout 120s;
    }

    location /media/ {
      proxy_pass http://django_api/api/files/serve/;
      proxy_set_header Host $host;
      proxy_set_header X-Original-URI $request_uri;
    }
  }
}
```

- `client_max_body_size` alinhado com `MAX_UPLOAD_MB`.
- TLS configurado via `listen 443 ssl; ssl_certificate ...`.
- Reverse proxy garante que o filesystem nunca é exposto diretamente.

---

### Segurança e Operabilidade
- **Non-root containers** (`user` definido em todos os serviços). Ajustar permissões dos volumes no host (`chown 1000:1000`).
- **JWT + refresh tokens** com rotação. Guardar secrets no `.env` usando `pass` ou `1Password`.
- **Headers**: HSTS, CSP estrita, proteção CSRF apenas para rotas autenticadas via browser (SPA cuida do token).
- **Upload limits**: `client_max_body_size` + `DATA_UPLOAD_MAX_MEMORY_SIZE`.
- **Redis/Flower** expostos somente na rede interna; se necessário acesso externo, aplicar túnel SSH ou WireGuard.
- **Backups**: snapshots diários do volume `media_volume` + dump PostgreSQL. Usar `restic` apontando para Object Storage Hostinger/S3.
- **Logs**: Nginx (JSON), Gunicorn e Celery em STDOUT → coletor (Filebeat/Vector). Configurar retenção e alertas para filas atrasadas (ex.: monitorar `celery_queue_length`).
- **Observabilidade**: integrar metrics Prometheus (django-prometheus) e healthchecks (endpoint `/healthz` + `docker-compose.yml` `healthcheck`).

---

### Fluxo fim a fim
1. Usuário autenticado envia `multipart/form-data` com PDF → Django valida, salva no filesystem e cria registro.
2. Django dispara tasks Celery para hash, metadados e miniaturas. Worker lê o mesmo arquivo via `media_volume`.
3. Resultados são gravados no banco; caso falhem, Celery reexecuta conforme política.
4. Download posterior passa pelo endpoint autenticado, que lê do filesystem e responde com `Content-Disposition`.
5. Celery Beat executa limpezas e revalidações, mantendo o storage organizado.

Com essa base, o sistema opera com storage local performático, possui caminho claro para object storage futuro e segue boas práticas de segurança e escalabilidade para produção em Hostinger.
