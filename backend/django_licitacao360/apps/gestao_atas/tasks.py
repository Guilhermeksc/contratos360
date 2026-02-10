"""
Tasks do Celery para atualização de dados do PNCP
"""
import asyncio
import json
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from asgiref.sync import sync_to_async

from .models import AmparoLegal, Compra, ItemCompra, Modalidade, ModoDisputa, ResultadoItem, Fornecedor

logger = logging.getLogger(__name__)

PNCP_BASE = "https://pncp.gov.br/api/consulta/v1"
HEADERS = {
    "User-Agent": "curl/8.8",
    "Accept": "application/json",
}

# CNPJ padrão do órgão (pode ser configurado via variável de ambiente)
DEFAULT_CNPJ = "00394502000144"

# Mapeamento de modalidades do PNCP
MODALIDADES = {
    1: "Leilão - Eletrônico",
    2: "Diálogo Competitivo",
    3: "Concurso",
    4: "Concorrência - Eletrônica",
    5: "Concorrência - Presencial",
    6: "Pregão - Eletrônico",
    7: "Pregão - Presencial",
    8: "Dispensa de Licitação",
    9: "Inexigibilidade",
    10: "Manifestação de Interesse",
    11: "Pré-qualificação",
    12: "Credenciamento",
    13: "Leilão - Presencial",
    14: "Inaplicabilidade da Licitação",
    15: "Chamada pública",
}

# Todas as modalidades a serem consultadas (1 a 13)
# Pode ser configurado via variável de ambiente PNCP_MODALIDADES (separado por vírgula)
# Exemplo: PNCP_MODALIDADES="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"
DEFAULT_MODALIDADES = list(MODALIDADES.keys())  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
