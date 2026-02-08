# /app/pncp_consulta_pregao.py
# Etapa 1 – Publicações (PNCP)
# Coleta publicações paginadas do endpoint /contratacoes/publicacao e dá upsert em: orgaos, unidades_compradoras, compras.

from __future__ import annotations

import asyncio
import json
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import aiohttp
from django.db import transaction
from django.db.models import Q

from ...models import AmparoLegal, Compra, Modalidade, ModoDisputa


def _dedup(rows: Iterable[Tuple], key_fn: Callable[[Tuple], Any]) -> List[Tuple]:
    """
    Mantém a ÚLTIMA ocorrência de cada chave (sobrescreve anteriores).
    Retorna lista sem duplicados, preservando o último valor visto.
    """
    bucket: Dict[Any, Tuple] = {}
    for r in rows:
        bucket[key_fn(r)] = r
    return list(bucket.values())


def _to_decimal(value: Any) -> Optional[Decimal]:
    if value in (None, "", "null"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
PNCP_BASE = "https://pncp.gov.br/api/consulta/v1"
HEADERS = {
    "User-Agent": "curl/8.8",           # cabeçalho “neutro” que os gateways costumam aceitar bem
    "Accept": "application/json",
}
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
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, params=params, headers=HEADERS, timeout=timeout) as resp:
                # print(f"[DEBUG] GET {resp.status} {resp.url}")
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
def _extract_list(payload: Dict[str, Any]) -> Tuple[Iterable[Dict[str, Any]], int, int]:
    """
    Extrai a lista de publicações e info de paginação, lidando com variações de chave:
    data (atual), publicacoes (variante antiga), content (fallback comum).
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
# ----------------------
# UPSERTS (idempotentes)
# ----------------------
def _parse_date(value: Optional[str]) -> Optional[datetime]:
    """
    Converte string de data para datetime.
    O model Compra usa DateTimeField, então retornamos datetime ao invés de date.
    """
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
        # Se não tiver timezone, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=None)  # Mantém naive, será tratado pelo Django
        return dt
    except ValueError:
        # tenta formatos sem timezone
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(text, fmt)
                return dt
            except ValueError:
                continue
    return None


def _rows_from_publicacoes(publicacoes: Iterable[Dict[str, Any]]):
    """
    Extrai dados das publicações e prepara para upsert usando Django ORM.
    Retorna dicionários com os dados processados.
    """
    orgaos_data = []
    unidades_data = []
    compras_data = []
    
    for p in publicacoes:
        cnpj = str(p.get("orgaoEntidade", {}).get("cnpj") or "").zfill(14) or None
        razao = p.get("orgaoEntidade", {}).get("razaoSocial")
        und = p.get("unidadeOrgao") or {}
        codigo_unidade = und.get("codigoUnidade")
        nome_unidade = und.get("nomeUnidade")
        municipio = und.get("municipioNome")
        uf = und.get("ufSigla")
        endereco = None  # não vem nessa etapa
        ano = int(p.get("anoCompra") or 0)
        seq = int(p.get("sequencialCompra") or 0)
        
        # Garante que campos CharField recebem string vazia ao invés de None
        numero_compra = p.get("numeroCompra") or ""
        modalidade_id = p.get("modalidadeId")
        modalidade_nome = p.get("modalidadeNome") or ""  # Mantido para referência
        amparo_legal_data = p.get("amparoLegal")
        amparo_legal_id = amparo_legal_data.get("codigo") if isinstance(amparo_legal_data, dict) else None
        modo_disputa_id = p.get("modoDisputaId")
        objeto_compra = (p.get("objeto") or p.get("objetoCompra")) or ""
        processo_adm = (
            p.get("processo")
            or p.get("numeroProcesso")
            or p.get("numeroProcessoCompra")
            or p.get("processoCompra")
        )
        if processo_adm:
            processo_adm = str(processo_adm).strip()
        else:
            processo_adm = ""
        data_publicacao = _parse_date(
            p.get("dataPublicacaoPncp") or p.get("dataPublicacao")
        )
        data_atualizacao = _parse_date(
            p.get("dataAtualizacao") or p.get("dataAtualizacaoPncp")
        )
        valor_total_estimado = _to_decimal(p.get("valorTotalEstimado"))
        valor_total_homologado = _to_decimal(p.get("valorTotalHomologado"))
        percentual_desconto = None
        if (
            valor_total_estimado is not None
            and valor_total_homologado is not None
            and valor_total_estimado > 0
        ):
            percentual_desconto = (
                (valor_total_estimado - valor_total_homologado) / valor_total_estimado
            ) * Decimal("100")
        
        if cnpj:
            orgaos_data.append({"cnpj": cnpj, "razao_social": razao})
        
        if codigo_unidade:
            unidades_data.append({
                "codigo_unidade": codigo_unidade,
                "orgao_cnpj": cnpj,
                "nome_unidade": nome_unidade,
                "municipio": municipio,
                "uf": uf,
                "endereco": endereco,
            })
        
        if ano and seq and codigo_unidade:
            # Garante que codigo_unidade é string (CharField)
            codigo_unidade = str(codigo_unidade) if codigo_unidade else ""
            compra_id = f"{ano}::{seq}"
            compras_data.append({
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
            })
    
    return orgaos_data, unidades_data, compras_data

#-----------------------
# Funções dos Upserts usando Django ORM
#-----------------------

def _get_modalidade(modalidade_id: Optional[int]) -> Optional[Modalidade]:
    """Busca modalidade por ID"""
    if not modalidade_id:
        return None
    try:
        return Modalidade.objects.get(id=modalidade_id)
    except Modalidade.DoesNotExist:
        return None


def _get_amparo_legal(amparo_id: Optional[int]) -> Optional[AmparoLegal]:
    """Busca amparo legal por ID"""
    if not amparo_id:
        return None
    try:
        return AmparoLegal.objects.get(id=amparo_id)
    except AmparoLegal.DoesNotExist:
        return None


def _get_modo_disputa(modo_disputa_id: Optional[int]) -> Optional[ModoDisputa]:
    """Busca modo de disputa por ID"""
    if not modo_disputa_id:
        return None
    try:
        return ModoDisputa.objects.get(id=modo_disputa_id)
    except ModoDisputa.DoesNotExist:
        return None


def _upsert_orgaos(orgaos_data: List[Dict[str, Any]]) -> int:
    """
    Upsert de órgãos usando Django ORM.
    Nota: Esta função assume que a tabela orgaos existe.
    Se não existir, pode ser necessário criar um model ou usar SQL direto.
    """
    if not orgaos_data:
        return 0
    
    # Se não houver model Orgao, pode pular ou usar SQL direto
    # Por enquanto, retornamos 0 pois não há model definido
    return 0


def _upsert_unidades(unidades_data: List[Dict[str, Any]]) -> int:
    """
    Upsert de unidades usando Django ORM.
    Nota: Esta função assume que a tabela unidades_compradoras existe.
    Se não existir, pode ser necessário criar um model ou usar SQL direto.
    """
    if not unidades_data:
        return 0
    
    # Se não houver model UnidadeCompradora, pode pular ou usar SQL direto
    # Por enquanto, retornamos 0 pois não há model definido
    return 0


def _upsert_compras(compras_data: List[Dict[str, Any]]) -> int:
    """
    Upsert de compras usando Django ORM com relacionamentos.
    """
    if not compras_data:
        return 0
    
    count = 0
    with transaction.atomic():
        for compra_dict in compras_data:
            try:
                # Extrai IDs dos relacionamentos (cria cópia para não modificar o original)
                compra_data = dict(compra_dict)
                modalidade_id = compra_data.pop("modalidade_id", None)
                amparo_legal_id = compra_data.pop("amparo_legal_id", None)
                modo_disputa_id = compra_data.pop("modo_disputa_id", None)
                compra_id = compra_data.pop("compra_id")
                
                # Busca os objetos relacionados
                modalidade = _get_modalidade(modalidade_id) if modalidade_id else None
                amparo_legal = _get_amparo_legal(amparo_legal_id) if amparo_legal_id else None
                modo_disputa = _get_modo_disputa(modo_disputa_id) if modo_disputa_id else None
                
                # Adiciona os objetos relacionados aos defaults
                compra_data["modalidade"] = modalidade
                compra_data["amparo_legal"] = amparo_legal
                compra_data["modo_disputa"] = modo_disputa
                
                Compra.objects.update_or_create(
                    compra_id=compra_id,
                    defaults=compra_data
                )
                count += 1
            except Exception as e:
                print(f"[WARN] Erro ao salvar compra {compra_dict.get('compra_id', 'N/A')}: {e}")
                continue
    
    return count

# ----------------------
# Função principal Etapa 1
# ----------------------
async def etapa1_publicacoes(
    data_inicial: str,
    data_final: str,
    modalidade: int,
    cnpj: str,
    unidade: Optional[str] = None,
    pagina_inicial: int = 1,
    modo: str = "completo",     # "completo" percorre até totalPaginas; "rapido" pega só 1 página
    paginas_max: Optional[int] = None,
) -> Dict[str, int]:
    """
    Coleta publicações paginadas e upserta nas tabelas base.
    Retorna contadores: {'orgaos': X, 'unidades': Y, 'compras': Z, 'ignoradas': W, 'paginas': N}
    """
    print("[Etapa 1] Iniciando coleta de publicacoes...")
    unidade_param = unidade if (unidade and unidade not in {"0", "1", "-", ""}) else None
    uni_info = unidade_param or "-"
    print(f"Filtros -> dataInicial={data_inicial}, dataFinal={data_final}, modalidade={modalidade}, cnpj={cnpj}, unidade={uni_info}")
    base_params = {
        "dataInicial": data_inicial.replace("-", ""),
        "dataFinal": data_final.replace("-", ""),
        "codigoModalidadeContratacao": str(modalidade),
        "cnpj": cnpj,
        "pagina": str(pagina_inicial),
    }
    if unidade_param:
        base_params["codigoUnidadeAdministrativa"] = unidade_param
    totals = {"orgaos": 0, "unidades": 0, "compras": 0, "ignoradas": 0, "paginas": 0}
    async with aiohttp.ClientSession(trust_env=True) as session:
        def process_payload(payload: Dict[str, Any]) -> Tuple[int, int]:
            pubs, total_paginas, numero_pagina = _extract_list(payload)
            print(f"[INFO] Pagina {numero_pagina}/{total_paginas} - publicacoes: {len(pubs)}")
            org_data, und_data, cmp_data = _rows_from_publicacoes(pubs)
            
            # Deduplica por chave primária
            org_dict = {item["cnpj"]: item for item in org_data}
            und_dict = {item["codigo_unidade"]: item for item in und_data}
            cmp_dict = {(item["ano_compra"], item["sequencial_compra"]): item for item in cmp_data}
            
            try:
                n1 = _upsert_orgaos(list(org_dict.values()))
                n2 = _upsert_unidades(list(und_dict.values()))
                n3 = _upsert_compras(list(cmp_dict.values()))
                totals["orgaos"] += n1
                totals["unidades"] += n2
                totals["compras"] += n3
            except Exception as e:
                print(f"[WARN] Falha ao upsert na pagina {numero_pagina}: {e!r}")
                totals["ignoradas"] += len(pubs)
            totals["paginas"] += 1
            return total_paginas, numero_pagina
            first_page = int(pagina_inicial)
            params = dict(base_params)
            params["pagina"] = str(first_page)
            payload, err = await _get_publications_page(session, params)
            if err:
                print(f"[WARN] Falha ao buscar pagina {first_page}: {err}")
                print(f"[Etapa 1] upsert orgaos={totals['orgaos']}, unidades={totals['unidades']}, compras={totals['compras']}, ignoradas={totals['ignoradas']}")
                print(f"Etapa 1 concluida. Paginas processadas={totals['paginas']}")
                print(f"[Etapa 1] Totais: {totals}")
                return totals
            total_paginas_known, numero_pagina = process_payload(payload)
            if modo != "rapido":
                last_page = total_paginas_known
                if paginas_max is not None:
                    last_page = min(last_page, first_page + paginas_max - 1)

                sem = asyncio.Semaphore(10)

                async def fetch_page(pg: int):
                    params = dict(base_params)
                    params["pagina"] = str(pg)
                    async with sem:
                        payload, err = await _get_publications_page(session, params)
                    return pg, payload, err

                tasks = [asyncio.create_task(fetch_page(pg))
                         for pg in range(numero_pagina + 1, last_page + 1)]

                for coro in asyncio.as_completed(tasks):
                    pg, payload, err = await coro
                    if err:
                        print(f"[WARN] Falha ao buscar pagina {pg}: {err}")
                        continue
                    process_payload(payload)
                    print(f"[INFO] Pagina processada: {pg}")
    print(f"[Etapa 1] upsert orgaos={totals['orgaos']}, unidades={totals['unidades']}, compras={totals['compras']}, ignoradas={totals['ignoradas']}")
    print(f"Etapa 1 concluida. Paginas processadas={totals['paginas']}")
    print(f"[Etapa 1] Totais: {totals}")
    return totals
# Execução direta (opcional, útil para smoke test manual do container)
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 6:
        print("Uso: python pncp_consulta_pregao.py <data_inicial> <data_final> <modalidade> <cnpj> <unidade|1> [pagina_inicial]")
        sys.exit(1)
    di, df, mod, cnpj, uni = sys.argv[1:6]
    pag = int(sys.argv[6]) if len(sys.argv) >= 7 else 1
    asyncio.run(etapa1_publicacoes(di, df, int(mod), cnpj, unidade=uni, pagina_inicial=pag, modo="completo"))
