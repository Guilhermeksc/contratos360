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

