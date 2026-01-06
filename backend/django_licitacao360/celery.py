"""
Configuração do Celery para o projeto Licitacao360
"""
import os
from celery import Celery
from celery.signals import task_postrun

# Configurar o módulo de settings padrão do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_licitacao360.settings")

app = Celery("licitacao360")

# Usar configurações do Django com namespace CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-descobrir tasks em todos os apps instalados
app.autodiscover_tasks()


@task_postrun.connect
def close_db_connections(**kwargs):
    """
    Fecha conexões de banco de dados após cada task do Celery.
    Isso garante que as transações sejam commitadas e as conexões sejam liberadas.
    """
    from django.db import connections
    connections.close_all()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Task de debug para testar a configuração do Celery
    """
    print(f"Request: {self.request!r}")

