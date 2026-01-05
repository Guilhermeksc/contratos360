"""Carregamento automático de fixtures XLSX para UASGs/ComimSups."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import ComimSup, Uasg

logger = logging.getLogger(__name__)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def _as_int(value, default: Optional[int] = None) -> Optional[int]:
	if pd.isna(value) or value is None:
		return default
	try:
		if isinstance(value, (int, float)):
			return int(value)
		return int(float(str(value).strip()))
	except (TypeError, ValueError):
		return default


def _as_bool(value, default: bool = False) -> bool:
	if pd.isna(value) or value is None:
		return default
	if isinstance(value, bool):
		return value
	if isinstance(value, (int, float)):
		return bool(int(value))

	normalized = str(value).strip().lower()
	if not normalized:
		return default
	return normalized in {"true", "1", "sim", "s", "yes", "y"}


def _as_str(value) -> Optional[str]:
	if pd.isna(value) or value is None:
		return None
	text = str(value).strip()
	return text or None


def _load_dataframe(filename: str, required_columns: Iterable[str]):
	path = FIXTURE_DIR / filename
	if not path.exists():
		logger.warning("📂 Arquivo %s não encontrado em %s", filename, FIXTURE_DIR)
		return None

	try:
		df = pd.read_excel(path)
	except Exception as exc:  # pragma: no cover - log detalhado
		logger.exception("❌ Falha ao ler %s: %s", filename, exc)
		return None

	df.columns = [col.strip().lower() for col in df.columns]

	missing = [col for col in required_columns if col not in df.columns]
	if missing:
		logger.error("❌ Colunas obrigatórias ausentes em %s: %s", filename, missing)
		logger.error("📋 Cabeçalho disponível: %s", list(df.columns))
		return None

	logger.info("📄 %s carregado (%d linhas)", filename, len(df))
	return df


def _lookup_value(row, candidates: Iterable[str]) -> Optional[str]:
	for key in candidates:
		if key in row and not pd.isna(row[key]):
			return _as_str(row[key])
	return None


def _load_comimsups():
	df = _load_dataframe(
		"comimsup.xlsx",
		required_columns=("uasg", "sigla_comimsup", "indicativo_comimsup", "nome_comimsup"),
	)
	if df is None:
		return

	created = 0
	for _, row in df.iterrows():
		uasg_code = _as_str(row.get("uasg"))
		if not uasg_code:
			logger.warning("⏭️ Linha ignorada em comimsup.xlsx: campo 'uasg' vazio")
			continue

		obj, was_created = ComimSup.objects.update_or_create(
			uasg=uasg_code,
			defaults={
				"sigla_comimsup": _as_str(row.get("sigla_comimsup")) or "",
				"indicativo_comimsup": _as_str(row.get("indicativo_comimsup")) or "",
				"nome_comimsup": _as_str(row.get("nome_comimsup")) or "",
			},
		)
		if was_created:
			created += 1
			logger.debug("✅ Criado ComimSup %s (%s)", obj.sigla_comimsup, obj.uasg)

	logger.info("✅ ComimSup: %d registros processados (%d novos)", len(df), created)


def _load_uasgs():
	df = _load_dataframe(
		"organizacao_militar.xlsx",
		required_columns=("id_uasg", "uasg", "sigla_om"),
	)
	if df is None:
		return

	text_fields = [
		"nome_om",
		"indicativo_om",
		"sigla_om",
		"uf",
		"cidade",
		"bairro",
		"classificacao",
		"endereco",
		"cep",
		"secom",
		"cnpj",
		"ddi",
		"ddd",
		"telefone",
		"intranet",
		"internet",
		"distrito",
		"ods",
	]
	bool_fields = ["uasg_centralizadora", "uasg_centralizada", "situacao", "ativa"]

	processed = 0
	created = 0

	for idx, row in df.iterrows():
		row_number = idx + 2  # cabeçalho ocupa a primeira linha
		id_uasg = _as_int(row.get("id_uasg"))
		uasg_code = _as_int(row.get("uasg"))

		if id_uasg is None or uasg_code is None:
			logger.warning(
				"⏭️ Linha %s ignorada em organizacao_militar.xlsx (id_uasg=%s, uasg=%s)",
				row_number,
				row.get("id_uasg"),
				row.get("uasg"),
			)
			continue

		defaults = {field: _as_str(row.get(field)) for field in text_fields}
		defaults.update({field: _as_bool(row.get(field)) for field in bool_fields})

		comimsup_code = _lookup_value(
			row,
			("comimsup_uasg", "uasg_comimsup", "comimsup"),
		)
		comimsup_obj = None
		if comimsup_code:
			comimsup_obj = ComimSup.objects.filter(uasg=comimsup_code).first()
			if comimsup_obj is None:
				logger.warning(
					"⚠️ Linha %s: ComimSup com UASG=%s não encontrado",
					row_number,
					comimsup_code,
				)
		defaults["comimsup"] = comimsup_obj

		obj, was_created = Uasg.objects.update_or_create(
			id_uasg=id_uasg,
			defaults={"uasg": uasg_code, **defaults},
		)

		processed += 1
		if was_created:
			created += 1
			logger.debug("✅ Criada/atualizada UASG %s (%s)", obj.sigla_om, obj.uasg)

	logger.info(
		"✅ UASGs: %d registros processados (%d novos)",
		processed,
		created,
	)


@receiver(post_migrate)
def load_fixtures_uasgs(sender, **kwargs):
	"""Carrega as planilhas padrão logo após as migrações do app."""

	if sender.name != "django_licitacao360.apps.uasgs":
		return

	logger.info("📥 Iniciando carga automática de ComimSup e UASGs...")

	try:
		with transaction.atomic():
			_load_comimsups()
			_load_uasgs()
	except Exception as exc:  # pragma: no cover - log detalhado
		logger.exception("❌ Erro ao carregar fixtures de UASG: %s", exc)
	else:
		logger.info("🎉 Fixtures de UASG processadas com sucesso!")
