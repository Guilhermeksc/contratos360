from __future__ import annotations

import logging
from datetime import date
from urllib.parse import urlparse

from celery import shared_task
from django.conf import settings
from django.db import connections
from django.utils import timezone
import redis

from .services.inlabs_downloader import ingest_inlabs_articles, InlabsDownloadError

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


@shared_task(bind=True, autoretry_for=(InlabsDownloadError,), retry_backoff=120, retry_kwargs={"max_retries": 3})
def collect_inlabs_articles(self, target_date: str | None = None) -> dict:
    """
    Task Celery para baixar e salvar artigos do INLABS.
    
    Usa lock distribuído para evitar execuções simultâneas da mesma data.
    """
    if target_date:
        edition_date = date.fromisoformat(target_date)
    else:
        edition_date = timezone.localdate()

    lock_key = f"inlabs:lock:{edition_date.isoformat()}"
    lock_timeout = 3600  # 1 hora (tempo máximo de execução)
    redis_client = get_redis_client()

    # Tenta adquirir lock distribuído
    lock_acquired = redis_client.set(lock_key, "locked", nx=True, ex=lock_timeout)
    
    if not lock_acquired:
        logger.warning(
            "Coleta INLABS já em execução para %s. Ignorando execução duplicada.",
            edition_date
        )
        return {
            "edition_date": edition_date.isoformat(),
            "skipped": True,
            "reason": "Já existe uma execução em andamento para esta data",
        }

    try:
        logger.info("Iniciando coleta INLABS para %s", edition_date)
        result = ingest_inlabs_articles(edition_date)
        
        # Garantir que as transações foram commitadas
        connections.close_all()
        
        logger.info(
            "Coleta INLABS finalizada. data=%s artigos=%s avisos=%s credenciamentos=%s",
            result["edition_date"],
            result["saved_articles"],
            result.get("saved_avisos", 0),
            result.get("saved_credenciamentos", 0),
        )
        return result
    except Exception as exc:
        logger.error("Erro ao coletar artigos INLABS para %s: %s", edition_date, exc, exc_info=True)
        raise
    finally:
        # Remove o lock ao finalizar (mesmo em caso de erro)
        try:
            redis_client.delete(lock_key)
        except Exception as exc:
            logger.warning("Erro ao remover lock %s: %s", lock_key, exc)
        # Garantir fechamento de conexões
        connections.close_all()
