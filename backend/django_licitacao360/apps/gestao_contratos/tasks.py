"""
Tasks Celery para sincronização de contratos do ComprasNet
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

import redis
from celery import shared_task
from django.conf import settings
from django.db import connections

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
    
    Args:
        uasg_code: Código da UASG a ser sincronizada
    
    Returns:
        Dicionário com estatísticas da sincronização
    """
    lock_key = f"contratos:lock:{uasg_code}"
    lock_timeout = 3600  # 1 hora (tempo máximo de execução)
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

