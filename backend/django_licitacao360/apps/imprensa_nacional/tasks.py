from __future__ import annotations

import logging
from datetime import date

from celery import shared_task
from django.utils import timezone

from .services.inlabs_downloader import ingest_inlabs_articles, InlabsDownloadError

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(InlabsDownloadError,), retry_backoff=120, retry_kwargs={"max_retries": 3})
def collect_inlabs_articles(self, target_date: str | None = None) -> dict:
    """Task Celery para baixar e salvar artigos do INLABS."""

    if target_date:
        edition_date = date.fromisoformat(target_date)
    else:
        edition_date = timezone.localdate()

    logger.info("Iniciando coleta INLABS para %s", edition_date)
    result = ingest_inlabs_articles(edition_date)
    logger.info(
        "Coleta INLABS finalizada. data=%s artigos=%s", result["edition_date"], result["saved_articles"]
    )
    return result
