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


def _to_decimal(value: Any) -> Optional[Decimal]:
    """Converte valor para Decimal"""
    if value in (None, "", "null"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    """Converte string de data para datetime timezone-aware"""
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = timezone.make_aware(dt)
        return dt
    except ValueError:
        # tenta formatos sem timezone
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                dt = datetime.strptime(text, fmt)
                return timezone.make_aware(dt)
            except ValueError:
                continue
    return None


async def _get_publications_page(
    session: aiohttp.ClientSession,
    params: Dict[str, str],
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Faz GET assíncrono com retry/backoff simples.
    Retorna (payload_json, erro_str)
    """
    url = f"{PNCP_BASE}/contratacoes/publicacao"
    timeout = aiohttp.ClientTimeout(total=60)
    # Log da URL completa para debug
    url_with_params = f"{url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    logger.debug(f"[PNCP Task] GET {url_with_params}")
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, params=params, headers=HEADERS, timeout=timeout) as resp:
                if resp.status != 200:
                    body = (await resp.text())[:240]
                    err = f"API {resp.status}: {body}"
                    if attempt < max_retries and resp.status in (500, 502, 503, 504):
                        await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
                        continue
                    return None, err
                ct = (resp.headers.get("Content-Type") or "").lower()
                if "application/json" not in ct:
                    preview = (await resp.text())[:240].replace("\n", " ")
                    return None, f"Content-Type inesperado ({ct}). Body[:240]={preview!r}"
                data = await resp.json()
                return data, None
        except aiohttp.ClientError as e:
            if attempt < max_retries:
                await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
                continue
            return None, f"ClientError: {repr(e)}"
        except asyncio.TimeoutError as e:
            if attempt < max_retries:
                await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
                continue
            return None, f"TimeoutError: {repr(e)}"
        except json.JSONDecodeError as e:
            return None, f"JSONDecodeError: {repr(e)}"
    return None, "Erro desconhecido"


def _get_modalidade_sync(modalidade_id: Optional[int]) -> Optional[Modalidade]:
    """Busca modalidade por ID"""
    if not modalidade_id:
        return None
    try:
        return Modalidade.objects.get(id=modalidade_id)
    except Modalidade.DoesNotExist:
        return None


def _get_amparo_legal_sync(amparo_id: Optional[int]) -> Optional[AmparoLegal]:
    """Busca amparo legal por ID"""
    if not amparo_id:
        return None
    try:
        return AmparoLegal.objects.get(id=amparo_id)
    except AmparoLegal.DoesNotExist:
        return None


def _get_modo_disputa_sync(modo_disputa_id: Optional[int]) -> Optional[ModoDisputa]:
    """Busca modo de disputa por ID"""
    if not modo_disputa_id:
        return None
    try:
        return ModoDisputa.objects.get(id=modo_disputa_id)
    except ModoDisputa.DoesNotExist:
        return None


def _save_compras_sync(compras_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Função síncrona para salvar compras no banco de dados.
    Esta função será chamada via sync_to_async dentro do contexto assíncrono.
    """
    totals = {"compras": 0, "ignoradas": 0}
    if not compras_data:
        return totals
    
    with transaction.atomic():
        for compra_data in compras_data:
            try:
                # Extrai IDs dos relacionamentos antes de salvar
                modalidade_id = compra_data.pop("modalidade_id", None)
                amparo_legal_id = compra_data.pop("amparo_legal_id", None)
                modo_disputa_id = compra_data.pop("modo_disputa_id", None)
                
                # Busca os objetos relacionados
                modalidade = _get_modalidade_sync(modalidade_id) if modalidade_id else None
                amparo_legal = _get_amparo_legal_sync(amparo_legal_id) if amparo_legal_id else None
                modo_disputa = _get_modo_disputa_sync(modo_disputa_id) if modo_disputa_id else None
                
                # Adiciona os objetos relacionados aos defaults
                defaults = dict(compra_data)
                defaults["modalidade"] = modalidade
                defaults["amparo_legal"] = amparo_legal
                defaults["modo_disputa"] = modo_disputa
                
                Compra.objects.update_or_create(
                    compra_id=compra_data["compra_id"],
                    defaults=defaults
                )
                totals["compras"] += 1
            except Exception as e:
                logger.error(
                    f"[PNCP Task] Erro ao salvar compra {compra_data.get('compra_id', 'N/A')}: {e}"
                )
                totals["ignoradas"] += 1
    return totals


# Versão assíncrona da função de salvamento
# thread_sensitive=False permite que operações de banco sejam executadas em thread separada
_save_compras_async = sync_to_async(_save_compras_sync, thread_sensitive=False)


def _extract_list(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Extrai a lista de publicações e info de paginação.
    """
    pubs = payload.get("publicacoes")
    if not pubs:
        pubs = payload.get("data")
    if not pubs:
        pubs = payload.get("content")
    if not isinstance(pubs, list):
        pubs = []
    total_paginas = int(payload.get("totalPaginas") or 1)
    numero_pagina = int(payload.get("numeroPagina") or 1)
    return pubs, total_paginas, numero_pagina


def _process_publicacao(p: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Processa uma publicação e retorna os dados da compra para salvar.
    """
    ano = int(p.get("anoCompra") or 0)
    seq = int(p.get("sequencialCompra") or 0)
    codigo_unidade = (p.get("unidadeOrgao") or {}).get("codigoUnidade")
    
    if not (ano and seq and codigo_unidade):
        return None
    
    numero_compra = p.get("numeroCompra")
    modalidade_id = p.get("modalidadeId")
    amparo_legal_data = p.get("amparoLegal")
    amparo_legal_id = amparo_legal_data.get("codigo") if isinstance(amparo_legal_data, dict) else None
    modo_disputa_id = p.get("modoDisputaId")
    objeto_compra = p.get("objeto") or p.get("objetoCompra")
    processo_adm = (
        p.get("processo")
        or p.get("numeroProcesso")
        or p.get("numeroProcessoCompra")
        or p.get("processoCompra")
    )
    if processo_adm:
        processo_adm = str(processo_adm).strip()
    
    data_publicacao = _parse_date(
        p.get("dataPublicacaoPncp") or p.get("dataPublicacao")
    )
    data_atualizacao = _parse_date(
        p.get("dataAtualizacao") or p.get("dataAtualizacaoPncp")
    )
    valor_total_estimado = _to_decimal(p.get("valorTotalEstimado"))
    valor_total_homologado = _to_decimal(p.get("valorTotalHomologado"))
    
    # Calcula percentual de desconto
    percentual_desconto = None
    if (
        valor_total_estimado is not None
        and valor_total_homologado is not None
        and valor_total_estimado > 0
    ):
        percentual_desconto = (
            (valor_total_estimado - valor_total_homologado) / valor_total_estimado
        ) * Decimal("100")
    
    # Gera compra_id no formato "ano::sequencial"
    compra_id = f"{ano}::{seq}"
    
    return {
        "compra_id": compra_id,
        "ano_compra": ano,
        "sequencial_compra": seq,
        "numero_compra": numero_compra or "",
        "codigo_unidade": codigo_unidade,
        "objeto_compra": objeto_compra or "",
        "modalidade_id": modalidade_id,
        "amparo_legal_id": amparo_legal_id,
        "modo_disputa_id": modo_disputa_id,
        "numero_processo": processo_adm or "",
        "data_publicacao_pncp": data_publicacao,
        "data_atualizacao": data_atualizacao,
        "valor_total_estimado": valor_total_estimado,
        "valor_total_homologado": valor_total_homologado,
        "percentual_desconto": percentual_desconto,
    }


async def _fetch_and_process_publications(
    data_inicial: str,
    data_final: str,
    modalidade: int,
    cnpj: str,
    unidade: Optional[str] = None,
) -> Dict[str, int]:
    """
    Busca publicações da API do PNCP e processa todas as páginas.
    Retorna contadores: {'compras': X, 'ignoradas': Y, 'paginas': N}
    """
    logger.info(
        f"[PNCP Task] Iniciando coleta de publicações - "
        f"dataInicial={data_inicial}, dataFinal={data_final}, "
        f"modalidade={modalidade}, cnpj={cnpj}, unidade={unidade or '-'}"
    )
    
    # Garante que modalidade é um inteiro válido
    modalidade_int = int(modalidade) if modalidade else None
    if not modalidade_int:
        logger.error(f"[PNCP Task] Modalidade inválida: {modalidade}")
        return {"compras": 0, "ignoradas": 0, "paginas": 0}
    
    base_params = {
        "dataInicial": data_inicial.replace("-", ""),
        "dataFinal": data_final.replace("-", ""),
        "codigoModalidadeContratacao": str(modalidade_int),
        "cnpj": cnpj,
        "pagina": "1",
    }
    if unidade and unidade not in {"0", "1", "-", ""}:
        base_params["codigoUnidadeAdministrativa"] = unidade
    
    # Log dos parâmetros para debug
    logger.info(f"[PNCP Task] Parâmetros da requisição: {base_params}")
    
    totals = {"compras": 0, "ignoradas": 0, "paginas": 0}
    compras_data = {}  # Usado para deduplicação: {(ano, seq): dados}
    
    async with aiohttp.ClientSession(trust_env=True) as session:
        # Busca primeira página
        params = dict(base_params)
        params["pagina"] = "1"
        payload, err = await _get_publications_page(session, params)
        
        if err:
            logger.error(f"[PNCP Task] Falha ao buscar página 1: {err}")
            return totals
        
        pubs, total_paginas, numero_pagina = _extract_list(payload)
        logger.info(f"[PNCP Task] Total de páginas: {total_paginas}")
        
        # Processa primeira página
        for p in pubs:
            compra_data = _process_publicacao(p)
            if compra_data:
                key = (compra_data["ano_compra"], compra_data["sequencial_compra"])
                compras_data[key] = compra_data  # Mantém a última ocorrência
            else:
                totals["ignoradas"] += 1
        totals["paginas"] += 1
        
        # Busca páginas restantes em paralelo
        if total_paginas > 1:
            sem = asyncio.Semaphore(10)
            
            async def fetch_page(pg: int):
                params = dict(base_params)
                params["pagina"] = str(pg)
                async with sem:
                    payload, err = await _get_publications_page(session, params)
                return pg, payload, err
            
            tasks = [
                asyncio.create_task(fetch_page(pg))
                for pg in range(2, total_paginas + 1)
            ]
            
            for coro in asyncio.as_completed(tasks):
                pg, payload, err = await coro
                if err:
                    logger.warning(f"[PNCP Task] Falha ao buscar página {pg}: {err}")
                    totals["ignoradas"] += 1
                    continue
                
                pubs, _, _ = _extract_list(payload)
                for p in pubs:
                    compra_data = _process_publicacao(p)
                    if compra_data:
                        key = (compra_data["ano_compra"], compra_data["sequencial_compra"])
                        compras_data[key] = compra_data
                    else:
                        totals["ignoradas"] += 1
                totals["paginas"] += 1
        
        # Salva no banco usando Django ORM (função síncrona)
        if compras_data:
            totals_saved = await _save_compras_async(list(compras_data.values()))
            totals["compras"] += totals_saved["compras"]
            totals["ignoradas"] += totals_saved["ignoradas"]
    
    logger.info(
        f"[PNCP Task] Concluído - compras={totals['compras']}, "
        f"ignoradas={totals['ignoradas']}, páginas={totals['paginas']}"
    )
    return totals


@shared_task(bind=True, name="django_licitacao360.apps.pncp.tasks.task_atualizacao_seq_pncp")
def task_atualizacao_seq_pncp(self, cnpj: Optional[str] = None, modalidades: Optional[List[int]] = None):
    """
    Task do Celery para atualizar dados dos sequenciais dos últimos 10 dias.
    
    A task busca publicações do PNCP dos últimos 10 dias (incluindo o dia atual)
    para todas as modalidades configuradas.
    
    Args:
        cnpj: CNPJ do órgão (padrão: DEFAULT_CNPJ)
        modalidades: Lista de códigos de modalidades (padrão: todas as 13 modalidades)
    """
    import os
    
    cnpj = cnpj or os.getenv("PNCP_CNPJ", DEFAULT_CNPJ)
    
    # Processa modalidades da variável de ambiente ou usa padrão
    if modalidades is None:
        modalidades_str = os.getenv("PNCP_MODALIDADES", None)
        if modalidades_str:
            modalidades = [int(m.strip()) for m in modalidades_str.split(",") if m.strip()]
        else:
            modalidades = DEFAULT_MODALIDADES
    
    # Calcula datas: últimos 10 dias (incluindo o dia atual)
    hoje = timezone.now().date()
    data_inicial_dt = hoje - timedelta(days=9)  # 9 dias atrás + hoje = 10 dias
    
    data_inicial = data_inicial_dt.strftime("%Y-%m-%d")
    data_final = hoje.strftime("%Y-%m-%d")
    
    logger.info(
        f"[PNCP Task] Iniciando atualização - "
        f"data_inicial={data_inicial}, data_final={data_final} "
        f"(últimos 10 dias), cnpj={cnpj}, modalidades={modalidades}"
    )
    
    try:
        # Executa a função assíncrona para cada modalidade
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            total_geral = {"compras": 0, "ignoradas": 0, "paginas": 0}
            
            # Processa cada modalidade sequencialmente
            for modalidade in modalidades:
                modalidade_nome = MODALIDADES.get(modalidade, f"Modalidade {modalidade}")
                logger.info(
                    f"[PNCP Task] Processando modalidade {modalidade} - {modalidade_nome}"
                )
                totals = loop.run_until_complete(
                    _fetch_and_process_publications(
                        data_inicial=data_inicial,
                        data_final=data_final,
                        modalidade=modalidade,
                        cnpj=cnpj,
                    )
                )
                # Acumula totais
                total_geral["compras"] += totals.get("compras", 0)
                total_geral["ignoradas"] += totals.get("ignoradas", 0)
                total_geral["paginas"] += totals.get("paginas", 0)
                logger.info(
                    f"[PNCP Task] Modalidade {modalidade} ({modalidade_nome}) concluída - "
                    f"compras={totals.get('compras', 0)}, "
                    f"ignoradas={totals.get('ignoradas', 0)}, "
                    f"páginas={totals.get('paginas', 0)}"
                )
            
            logger.info(f"[PNCP Task] Sucesso geral - {total_geral}")
            return total_geral
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"[PNCP Task] Erro durante execução: {e}", exc_info=True)
        raise


# ============================================================================
# Task para buscar itens das compras (Etapa 2)
# ============================================================================

PNCP_API_BASE = "https://pncp.gov.br/api/pncp/v1"
MAX_CONCURRENCY_ITENS = 5
MAX_RETRIES_ITENS = 5
PAGE_SIZE_ITENS = 999_999_999  # força a API a retornar todos os itens em uma única página


def _get_compra_sync(ano: int, seq: int) -> Optional[Compra]:
    """
    Busca uma compra específica no banco de dados.
    """
    try:
        return Compra.objects.get(ano_compra=ano, sequencial_compra=seq)
    except Compra.DoesNotExist:
        return None
    except Compra.MultipleObjectsReturned:
        logger.warning(f"[PNCP Itens] Múltiplas compras encontradas para {ano}/{seq}")
        return Compra.objects.filter(ano_compra=ano, sequencial_compra=seq).first()


_get_compra_async = sync_to_async(_get_compra_sync, thread_sensitive=False)


def _get_compras_para_itens_sync(
    data_inicial: datetime,
    data_final: datetime,
    modalidades: List[str],
    cnpj: str,
) -> List[Dict[str, Any]]:
    """
    Busca compras no banco de dados usando Django ORM.
    Retorna lista de compras com informações necessárias para buscar itens.
    Como todas as compras são do mesmo CNPJ, apenas filtramos por data e modalidade.
    """
    # Converte nomes de modalidades para IDs
    modalidades_ids = []
    for modalidade_nome in modalidades:
        modalidade_obj = Modalidade.objects.filter(nome=modalidade_nome).first()
        if modalidade_obj:
            modalidades_ids.append(modalidade_obj.id)
    
    queryset = Compra.objects.filter(
        data_publicacao_pncp__gte=data_inicial,
        data_publicacao_pncp__lte=data_final,
    )
    if modalidades_ids:
        queryset = queryset.filter(modalidade_id__in=modalidades_ids)
    queryset = queryset.order_by("-ano_compra", "-sequencial_compra")
    
    compras = []
    for compra in queryset:
        compras.append({
            "ano_compra": compra.ano_compra,
            "sequencial_compra": compra.sequencial_compra,
            "codigo_unidade": compra.codigo_unidade,
            "orgao_cnpj": cnpj,  # Usa o CNPJ passado como parâmetro (todos são do mesmo órgão)
            "compra": compra,  # Mantém referência ao objeto Compra para usar depois
        })
    
    return compras


_get_compras_para_itens_async = sync_to_async(_get_compras_para_itens_sync, thread_sensitive=False)


def _to_decimal_itens(value: Optional[Any]) -> Optional[Decimal]:
    """Converte valor para Decimal"""
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


async def _fetch_itens_api(
    session: aiohttp.ClientSession,
    orgao_cnpj: str,
    ano: int,
    seq: int,
    max_retries: int = MAX_RETRIES_ITENS,
) -> List[Dict[str, Any]]:
    """
    Busca itens de uma compra específica da API do PNCP.
    """
    url = f"{PNCP_API_BASE}/orgaos/{orgao_cnpj}/compras/{ano}/{seq}/itens"
    params = {"tamanhoPagina": PAGE_SIZE_ITENS}
    
    logger.debug(f"[PNCP Itens] GET {url} params={params}")
    
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, timeout=60, params=params, headers=HEADERS) as resp:
                logger.debug(
                    f"[PNCP Itens] Resposta {resp.status} para {ano}/{seq} (tentativa {attempt}/{max_retries})"
                )
                
                if resp.status == 404:
                    logger.debug(f"[PNCP Itens] Nenhum item (404) para {ano}/{seq}")
                    return []
                
                if resp.status == 429:
                    retry_after = resp.headers.get("Retry-After")
                    wait = (
                        int(retry_after)
                        if retry_after and retry_after.isdigit()
                        else 2 ** attempt
                    )
                    logger.debug(
                        f"[PNCP Itens] Rate limit para {ano}/{seq}; aguardando {wait}s antes de retry"
                    )
                    await asyncio.sleep(wait)
                    continue
                
                resp.raise_for_status()
                data = await resp.json()
                
                # A API pode retornar lista direta ou objeto com 'data'
                itens = data if isinstance(data, list) else data.get("data", [])
                logger.debug(
                    f"[PNCP Itens] Itens recebidos para {ano}/{seq}: {len(itens)}"
                )
                return itens
                
        except asyncio.CancelledError:
            logger.debug(f"[PNCP Itens] Cancelado durante fetch {ano}/{seq}")
            raise
        except aiohttp.ClientError as e:
            logger.warning(
                f"[PNCP Itens] Erro de rede em {ano}/{seq} (tentativa {attempt}/{max_retries}): {e}"
            )
            if attempt == max_retries:
                raise
            await asyncio.sleep(2 ** attempt)
    
    raise RuntimeError(f"[PNCP Itens] Falha após {max_retries} tentativas para {ano}/{seq}")


async def _worker_itens(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    compra_info: Dict[str, Any],
) -> Tuple[int, int, List[Dict[str, Any]], Optional[str]]:
    """
    Worker assíncrono para buscar itens de uma compra.
    """
    ano = compra_info["ano_compra"]
    seq = compra_info["sequencial_compra"]
    cnpj = compra_info["orgao_cnpj"]
    
    try:
        logger.debug(f"[PNCP Itens] Iniciando worker {ano}/{seq} orgao={cnpj}")
        async with sem:
            itens = await _fetch_itens_api(session, cnpj, ano, seq)
        logger.debug(f"[PNCP Itens] Worker concluído {ano}/{seq} itens={len(itens)}")
        return ano, seq, itens, None
    except asyncio.CancelledError:
        logger.debug(f"[PNCP Itens] Worker cancelado {ano}/{seq}")
        raise
    except Exception as e:
        logger.error(f"[PNCP Itens] Worker falhou {ano}/{seq}: {e}")
        return ano, seq, [], str(e)


def _save_item_sync(
    compra: Compra,
    numero_item: int,
    descricao: str,
    unidade_medida: str,
    valor_unitario_estimado: Optional[Decimal],
    valor_total_estimado: Optional[Decimal],
    quantidade: Optional[Decimal],
    situacao_compra_item_nome: str,
    tem_resultado: bool,
) -> None:
    """
    Salva ou atualiza um item de compra no banco de dados.
    """
    item_id = f"{compra.ano_compra}::{compra.sequencial_compra}::{numero_item}"
    
    # Garante que quantidade não seja None (campo não aceita null)
    quantidade_final = quantidade if quantidade is not None else Decimal("0")
    
    ItemCompra.objects.update_or_create(
        item_id=item_id,
        defaults={
            "compra": compra,
            "numero_item": numero_item,
            "descricao": descricao or "",
            "unidade_medida": unidade_medida or "",
            "valor_unitario_estimado": valor_unitario_estimado,
            "valor_total_estimado": valor_total_estimado,
            "quantidade": quantidade_final,
            "percentual_economia": None,  # Será calculado depois se necessário
            "situacao_compra_item_nome": situacao_compra_item_nome or "",
            "tem_resultado": tem_resultado,
        }
    )


_save_item_async = sync_to_async(_save_item_sync, thread_sensitive=False)


def _save_itens_batch_sync(
    itens_data: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Salva um lote de itens no banco de dados.
    """
    totals = {"itens": 0, "ignoradas": 0}
    
    if not itens_data:
        return totals
    
    with transaction.atomic():
        for item_data in itens_data:
            try:
                _save_item_sync(**item_data)
                totals["itens"] += 1
            except Exception as e:
                logger.error(
                    f"[PNCP Itens] Erro ao salvar item {item_data.get('numero_item', 'N/A')}: {e}"
                )
                totals["ignoradas"] += 1
    
    return totals


_save_itens_batch_async = sync_to_async(_save_itens_batch_sync, thread_sensitive=False)


async def _processar_itens_async(
    data_inicial: datetime,
    data_final: datetime,
    modalidades: List[str],
    cnpj: str,
) -> Dict[str, int]:
    """
    Processa itens de compras: busca compras, busca itens da API e salva no banco.
    """
    logger.info(
        f"[PNCP Itens] Iniciando processamento de itens - "
        f"data_inicial={data_inicial.date()}, data_final={data_final.date()}, "
        f"modalidades={modalidades}, cnpj={cnpj}"
    )
    
    # Busca compras do banco
    compras = await _get_compras_para_itens_async(
        data_inicial, data_final, modalidades, cnpj
    )
    
    if not compras:
        logger.info("[PNCP Itens] Nenhuma compra encontrada para buscar itens.")
        return {"itens": 0, "ignoradas": 0, "compras_processadas": 0}
    
    logger.info(f"[PNCP Itens] Compras encontradas: {len(compras)}")
    
    totals = {"itens": 0, "ignoradas": 0, "compras_processadas": 0}
    sem = asyncio.Semaphore(MAX_CONCURRENCY_ITENS)
    
    async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
        tasks = [
            asyncio.create_task(_worker_itens(session, sem, comp)) for comp in compras
        ]
        
        try:
            for t in asyncio.as_completed(tasks):
                ano, seq, itens, err = await t
                
                if err:
                    logger.warning(f"[PNCP Itens] Falha ao buscar itens {ano}/{seq}: {err}")
                    totals["ignoradas"] += 1
                    continue
                
                totals["compras_processadas"] += 1
                
                # Busca a compra no banco de dados (função síncrona)
                compra_obj = await _get_compra_async(ano, seq)
                
                if not compra_obj:
                    logger.warning(f"[PNCP Itens] Compra {ano}/{seq} não encontrada no banco")
                    totals["ignoradas"] += 1
                    continue
                
                # Processa cada item
                itens_para_salvar = []
                
                for item in itens:
                    numero_item = item.get("numeroItem")
                    if numero_item is None:
                        continue
                    
                    descricao = (
                        item.get("descricao") or item.get("descricaoItem") or ""
                    )
                    unidade = item.get("unidadeMedida") or ""
                    valor_unitario_estimado = _to_decimal_itens(
                        item.get("valorUnitarioEstimado")
                    )
                    valor_total_estimado = _to_decimal_itens(item.get("valorTotal"))
                    quantidade = _to_decimal_itens(item.get("quantidade"))
                    situacao_nome = item.get("situacaoCompraItemNome") or ""
                    tem_resultado_raw = item.get("temResultado")
                    tem_resultado = bool(tem_resultado_raw) if tem_resultado_raw is not None else False
                    
                    itens_para_salvar.append({
                        "compra": compra_obj,
                        "numero_item": int(numero_item),
                        "descricao": descricao,
                        "unidade_medida": unidade,
                        "valor_unitario_estimado": valor_unitario_estimado,
                        "valor_total_estimado": valor_total_estimado,
                        "quantidade": quantidade,
                        "situacao_compra_item_nome": situacao_nome,
                        "tem_resultado": tem_resultado,
                    })
                
                # Salva lote de itens
                if itens_para_salvar:
                    batch_totals = await _save_itens_batch_async(itens_para_salvar)
                    totals["itens"] += batch_totals["itens"]
                    totals["ignoradas"] += batch_totals["ignoradas"]
                    
        except asyncio.CancelledError:
            logger.warning("[PNCP Itens] Cancelamento recebido; aguardando finalização das tasks...")
            raise
        finally:
            pendentes = [t for t in tasks if not t.done()]
            if pendentes:
                logger.warning(f"[PNCP Itens] Cancelando tasks pendentes: {len(pendentes)}")
                for t in pendentes:
                    t.cancel()
                await asyncio.gather(*pendentes, return_exceptions=True)
    
    logger.info(
        f"[PNCP Itens] Concluído - itens={totals['itens']}, "
        f"ignoradas={totals['ignoradas']}, compras_processadas={totals['compras_processadas']}"
    )
    return totals


@shared_task(bind=True, name="django_licitacao360.apps.pncp.tasks.task_atualizacao_itens_pncp")
def task_atualizacao_itens_pncp(self, cnpj: Optional[str] = None, modalidades: Optional[List[int]] = None):
    """
    Task do Celery para atualizar itens das compras dos últimos 10 dias.
    
    Esta task deve ser executada após task_atualizacao_seq_pncp para buscar
    os itens das compras já cadastradas.
    
    Args:
        cnpj: CNPJ do órgão (padrão: DEFAULT_CNPJ)
        modalidades: Lista de códigos de modalidades (padrão: todas as 13 modalidades)
    """
    import os
    
    cnpj = cnpj or os.getenv("PNCP_CNPJ", DEFAULT_CNPJ)
    
    # Processa modalidades da variável de ambiente ou usa padrão
    if modalidades is None:
        modalidades_str = os.getenv("PNCP_MODALIDADES", None)
        if modalidades_str:
            modalidades = [int(m.strip()) for m in modalidades_str.split(",") if m.strip()]
        else:
            modalidades = DEFAULT_MODALIDADES
    
    # Converte códigos de modalidades para nomes
    modalidades_nomes = [MODALIDADES.get(m, f"Modalidade {m}") for m in modalidades]
    
    # Calcula datas: últimos 10 dias (incluindo o dia atual)
    hoje = timezone.now().date()
    data_inicial_dt = hoje - timedelta(days=9)  # 9 dias atrás + hoje = 10 dias
    
    # Converte para datetime no início e fim do dia
    data_inicial = timezone.make_aware(datetime.combine(data_inicial_dt, datetime.min.time()))
    data_final = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))
    
    logger.info(
        f"[PNCP Itens Task] Iniciando atualização de itens - "
        f"data_inicial={data_inicial.date()}, data_final={data_final.date()} "
        f"(últimos 10 dias), cnpj={cnpj}, modalidades={modalidades_nomes}"
    )
    
    try:
        # Executa a função assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            totals = loop.run_until_complete(
                _processar_itens_async(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    modalidades=modalidades_nomes,
                    cnpj=cnpj,
                )
            )
            logger.info(f"[PNCP Itens Task] Sucesso - {totals}")
            return totals
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"[PNCP Itens Task] Erro durante execução: {e}", exc_info=True)
        raise


# ============================================================================
# Task para buscar resultados dos itens (Etapa 3)
# ============================================================================

MAX_CONCURRENCY_RESULTADOS = 5
MAX_RETRIES_RESULTADOS = 3


def _get_itens_para_resultados_sync(
    data_inicial: datetime,
    data_final: datetime,
    modalidades: List[str],
    cnpj: str,
) -> List[Dict[str, Any]]:
    """
    Busca itens que precisam ter resultados buscados:
    - tem_resultado = True
    - situacao_compra_item_nome contém "Homologado"
    - Não têm resultado com valor_unitario_homologado ainda
    """
    # Busca itens que atendem aos critérios
    # Converte nomes de modalidades para IDs
    modalidades_ids = []
    for modalidade_nome in modalidades:
        modalidade_obj = Modalidade.objects.filter(nome=modalidade_nome).first()
        if modalidade_obj:
            modalidades_ids.append(modalidade_obj.id)
    
    queryset = ItemCompra.objects.filter(
        compra__data_publicacao_pncp__gte=data_inicial,
        compra__data_publicacao_pncp__lte=data_final,
        tem_resultado=True,
        situacao_compra_item_nome__icontains="Homologado",
    )
    if modalidades_ids:
        queryset = queryset.filter(compra__modalidade_id__in=modalidades_ids)
    itens = queryset.select_related("compra").prefetch_related("resultados")
    
    # Filtra apenas itens que não têm resultado com valor_unitario_homologado
    itens_para_processar = []
    for item in itens:
        # Verifica se já tem resultado com valor_unitario_homologado
        tem_resultado_completo = item.resultados.filter(
            valor_unitario_homologado__isnull=False
        ).exists()
        
        if not tem_resultado_completo:
            # Garante que numero_item seja obtido corretamente do objeto item
            numero_item = item.numero_item
            itens_para_processar.append({
                "ano_compra": item.compra.ano_compra,
                "sequencial_compra": item.compra.sequencial_compra,
                "numero_item": numero_item,  # numero_item do item de compra
                "orgao_cnpj": cnpj,
                "item": item,  # Mantém referência ao objeto ItemCompra
            })
            logger.debug(
                f"[PNCP Resultados] Item adicionado para processamento: "
                f"ano={item.compra.ano_compra}, seq={item.compra.sequencial_compra}, "
                f"numero_item={numero_item}, item_id={item.item_id}"
            )
    
    return itens_para_processar


_get_itens_para_resultados_async = sync_to_async(_get_itens_para_resultados_sync, thread_sensitive=False)


def _to_decimal_resultados(value: Optional[Any]) -> Optional[Decimal]:
    """Converte valor para Decimal"""
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _to_int_resultados(value: Optional[Any]) -> Optional[int]:
    """Converte valor para int"""
    if value in (None, ""):
        return None
    try:
        return int(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError):
        return None


async def _fetch_resultados_api(
    session: aiohttp.ClientSession,
    orgao_cnpj: str,
    ano: int,
    seq: int,
    numero_item: int,
    max_retries: int = MAX_RETRIES_RESULTADOS,
) -> List[Dict[str, Any]]:
    """
    Busca resultados de um item específico da API do PNCP.
    """
    url = f"{PNCP_API_BASE}/orgaos/{orgao_cnpj}/compras/{ano}/{seq}/itens/{numero_item}/resultados"
    
    logger.debug(f"[PNCP Resultados] GET {url}")
    
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, headers=HEADERS, timeout=60) as resp:
                if resp.status == 404:
                    logger.debug(f"[PNCP Resultados] Nenhum resultado (404) para {ano}/{seq}/{numero_item}")
                    return []
                
                if resp.status == 429:
                    retry_after = int(resp.headers.get("Retry-After", "5"))
                    backoff = retry_after * (2 ** (attempt - 1))
                    logger.warning(
                        f"[PNCP Resultados] 429 recebido para {url} (tentativa {attempt}/{max_retries}). "
                        f"Aguardando {backoff}s antes de tentar novamente."
                    )
                    await asyncio.sleep(backoff)
                    continue
                
                resp.raise_for_status()
                data = await resp.json()
                
                # Processa diferentes formatos de resposta
                if data is None:
                    return []
                if isinstance(data, list):
                    return [d for d in data if isinstance(d, dict)]
                if isinstance(data, dict):
                    inner = data.get("data")
                    if isinstance(inner, list):
                        return [d for d in inner if isinstance(d, dict)]
                
                logger.warning(
                    f"[PNCP Resultados] Estrutura inesperada para {ano}/{seq}/{numero_item}: {type(data)}"
                )
                return []
                
        except asyncio.CancelledError:
            logger.debug(f"[PNCP Resultados] Cancelado durante fetch {ano}/{seq}/{numero_item}")
            raise
        except aiohttp.ClientError as e:
            logger.warning(
                f"[PNCP Resultados] Erro de rede em {ano}/{seq}/{numero_item} "
                f"(tentativa {attempt}/{max_retries}): {e}"
            )
            if attempt == max_retries:
                raise
            await asyncio.sleep(2 ** attempt)
    
    raise RuntimeError(f"[PNCP Resultados] Falha após {max_retries} tentativas para {ano}/{seq}/{numero_item}")


async def _worker_resultados(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    item_info: Dict[str, Any],
) -> Tuple[int, int, int, List[Dict[str, Any]], Optional[str]]:
    """
    Worker assíncrono para buscar resultados de um item.
    """
    ano = item_info["ano_compra"]
    seq = item_info["sequencial_compra"]
    num = item_info["numero_item"]
    cnpj = item_info["orgao_cnpj"]
    
    try:
        logger.debug(f"[PNCP Resultados] Iniciando worker {ano}/{seq}/{num} orgao={cnpj}")
        async with sem:
            resultados = await _fetch_resultados_api(session, cnpj, ano, seq, num)
        logger.debug(f"[PNCP Resultados] Worker concluído {ano}/{seq}/{num} resultados={len(resultados)}")
        return ano, seq, num, resultados, None
    except asyncio.CancelledError:
        logger.debug(f"[PNCP Resultados] Worker cancelado {ano}/{seq}/{num}")
        raise
    except Exception as e:
        logger.error(f"[PNCP Resultados] Worker falhou {ano}/{seq}/{num}: {e}")
        return ano, seq, num, [], str(e)


def _save_fornecedor_sync(cnpj: str, razao_social: Optional[str]) -> None:
    """Salva ou atualiza um fornecedor"""
    if not cnpj:
        return
    
    Fornecedor.objects.update_or_create(
        cnpj_fornecedor=cnpj,
        defaults={"razao_social": razao_social or ""}
    )


_save_fornecedor_async = sync_to_async(_save_fornecedor_sync, thread_sensitive=False)


def _save_resultado_sync(
    item_compra: ItemCompra,
    fornecedor: Fornecedor,
    valor_total_homologado: Decimal,
    quantidade_homologada: int,
    valor_unitario_homologado: Decimal,
    status: str,
    marca: Optional[str] = None,
    modelo: Optional[str] = None,
) -> None:
    """Salva ou atualiza um resultado de item"""
    # Garante que estamos usando o numero_item correto do item_compra
    ano = item_compra.compra.ano_compra
    seq = item_compra.compra.sequencial_compra
    numero_item = item_compra.numero_item  # Usa o numero_item do objeto item_compra
    
    resultado_id = f"{ano}::{seq}::{numero_item}"
    
    # Log para debug
    logger.debug(
        f"[PNCP Resultados] Criando resultado_id: {resultado_id} "
        f"(ano={ano}, seq={seq}, numero_item={numero_item}, item_id={item_compra.item_id})"
    )
    
    ResultadoItem.objects.update_or_create(
        resultado_id=resultado_id,
        defaults={
            "item_compra": item_compra,
            "fornecedor": fornecedor,
            "valor_total_homologado": valor_total_homologado,
            "quantidade_homologada": quantidade_homologada,
            "valor_unitario_homologado": valor_unitario_homologado,
            "status": status or "",
            "marca": marca or "",
            "modelo": modelo or "",
        }
    )


def _atualizar_percentual_item_sync(
    item_compra: ItemCompra,
    valor_total_homologado: Optional[Decimal],
) -> None:
    """Atualiza o percentual de economia do item"""
    if valor_total_homologado is None:
        return
    
    if item_compra.valor_total_estimado is None or item_compra.valor_total_estimado == 0:
        item_compra.percentual_economia = None
    else:
        percentual = (
            (item_compra.valor_total_estimado - valor_total_homologado) / 
            item_compra.valor_total_estimado
        ) * Decimal("100")
        item_compra.percentual_economia = percentual.quantize(Decimal("0.01"))
    
    item_compra.save(update_fields=["percentual_economia"])


def _processar_resultado_batch_sync(
    resultados_data: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Processa um lote de resultados: salva fornecedores, resultados e atualiza percentuais.
    """
    totals = {"resultados": 0, "fornecedores": 0, "ignoradas": 0}
    
    if not resultados_data:
        return totals
    
    with transaction.atomic():
        for resultado_data in resultados_data:
            try:
                item_compra = resultado_data["item_compra"]
                resultado_api = resultado_data["resultado_api"]
                
                # Extrai dados do resultado da API
                cnpj_f = resultado_api.get("niFornecedor")
                razao_f = resultado_api.get("nomeRazaoSocialFornecedor")
                valor_total = _to_decimal_resultados(resultado_api.get("valorTotalHomologado"))
                quantidade = _to_int_resultados(resultado_api.get("quantidadeHomologada"))
                valor_unitario = _to_decimal_resultados(resultado_api.get("valorUnitarioHomologado"))
                situacao = (
                    resultado_api.get("situacaoCompraItemResultadoNome") or 
                    resultado_api.get("situacaoCompraItemResultadoId")
                )
                marca = resultado_api.get("marca")
                modelo = resultado_api.get("modelo")
                
                # Valida dados obrigatórios
                if not cnpj_f or not valor_total or not quantidade or not valor_unitario:
                    logger.debug(
                        f"[PNCP Resultados] Dados incompletos para item {item_compra.item_id}: "
                        f"cnpj={cnpj_f}, valor_total={valor_total}, quantidade={quantidade}, "
                        f"valor_unitario={valor_unitario}"
                    )
                    totals["ignoradas"] += 1
                    continue
                
                # Salva fornecedor
                fornecedor, created = Fornecedor.objects.get_or_create(
                    cnpj_fornecedor=cnpj_f,
                    defaults={"razao_social": razao_f or ""}
                )
                if created:
                    totals["fornecedores"] += 1
                elif razao_f:
                    # Atualiza razão social se fornecida
                    fornecedor.razao_social = razao_f
                    fornecedor.save(update_fields=["razao_social"])
                
                # Salva resultado
                _save_resultado_sync(
                    item_compra=item_compra,
                    fornecedor=fornecedor,
                    valor_total_homologado=valor_total,
                    quantidade_homologada=quantidade,
                    valor_unitario_homologado=valor_unitario,
                    status=str(situacao) if situacao else "",
                    marca=marca,
                    modelo=modelo,
                )
                
                # Atualiza percentual de economia do item
                _atualizar_percentual_item_sync(item_compra, valor_total)
                
                totals["resultados"] += 1
                
            except Exception as e:
                logger.error(
                    f"[PNCP Resultados] Erro ao processar resultado: {e}",
                    exc_info=True
                )
                totals["ignoradas"] += 1
    
    return totals


_processar_resultado_batch_async = sync_to_async(_processar_resultado_batch_sync, thread_sensitive=False)


async def _processar_resultados_async(
    data_inicial: datetime,
    data_final: datetime,
    modalidades: List[str],
    cnpj: str,
) -> Dict[str, int]:
    """
    Processa resultados de itens: busca itens, busca resultados da API e salva no banco.
    """
    logger.info(
        f"[PNCP Resultados] Iniciando processamento de resultados - "
        f"data_inicial={data_inicial.date()}, data_final={data_final.date()}, "
        f"modalidades={modalidades}, cnpj={cnpj}"
    )
    
    # Busca itens que precisam ter resultados buscados
    itens = await _get_itens_para_resultados_async(
        data_inicial, data_final, modalidades, cnpj
    )
    
    if not itens:
        logger.info("[PNCP Resultados] Nenhum item encontrado para buscar resultados.")
        return {"resultados": 0, "fornecedores": 0, "ignoradas": 0, "itens_processados": 0}
    
    logger.info(f"[PNCP Resultados] Itens encontrados: {len(itens)}")
    
    totals = {"resultados": 0, "fornecedores": 0, "ignoradas": 0, "itens_processados": 0}
    sem = asyncio.Semaphore(MAX_CONCURRENCY_RESULTADOS)
    
    # Cria dicionário de lookup para acesso rápido aos itens
    itens_lookup = {
        (item_info["ano_compra"], item_info["sequencial_compra"], item_info["numero_item"]): item_info["item"]
        for item_info in itens
    }
    
    async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
        tasks = [
            asyncio.create_task(_worker_resultados(session, sem, item_info)) 
            for item_info in itens
        ]
        
        try:
            for t in asyncio.as_completed(tasks):
                ano, seq, num, resultados, err = await t
                
                if err:
                    logger.warning(f"[PNCP Resultados] Falha ao buscar resultados {ano}/{seq}/{num}: {err}")
                    totals["ignoradas"] += 1
                    continue
                
                totals["itens_processados"] += 1
                
                if not resultados:
                    logger.debug(f"[PNCP Resultados] Nenhum resultado para {ano}/{seq}/{num}")
                    continue
                
                # Busca o item no dicionário de lookup usando ano, seq e num (numero_item)
                item_compra = itens_lookup.get((ano, seq, num))
                
                # Se não encontrou no lookup, busca no banco usando numero_item correto
                if not item_compra:
                    item_compra = await _get_item_compra_async(ano, seq, num)
                
                if not item_compra:
                    logger.warning(f"[PNCP Resultados] Item {ano}/{seq}/{num} não encontrado")
                    totals["ignoradas"] += 1
                    continue
                
                # Valida que o numero_item do item_compra corresponde ao usado na busca
                if item_compra.numero_item != num:
                    logger.warning(
                        f"[PNCP Resultados] Inconsistência: item_compra.numero_item={item_compra.numero_item} "
                        f"diferente do numero_item usado na busca={num} para {ano}/{seq}"
                    )
                    # Usa o numero_item correto do item_compra
                    num = item_compra.numero_item
                
                # Prepara dados para processamento em lote
                # IMPORTANTE: Usa o item_compra correto com numero_item válido
                resultados_para_salvar = []
                for resultado in resultados:
                    if not isinstance(resultado, dict):
                        logger.debug(f"[PNCP Resultados] Ignorando resultado inválido: {type(resultado)}")
                        continue
                    
                    # Garante que estamos usando o item_compra correto
                    # O item_compra já foi validado acima e tem o numero_item correto
                    resultados_para_salvar.append({
                        "item_compra": item_compra,  # item_compra com numero_item correto
                        "resultado_api": resultado,
                    })
                    
                    logger.debug(
                        f"[PNCP Resultados] Preparando resultado para item: "
                        f"ano={ano}, seq={seq}, numero_item={item_compra.numero_item}, "
                        f"item_id={item_compra.item_id}"
                    )
                
                # Processa lote de resultados
                if resultados_para_salvar:
                    batch_totals = await _processar_resultado_batch_async(resultados_para_salvar)
                    totals["resultados"] += batch_totals["resultados"]
                    totals["fornecedores"] += batch_totals["fornecedores"]
                    totals["ignoradas"] += batch_totals["ignoradas"]
                    
        except asyncio.CancelledError:
            logger.warning("[PNCP Resultados] Cancelamento recebido; aguardando finalização das tasks...")
            raise
        finally:
            pendentes = [t for t in tasks if not t.done()]
            if pendentes:
                logger.warning(f"[PNCP Resultados] Cancelando tasks pendentes: {len(pendentes)}")
                for t in pendentes:
                    t.cancel()
                await asyncio.gather(*pendentes, return_exceptions=True)
    
    logger.info(
        f"[PNCP Resultados] Concluído - resultados={totals['resultados']}, "
        f"fornecedores={totals['fornecedores']}, ignoradas={totals['ignoradas']}, "
        f"itens_processados={totals['itens_processados']}"
    )
    return totals


def _get_item_compra_sync(ano: int, seq: int, num: int) -> Optional[ItemCompra]:
    """Busca um item de compra específico"""
    try:
        return ItemCompra.objects.get(
            compra__ano_compra=ano,
            compra__sequencial_compra=seq,
            numero_item=num
        )
    except ItemCompra.DoesNotExist:
        return None
    except ItemCompra.MultipleObjectsReturned:
        logger.warning(f"[PNCP Resultados] Múltiplos itens encontrados para {ano}/{seq}/{num}")
        return ItemCompra.objects.filter(
            compra__ano_compra=ano,
            compra__sequencial_compra=seq,
            numero_item=num
        ).first()


_get_item_compra_async = sync_to_async(_get_item_compra_sync, thread_sensitive=False)


@shared_task(bind=True, name="django_licitacao360.apps.pncp.tasks.task_atualizacao_resultados_pncp")
def task_atualizacao_resultados_pncp(self, cnpj: Optional[str] = None, modalidades: Optional[List[int]] = None):
    """
    Task do Celery para atualizar resultados dos itens dos últimos 10 dias.
    
    Esta task deve ser executada após task_atualizacao_itens_pncp para buscar
    os resultados dos itens já cadastrados.
    
    Args:
        cnpj: CNPJ do órgão (padrão: DEFAULT_CNPJ)
        modalidades: Lista de códigos de modalidades (padrão: todas as 13 modalidades)
    """
    import os
    
    cnpj = cnpj or os.getenv("PNCP_CNPJ", DEFAULT_CNPJ)
    
    # Processa modalidades da variável de ambiente ou usa padrão
    if modalidades is None:
        modalidades_str = os.getenv("PNCP_MODALIDADES", None)
        if modalidades_str:
            modalidades = [int(m.strip()) for m in modalidades_str.split(",") if m.strip()]
        else:
            modalidades = DEFAULT_MODALIDADES
    
    # Converte códigos de modalidades para nomes
    modalidades_nomes = [MODALIDADES.get(m, f"Modalidade {m}") for m in modalidades]
    
    # Calcula datas: últimos 10 dias (incluindo o dia atual)
    hoje = timezone.now().date()
    data_inicial_dt = hoje - timedelta(days=9)  # 9 dias atrás + hoje = 10 dias
    
    # Converte para datetime no início e fim do dia
    data_inicial = timezone.make_aware(datetime.combine(data_inicial_dt, datetime.min.time()))
    data_final = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))
    
    logger.info(
        f"[PNCP Resultados Task] Iniciando atualização de resultados - "
        f"data_inicial={data_inicial.date()}, data_final={data_final.date()} "
        f"(últimos 10 dias), cnpj={cnpj}, modalidades={modalidades_nomes}"
    )
    
    try:
        # Executa a função assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            totals = loop.run_until_complete(
                _processar_resultados_async(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    modalidades=modalidades_nomes,
                    cnpj=cnpj,
                )
            )
            logger.info(f"[PNCP Resultados Task] Sucesso - {totals}")
            return totals
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"[PNCP Resultados Task] Erro durante execução: {e}", exc_info=True)
        raise


# ============================================================================
# Task para atualizar compras via endpoint de atualização (Etapa 1b)
# ============================================================================

PNCP_ATUALIZACAO_BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/atualizacao"


async def _get_atualizacoes_page(
    session: aiohttp.ClientSession,
    params: Dict[str, str],
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Faz GET assíncrono no endpoint de atualização com retry/backoff simples.
    Retorna (payload_json, erro_str)
    """
    url = PNCP_ATUALIZACAO_BASE
    timeout = aiohttp.ClientTimeout(total=60)
    
    # Log da URL completa para debug
    url_with_params = f"{url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    logger.debug(f"[PNCP Atualização] GET {url_with_params}")
    
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, params=params, headers=HEADERS, timeout=timeout) as resp:
                if resp.status != 200:
                    body = (await resp.text())[:240]
                    err = f"API {resp.status}: {body}"
                    if attempt < max_retries and resp.status in (500, 502, 503, 504):
                        await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
                        continue
                    return None, err
                ct = (resp.headers.get("Content-Type") or "").lower()
                if "application/json" not in ct:
                    preview = (await resp.text())[:240].replace("\n", " ")
                    return None, f"Content-Type inesperado ({ct}). Body[:240]={preview!r}"
                data = await resp.json()
                return data, None
        except aiohttp.ClientError as e:
            if attempt < max_retries:
                await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
                continue
            return None, f"ClientError: {repr(e)}"
        except asyncio.TimeoutError as e:
            if attempt < max_retries:
                await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
                continue
            return None, f"TimeoutError: {repr(e)}"
        except json.JSONDecodeError as e:
            return None, f"JSONDecodeError: {repr(e)}"
    return None, "Erro desconhecido"


def _process_atualizacao(p: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Processa uma atualização e retorna os dados da compra para salvar/atualizar.
    """
    ano = int(p.get("anoCompra") or 0)
    seq = int(p.get("sequencialCompra") or 0)
    codigo_unidade = (p.get("unidadeOrgao") or {}).get("codigoUnidade")
    
    if not (ano and seq and codigo_unidade):
        return None
    
    numero_compra = p.get("numeroCompra") or ""
    modalidade_id = p.get("modalidadeId")
    amparo_legal_data = p.get("amparoLegal")
    amparo_legal_id = amparo_legal_data.get("codigo") if isinstance(amparo_legal_data, dict) else None
    modo_disputa_id = p.get("modoDisputaId")
    objeto_compra = p.get("objetoCompra") or ""
    processo_adm = p.get("processo")
    if processo_adm:
        processo_adm = str(processo_adm).strip()
    else:
        processo_adm = ""
    
    data_publicacao = _parse_date(
        p.get("dataPublicacaoPncp") or p.get("dataInclusao")
    )
    data_atualizacao = _parse_date(
        p.get("dataAtualizacao") or p.get("dataAtualizacaoGlobal")
    )
    valor_total_estimado = _to_decimal(p.get("valorTotalEstimado"))
    valor_total_homologado = _to_decimal(p.get("valorTotalHomologado"))
    
    # Calcula percentual de desconto
    percentual_desconto = None
    if (
        valor_total_estimado is not None
        and valor_total_homologado is not None
        and valor_total_estimado > 0
    ):
        percentual_desconto = (
            (valor_total_estimado - valor_total_homologado) / valor_total_estimado
        ) * Decimal("100")
    
    # Gera compra_id no formato "ano::sequencial"
    compra_id = f"{ano}::{seq}"
    
    return {
        "compra_id": compra_id,
        "ano_compra": ano,
        "sequencial_compra": seq,
        "numero_compra": numero_compra,
        "codigo_unidade": str(codigo_unidade),
        "objeto_compra": objeto_compra,
        "modalidade_id": modalidade_id,
        "amparo_legal_id": amparo_legal_id,
        "modo_disputa_id": modo_disputa_id,
        "numero_processo": processo_adm,
        "data_publicacao_pncp": data_publicacao,
        "data_atualizacao": data_atualizacao,
        "valor_total_estimado": valor_total_estimado,
        "valor_total_homologado": valor_total_homologado,
        "percentual_desconto": percentual_desconto,
    }


async def _fetch_and_process_atualizacoes(
    data_inicial: str,
    data_final: str,
    modalidade: int,
    cnpj: str,
    unidade: Optional[str] = None,
) -> Dict[str, int]:
    """
    Busca atualizações da API do PNCP e processa todas as páginas.
    Retorna contadores: {'compras': X, 'ignoradas': Y, 'paginas': N}
    """
    logger.info(
        f"[PNCP Atualização] Iniciando coleta de atualizações - "
        f"dataInicial={data_inicial}, dataFinal={data_final}, "
        f"modalidade={modalidade}, cnpj={cnpj}, unidade={unidade or '-'}"
    )
    
    # Garante que modalidade é um inteiro válido
    modalidade_int = int(modalidade) if modalidade else None
    if not modalidade_int:
        logger.error(f"[PNCP Atualização] Modalidade inválida: {modalidade}")
        return {"compras": 0, "ignoradas": 0, "paginas": 0}
    
    base_params = {
        "dataInicial": data_inicial.replace("-", ""),
        "dataFinal": data_final.replace("-", ""),
        "codigoModalidadeContratacao": str(modalidade_int),
        "cnpj": cnpj,
        "pagina": "1",
    }
    if unidade and unidade not in {"0", "1", "-", ""}:
        base_params["codigoUnidadeAdministrativa"] = unidade
    
    # Log dos parâmetros para debug
    logger.info(f"[PNCP Atualização] Parâmetros da requisição: {base_params}")
    
    totals = {"compras": 0, "ignoradas": 0, "paginas": 0}
    compras_data = {}  # Usado para deduplicação: {(ano, seq): dados}
    
    async with aiohttp.ClientSession(trust_env=True) as session:
        # Busca primeira página
        params = dict(base_params)
        params["pagina"] = "1"
        payload, err = await _get_atualizacoes_page(session, params)
        
        if err:
            logger.error(f"[PNCP Atualização] Falha ao buscar página 1: {err}")
            return totals
        
        # Extrai lista de atualizações
        atualizacoes = payload.get("data")
        if not isinstance(atualizacoes, list):
            atualizacoes = []
        
        total_paginas = int(payload.get("totalPaginas") or 1)
        numero_pagina = int(payload.get("numeroPagina") or 1)
        
        logger.info(f"[PNCP Atualização] Total de páginas: {total_paginas}")
        
        # Processa primeira página
        for p in atualizacoes:
            compra_data = _process_atualizacao(p)
            if compra_data:
                key = (compra_data["ano_compra"], compra_data["sequencial_compra"])
                compras_data[key] = compra_data  # Mantém a última ocorrência
            else:
                totals["ignoradas"] += 1
        totals["paginas"] += 1
        
        # Busca páginas restantes em paralelo
        if total_paginas > 1:
            sem = asyncio.Semaphore(10)
            
            async def fetch_page(pg: int):
                params = dict(base_params)
                params["pagina"] = str(pg)
                async with sem:
                    payload, err = await _get_atualizacoes_page(session, params)
                return pg, payload, err
            
            tasks = [
                asyncio.create_task(fetch_page(pg))
                for pg in range(2, total_paginas + 1)
            ]
            
            for coro in asyncio.as_completed(tasks):
                pg, payload, err = await coro
                if err:
                    logger.warning(f"[PNCP Atualização] Falha ao buscar página {pg}: {err}")
                    totals["ignoradas"] += 1
                    continue
                
                atualizacoes = payload.get("data")
                if not isinstance(atualizacoes, list):
                    atualizacoes = []
                
                for p in atualizacoes:
                    compra_data = _process_atualizacao(p)
                    if compra_data:
                        key = (compra_data["ano_compra"], compra_data["sequencial_compra"])
                        compras_data[key] = compra_data
                    else:
                        totals["ignoradas"] += 1
                totals["paginas"] += 1
        
        # Salva no banco usando Django ORM (função síncrona)
        if compras_data:
            totals_saved = await _save_compras_async(list(compras_data.values()))
            totals["compras"] += totals_saved["compras"]
            totals["ignoradas"] += totals_saved["ignoradas"]
    
    logger.info(
        f"[PNCP Atualização] Concluído - compras={totals['compras']}, "
        f"ignoradas={totals['ignoradas']}, páginas={totals['paginas']}"
    )
    return totals


@shared_task(bind=True, name="django_licitacao360.apps.pncp.tasks.task_atualizacao_compras_pncp")
def task_atualizacao_compras_pncp(self, cnpj: Optional[str] = None, modalidades: Optional[List[int]] = None):
    """
    Task do Celery para atualizar compras via endpoint de atualização dos últimos 10 dias.
    
    Esta task busca atualizações de compras que já existem ou cria novas se não existirem.
    Diferente da task de sequenciais, esta busca especificamente por atualizações.
    
    Args:
        cnpj: CNPJ do órgão (padrão: DEFAULT_CNPJ)
        modalidades: Lista de códigos de modalidades (padrão: todas as 13 modalidades)
    """
    import os
    
    cnpj = cnpj or os.getenv("PNCP_CNPJ", DEFAULT_CNPJ)
    
    # Processa modalidades da variável de ambiente ou usa padrão
    if modalidades is None:
        modalidades_str = os.getenv("PNCP_MODALIDADES", None)
        if modalidades_str:
            modalidades = [int(m.strip()) for m in modalidades_str.split(",") if m.strip()]
        else:
            modalidades = DEFAULT_MODALIDADES
    
    # Calcula datas: últimos 10 dias (incluindo o dia atual)
    hoje = timezone.now().date()
    data_inicial_dt = hoje - timedelta(days=9)  # 9 dias atrás + hoje = 10 dias
    
    data_inicial = data_inicial_dt.strftime("%Y-%m-%d")
    data_final = hoje.strftime("%Y-%m-%d")
    
    logger.info(
        f"[PNCP Atualização Task] Iniciando atualização - "
        f"data_inicial={data_inicial}, data_final={data_final} "
        f"(últimos 10 dias), cnpj={cnpj}, modalidades={modalidades}"
    )
    
    try:
        # Executa a função assíncrona para cada modalidade
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            total_geral = {"compras": 0, "ignoradas": 0, "paginas": 0}
            
            # Processa cada modalidade sequencialmente
            for modalidade in modalidades:
                modalidade_nome = MODALIDADES.get(modalidade, f"Modalidade {modalidade}")
                logger.info(
                    f"[PNCP Atualização Task] Processando modalidade {modalidade} - {modalidade_nome}"
                )
                totals = loop.run_until_complete(
                    _fetch_and_process_atualizacoes(
                        data_inicial=data_inicial,
                        data_final=data_final,
                        modalidade=modalidade,
                        cnpj=cnpj,
                    )
                )
                # Acumula totais
                total_geral["compras"] += totals.get("compras", 0)
                total_geral["ignoradas"] += totals.get("ignoradas", 0)
                total_geral["paginas"] += totals.get("paginas", 0)
                logger.info(
                    f"[PNCP Atualização Task] Modalidade {modalidade} ({modalidade_nome}) concluída - "
                    f"compras={totals.get('compras', 0)}, "
                    f"ignoradas={totals.get('ignoradas', 0)}, "
                    f"páginas={totals.get('paginas', 0)}"
                )
            
            logger.info(f"[PNCP Atualização Task] Sucesso geral - {total_geral}")
            return total_geral
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"[PNCP Atualização Task] Erro durante execução: {e}", exc_info=True)
        raise
