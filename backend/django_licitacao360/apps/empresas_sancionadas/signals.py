"""Carregamento automático de fixtures CSV para Empresas Sancionadas (CEIS)."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import EmpresasSancionadas

logger = logging.getLogger(__name__)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def _as_str(value) -> Optional[str]:
	"""Converte valor para string, retornando None se vazio."""
	if pd.isna(value) or value is None:
		return None
	text = str(value).strip()
	return text if text else None


def _as_date(value) -> Optional[datetime]:
	"""Converte string de data para objeto datetime."""
	if pd.isna(value) or value is None:
		return None
	
	text = str(value).strip()
	if not text or text.lower() in ("sem informação", "sem informacao", ""):
		return None
	
	# Tenta formatos comuns de data brasileira
	date_formats = [
		"%d/%m/%Y",
		"%d-%m-%Y",
		"%Y-%m-%d",
		"%d/%m/%y",
	]
	
	for fmt in date_formats:
		try:
			return datetime.strptime(text, fmt).date()
		except ValueError:
			continue
	
	logger.warning(f"⚠️ Não foi possível converter data: {text}")
	return None


def _load_ceis_csv():
	"""Carrega dados do arquivo CSV do CEIS."""
	csv_path = FIXTURE_DIR / "ceis.csv"
	
	if not csv_path.exists():
		logger.warning(f"📂 Arquivo ceis.csv não encontrado em {FIXTURE_DIR}")
		return
	
	try:
		# Lê CSV com separador ponto e vírgula e encoding latin-1
		df = pd.read_csv(
			csv_path,
			sep=";",
			encoding="latin-1",
			low_memory=False,
		)
	except Exception as exc:
		logger.exception(f"❌ Falha ao ler ceis.csv: {exc}")
		return
	
	# Normaliza nomes das colunas (remove espaços e converte para minúsculas)
	df.columns = df.columns.str.strip().str.lower()
	
	# Função auxiliar para encontrar coluna por palavras-chave (ignora encoding)
	def find_column(keywords):
		"""Encontra uma coluna usando palavras-chave, ignorando problemas de encoding."""
		keywords_lower = [k.lower().strip() for k in keywords]
		best_match = None
		best_score = 0
		
		for col in df.columns:
			col_lower = col.lower().strip()
			# Conta quantas palavras-chave estão presentes
			matches = sum(1 for kw in keywords_lower if kw in col_lower)
			# Se todas as palavras-chave estão presentes, é um match perfeito
			if matches == len(keywords_lower):
				return col
			# Mantém o melhor match parcial
			if matches > best_score:
				best_score = matches
				best_match = col
		
		# Retorna o melhor match se encontrou pelo menos uma palavra-chave
		return best_match if best_score > 0 else None
	
	# Mapeia campos do modelo para palavras-chave das colunas
	field_mapping = {
		"cadastro": ["cadastro"],
		"codigo_sancao": ["código", "sanção"],
		"tipo_pessoa": ["tipo", "pessoa"],
		"cpf_cnpj": ["cpf", "cnpj", "sancionado"],
		"nome_sancionado": ["nome", "sancionado"],
		"nome_orgao_sancionador": ["nome", "informado", "órgão", "sancionador"],
		"razao_social": ["razão", "social", "cadastro", "receita"],
		"nome_fantasia": ["nome", "fantasia", "cadastro", "receita"],
		"numero_processo": ["número", "processo"],
		"categoria_sancao": ["categoria", "sanção"],
		"data_inicio_sancao": ["data", "início", "sanção"],
		"data_final_sancao": ["data", "final", "sanção"],
		"data_publicacao": ["data", "publicação"],
		"publicacao": ["publicação"],
		"detalhamento_meio_publicacao": ["detalhamento", "meio", "publicação"],
		"data_transito_julgado": ["data", "trânsito", "julgado"],
		"abrangencia_sancao": ["abrangência", "sanção"],
		"orgao_sancionador": ["órgão", "sancionador"],
		"uf_orgao_sancionador": ["uf", "órgão", "sancionador"],
		"esfera_orgao_sancionador": ["esfera", "órgão", "sancionador"],
		"fundamentacao_legal": ["fundamentação", "legal"],
		"data_origem_informacao": ["data", "origem", "informação"],
		"origem_informacoes": ["origem", "informações"],
		"observacoes": ["observações"],
	}
	
	# Cria mapeamento de colunas reais para campos do modelo
	column_to_field = {}
	for field_name, keywords in field_mapping.items():
		col = find_column(keywords)
		if col:
			column_to_field[col] = field_name
		else:
			logger.warning(f"⚠️ Coluna não encontrada para campo {field_name} (keywords: {keywords})")
	
	logger.info(f"📋 Colunas mapeadas: {len(column_to_field)}/{len(field_mapping)}")
	logger.debug(f"📋 Mapeamento: {column_to_field}")
	
	processed = 0
	created = 0
	updated = 0
	
	logger.info(f"📄 Processando {len(df)} registros do CEIS...")
	
	for idx, row in df.iterrows():
		try:
			# Busca o código da sanção (chave única)
			codigo_sancao_col = None
			for col_name, field_name in column_to_field.items():
				if field_name == "codigo_sancao":
					codigo_sancao_col = col_name
					break
			
			if not codigo_sancao_col:
				# Tenta encontrar diretamente
				codigo_sancao_col = find_column(["código", "sanção"])
			
			if codigo_sancao_col and codigo_sancao_col in df.columns:
				codigo_sancao = _as_str(row.get(codigo_sancao_col))
			else:
				codigo_sancao = None
			
			if not codigo_sancao:
				logger.warning(f"⏭️ Linha {idx + 2} ignorada: código da sanção não encontrado")
				continue
			
			# Prepara dados para o modelo
			defaults = {}
			
			# Processa cada campo usando o mapeamento
			for col_name, field_name in column_to_field.items():
				if col_name in df.columns:
					value = row.get(col_name)
					
					# Campos de data
					if field_name.startswith("data_"):
						date_value = _as_date(value)
						if date_value:
							defaults[field_name] = date_value
					# Campos de texto
					else:
						str_value = _as_str(value)
						if str_value:
							defaults[field_name] = str_value
			
			# Cria ou atualiza o registro
			obj, was_created = EmpresasSancionadas.objects.update_or_create(
				codigo_sancao=codigo_sancao,
				defaults=defaults,
			)
			
			processed += 1
			if was_created:
				created += 1
			else:
				updated += 1
			
			if (idx + 1) % 1000 == 0:
				logger.info(f"📊 Processados {idx + 1}/{len(df)} registros...")
		
		except Exception as exc:
			logger.exception(f"❌ Erro ao processar linha {idx + 2}: {exc}")
			continue
	
	logger.info(
		f"✅ CEIS: {processed} registros processados "
		f"({created} novos, {updated} atualizados)"
	)


@receiver(post_migrate)
def load_fixtures_ceis(sender, **kwargs):
	"""Carrega o arquivo CSV do CEIS logo após as migrações do app."""
	
	if sender.name != "django_licitacao360.apps.empresas_sancionadas":
		return
	
	logger.info("📥 Iniciando carga automática de dados do CEIS...")
	
	try:
		with transaction.atomic():
			_load_ceis_csv()
	except Exception as exc:
		logger.exception(f"❌ Erro ao carregar fixtures do CEIS: {exc}")
	else:
		logger.info("🎉 Fixtures do CEIS processadas com sucesso!")
