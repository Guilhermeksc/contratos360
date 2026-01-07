# Roteiro de Implementação - Task Celery para Sincronização de Contratos

## Objetivo
Criar uma task Celery para sincronizar contratos do ComprasNet para UASGs específicas, similar à task de coleta do INLABS.

## Estrutura da Implementação

### 1. Criar arquivo `tasks.py` no app `gestao_contratos`
   - Localização: `backend/django_licitacao360/apps/gestao_contratos/tasks.py`
   - Conteúdo:
     - Importar `shared_task` do Celery
     - Importar `ComprasNetIngestionService` do serviço de ingestão
     - Criar função helper `get_redis_client()` (similar ao INLABS)
     - Criar task `sync_contratos_uasg()` com:
       - Lock distribuído usando Redis
       - Tratamento de erros
       - Logging adequado
       - Retry automático
       - Fechamento de conexões do banco

### 2. Características da Task
   - **Nome**: `sync_contratos_uasg`
   - **Parâmetros**: `uasg_code: str` (código da UASG)
   - **Lock distribuído**: Usar Redis para evitar execuções simultâneas da mesma UASG
   - **Retry**: Configurar retry automático para erros de rede/conexão
   - **Logging**: Logs informativos e de erro
   - **Retorno**: Dicionário com estatísticas da sincronização

### 3. Adicionar tasks ao `CELERY_BEAT_SCHEDULE` no `settings.py`
   - Criar 5 entradas, uma para cada UASG:
     - 787010
     - 787000
     - 770001
     - 787400
     - 787700
   - Horários sugeridos:
     - Distribuir ao longo do dia para evitar sobrecarga
     - Exemplo: 9h, 11h, 14h, 16h, 18h

### 4. Tratamento de Erros
   - Criar exceção customizada `ComprasNetSyncError` (opcional)
   - Capturar erros de rede, timeout, API
   - Logar erros com contexto completo
   - Garantir remoção do lock mesmo em caso de erro

### 5. Integração com o Serviço Existente
   - Usar `ComprasNetIngestionService.sync_contratos_por_uasg()`
   - Retornar estatísticas do serviço
   - Tratar casos onde não há contratos para processar

## Estrutura do Código

```python
# tasks.py
from celery import shared_task
from django.db import connections
import redis
from urllib.parse import urlparse
from django.conf import settings
import logging

from .services.ingestion import ComprasNetIngestionService

logger = logging.getLogger(__name__)

def get_redis_client():
    """Retorna cliente Redis usando a configuração do Celery."""
    broker_url = getattr(settings, "CELERY_BROKER_URL", "redis://redis:6379/0")
    parsed = urlparse(broker_url)
    return redis.Redis(
        host=parsed.hostname or "redis",
        port=parsed.port or 6379,
        db=2,  # DB diferente do broker e result backend
        decode_responses=True,
    )

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=120, retry_kwargs={"max_retries": 3})
def sync_contratos_uasg(self, uasg_code: str) -> dict:
    """
    Task Celery para sincronizar contratos de uma UASG específica.
    
    Usa lock distribuído para evitar execuções simultâneas da mesma UASG.
    """
    lock_key = f"contratos:lock:{uasg_code}"
    lock_timeout = 3600  # 1 hora
    redis_client = get_redis_client()
    
    # Tenta adquirir lock distribuído
    lock_acquired = redis_client.set(lock_key, "locked", nx=True, ex=lock_timeout)
    
    if not lock_acquired:
        logger.warning(
            "Sincronização de contratos já em execução para UASG %s. Ignorando execução duplicada.",
            uasg_code
        )
        return {
            "uasg_code": uasg_code,
            "skipped": True,
            "reason": "Já existe uma execução em andamento para esta UASG",
        }
    
    try:
        logger.info("Iniciando sincronização de contratos para UASG %s", uasg_code)
        service = ComprasNetIngestionService()
        result = service.sync_contratos_por_uasg(uasg_code)
        
        # Garantir que as transações foram commitadas
        connections.close_all()
        
        logger.info(
            "Sincronização de contratos finalizada. uasg=%s contratos=%s",
            uasg_code,
            result.get("contratos_processados", 0),
        )
        
        return {
            "uasg_code": uasg_code,
            **result,
        }
    except Exception as exc:
        logger.error(
            "Erro ao sincronizar contratos para UASG %s: %s",
            uasg_code,
            exc,
            exc_info=True
        )
        raise
    finally:
        # Remove o lock ao finalizar (mesmo em caso de erro)
        try:
            redis_client.delete(lock_key)
        except Exception as exc:
            logger.warning("Erro ao remover lock %s: %s", lock_key, exc)
        # Garantir fechamento de conexões
        connections.close_all()
```

## Configuração no settings.py

```python
CELERY_BEAT_SCHEDULE = {
    # ... tasks existentes ...
    
    "sync_contratos_uasg_787010": {
        "task": "django_licitacao360.apps.gestao_contratos.tasks.sync_contratos_uasg",
        "schedule": crontab(hour=9, minute=0),  # Diariamente às 9:00 BRT/BRST
        "args": ("787010",),
    },
    "sync_contratos_uasg_787000": {
        "task": "django_licitacao360.apps.gestao_contratos.tasks.sync_contratos_uasg",
        "schedule": crontab(hour=11, minute=0),  # Diariamente às 11:00 BRT/BRST
        "args": ("787000",),
    },
    "sync_contratos_uasg_770001": {
        "task": "django_licitacao360.apps.gestao_contratos.tasks.sync_contratos_uasg",
        "schedule": crontab(hour=14, minute=0),  # Diariamente às 14:00 BRT/BRST
        "args": ("770001",),
    },
    "sync_contratos_uasg_787400": {
        "task": "django_licitacao360.apps.gestao_contratos.tasks.sync_contratos_uasg",
        "schedule": crontab(hour=16, minute=0),  # Diariamente às 16:00 BRT/BRST
        "args": ("787400",),
    },
    "sync_contratos_uasg_787700": {
        "task": "django_licitacao360.apps.gestao_contratos.tasks.sync_contratos_uasg",
        "schedule": crontab(hour=18, minute=0),  # Diariamente às 18:00 BRT/BRST
        "args": ("787700",),
    },
}
```

## Checklist de Implementação

- [ ] Criar arquivo `tasks.py` no app `gestao_contratos`
- [ ] Implementar função `get_redis_client()`
- [ ] Implementar task `sync_contratos_uasg()`
- [ ] Adicionar logging adequado
- [ ] Adicionar tratamento de erros
- [ ] Adicionar lock distribuído
- [ ] Adicionar fechamento de conexões
- [ ] Atualizar `settings.py` com as 5 novas tasks
- [ ] Testar manualmente a task
- [ ] Verificar logs após execução agendada

## Observações

1. **Lock distribuído**: Evita que múltiplos workers executem a mesma sincronização simultaneamente
2. **Retry automático**: Configurado para tentar novamente em caso de falhas temporárias
3. **Horários distribuídos**: As UASGs são sincronizadas em horários diferentes para evitar sobrecarga
4. **Fechamento de conexões**: Importante para evitar vazamentos de conexão do banco de dados
5. **Logging**: Facilita debugging e monitoramento das sincronizações

