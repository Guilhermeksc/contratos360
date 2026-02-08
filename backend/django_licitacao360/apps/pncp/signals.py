"""Carregamento automático de fixtures JSON para AmparoLegal, Modalidade e ModoDisputa."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.dateparse import parse_datetime

from .models import AmparoLegal, Modalidade, ModoDisputa

logger = logging.getLogger(__name__)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def _parse_datetime(value: Optional[str]) -> Optional:
    """Converte string de data para datetime ou retorna None."""
    if not value:
        return None
    try:
        return parse_datetime(str(value))
    except (ValueError, TypeError):
        return None


def _as_bool(value, default: bool = False) -> bool:
    """Converte valor para boolean."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if not normalized:
        return default
    return normalized in {"true", "1", "sim", "s", "yes", "y"}


def _load_json_fixture(filename: str):
    """Carrega um arquivo JSON do diretório de fixtures."""
    path = FIXTURE_DIR / filename
    if not path.exists():
        logger.warning("📂 Arquivo %s não encontrado em %s", filename, FIXTURE_DIR)
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("📄 %s carregado (%d registros)", filename, len(data) if isinstance(data, list) else 1)
        return data
    except Exception as exc:
        logger.exception("❌ Falha ao ler %s: %s", filename, exc)
        return None


def _load_amparos_legais():
    """Carrega os amparos legais do fixture JSON."""
    data = _load_json_fixture("amparolegal.json")
    if data is None:
        return

    created = 0
    for item in data:
        try:
            obj, was_created = AmparoLegal.objects.update_or_create(
                id=item["id"],
                defaults={
                    "nome": item.get("nome", ""),
                    "descricao": item.get("descricao") or "",
                    "data_inclusao": _parse_datetime(item.get("dataInclusao")),
                    "data_atualizacao": _parse_datetime(item.get("dataAtualizacao")),
                    "status_ativo": _as_bool(item.get("statusAtivo"), True),
                },
            )
            if was_created:
                created += 1
                logger.debug("✅ Criado AmparoLegal %s (%s)", obj.id, obj.nome)
        except Exception as exc:
            logger.error("❌ Erro ao processar AmparoLegal id=%s: %s", item.get("id"), exc)

    logger.info("✅ AmparoLegal: %d registros processados (%d novos)", len(data), created)


def _load_modalidades():
    """Carrega as modalidades do fixture JSON."""
    data = _load_json_fixture("modalidade.json")
    if data is None:
        return

    created = 0
    for item in data:
        try:
            obj, was_created = Modalidade.objects.update_or_create(
                id=item["id"],
                defaults={
                    "nome": item.get("nome", ""),
                    "descricao": item.get("descricao") or "",
                    "data_inclusao": _parse_datetime(item.get("dataInclusao")),
                    "data_atualizacao": _parse_datetime(item.get("dataAtualizacao")),
                    "status_ativo": _as_bool(item.get("statusAtivo"), True),
                },
            )
            if was_created:
                created += 1
                logger.debug("✅ Criada Modalidade %s (%s)", obj.id, obj.nome)
        except Exception as exc:
            logger.error("❌ Erro ao processar Modalidade id=%s: %s", item.get("id"), exc)

    logger.info("✅ Modalidade: %d registros processados (%d novos)", len(data), created)


def _load_modos_disputa():
    """Carrega os modos de disputa do fixture JSON."""
    data = _load_json_fixture("modo_disputa.json")
    if data is None:
        return

    created = 0
    for item in data:
        try:
            obj, was_created = ModoDisputa.objects.update_or_create(
                id=item["id"],
                defaults={
                    "nome": item.get("nome", ""),
                    "descricao": item.get("descricao") or "",
                    "data_inclusao": _parse_datetime(item.get("dataInclusao")),
                    "data_atualizacao": _parse_datetime(item.get("dataAtualizacao")),
                    "status_ativo": _as_bool(item.get("statusAtivo"), True),
                },
            )
            if was_created:
                created += 1
                logger.debug("✅ Criado ModoDisputa %s (%s)", obj.id, obj.nome)
        except Exception as exc:
            logger.error("❌ Erro ao processar ModoDisputa id=%s: %s", item.get("id"), exc)

    logger.info("✅ ModoDisputa: %d registros processados (%d novos)", len(data), created)


@receiver(post_migrate)
def load_fixtures_pncp(sender, **kwargs):
    """Carrega as fixtures padrão logo após as migrações do app."""

    if sender.name != "django_licitacao360.apps.pncp":
        return

    logger.info("📥 Iniciando carga automática de AmparoLegal, Modalidade e ModoDisputa...")

    try:
        with transaction.atomic():
            _load_amparos_legais()
            _load_modalidades()
            _load_modos_disputa()
    except Exception as exc:
        logger.exception("❌ Erro ao carregar fixtures de PNCP: %s", exc)
    else:
        logger.info("🎉 Fixtures de PNCP processadas com sucesso!")
