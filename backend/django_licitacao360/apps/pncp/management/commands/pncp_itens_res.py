# /app/pncp_itens_resultados.py
# Etapa 3 — buscar resultados dos itens e fazer upsert em `fornecedores` e `resultados_item`

import asyncio
import logging
import random
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from aiolimiter import AsyncLimiter

from decimal import Decimal

from db import get_connection

UA = {"User-Agent": "GerATA Worker/1.0 (+https://example.local)"}
BASE_URL = "https://pncp.gov.br/api/pncp/v1"
limiter = AsyncLimiter(5, 1)  # até 5 requisições por segundo

logger = logging.getLogger(__name__)

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


def get_itens_para_resultados(
    data_inicial: str,
    data_final: str,
    modalidades: List[str],
    orgao_cnpj: str,
) -> List[Dict[str, Any]]:
    """
    Seleciona os itens e junta com órgão para montar URL dos resultados:
      {BASE_URL}/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numero_item}/resultados
    Busca apenas itens sem valor_unitario_homologado no período/modalidade/órgão informados.
    """
    from ...models import Modalidade
    
    if not modalidades:
        return []
    
    # Converte nomes de modalidades para IDs
    modalidades_ids = []
    for modalidade_nome in modalidades:
        modalidade_obj = Modalidade.objects.filter(nome=modalidade_nome).first()
        if modalidade_obj:
            modalidades_ids.append(modalidade_obj.id)
    
    if not modalidades_ids:
        logger.debug(f"Nenhuma modalidade encontrada para: {modalidades}")
        return []
    
    placeholders = ", ".join(["%s"] * len(modalidades_ids))
    base_sql = f"""
    SELECT ic.ano_compra,
           ic.sequencial_compra,
           ic.numero_item,
           o.cnpj AS orgao_cnpj
      FROM itens_compra ic
      JOIN compras c
        ON c.ano_compra = ic.ano_compra
       AND c.sequencial_compra = ic.sequencial_compra
      JOIN unidades_compradoras uc
        ON uc.codigo_unidade = c.codigo_unidade
      JOIN orgaos o
        ON o.cnpj = uc.orgao_cnpj
      LEFT JOIN resultados_item ri
        ON ri.ano_compra = ic.ano_compra
       AND ri.sequencial_compra = ic.sequencial_compra
             AND ri.numero_item = ic.numero_item
         WHERE c.data_publicacao_pncp BETWEEN %s AND %s
             AND c.modalidade_id IN ({placeholders})
             AND o.cnpj = %s
             AND ic.tem_resultado = 1
             AND ic.situacao_compra_item_nome LIKE '%Homologado%'
             AND ri.valor_unitario_homologado IS NULL
    """
    # IMPORTANTE: Esta query busca itens que já foram salvos na tabela itens_compra.
    # O numero_item usado aqui vem do que foi salvo anteriormente pela API.
    # Se a API retornou numeroItem=1 quando havia apenas um item homologado,
    # mas o item real era 30, então o numero_item na tabela será 1 (incorreto).
    # O problema está na forma como os itens são salvos inicialmente.
    sql = base_sql + """
    ORDER BY ic.ano_compra DESC, ic.sequencial_compra DESC, ic.numero_item ASC;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (data_inicial, data_final, *modalidades_ids, orgao_cnpj))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    itens: List[Dict[str, Any]] = []
    # Agrupa itens por compra para verificar inconsistências
    compras_itens: Dict[Tuple[int, int], List[Tuple[int, str]]] = {}
    
    for ano, seq, num, cnpj in rows:
        numero_item = int(num) if num is not None else None
        if numero_item is None:
            logger.warning(f"numero_item é None para compra {ano}/{seq}, pulando...")
            continue
        
        key = (int(ano), int(seq))
        if key not in compras_itens:
            compras_itens[key] = []
        compras_itens[key].append((numero_item, str(cnpj).zfill(14)))
    
    # Verifica inconsistências: se há apenas um item e numero_item=1, pode ser um problema
    for (ano, seq), items_list in compras_itens.items():
        if len(items_list) == 1 and items_list[0][0] == 1:
            logger.warning(
                f"[AVISO] Compra {ano}/{seq} tem apenas 1 item homologado com numero_item=1. "
                f"Isso pode indicar que o numero_item foi salvo incorretamente como sequencial "
                f"ao invés do número real do item. Verifique no banco de dados se há outros itens "
                f"nesta compra que não estão homologados."
            )
    
    # Adiciona todos os itens à lista
    for ano, seq, num, cnpj in rows:
        numero_item = int(num) if num is not None else None
        if numero_item is None:
            continue
        
        logger.debug(
            f"[DEBUG] Item encontrado na query SQL: ano={ano}, seq={seq}, "
            f"numero_item (raw)={num}, numero_item (int)={numero_item}, cnpj={cnpj}"
        )
        
        itens.append(
            {
                "ano_compra": int(ano),
                "sequencial_compra": int(seq),
                "numero_item": numero_item,  # numero_item do item de compra (vem da tabela itens_compra)
                "orgao_cnpj": str(cnpj).zfill(14),
            }
        )
    return itens


def upsert_fornecedor(cur, cnpj: Optional[str], razao: Optional[str]) -> None:
    if not cnpj:
        return
    cur.execute(
        """
        INSERT INTO fornecedores (cnpj_fornecedor, razao_social)
        VALUES (%s, COALESCE(%s,''))
        ON CONFLICT (cnpj_fornecedor) DO UPDATE
          SET razao_social = EXCLUDED.razao_social;
        """,
        (cnpj, razao),
    )


def _to_decimal(value: Optional[Any]) -> Optional[Decimal]:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _to_int(value: Optional[Any]) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(Decimal(str(value)))
    except Exception:
        return None


def atualizar_percentual_item(
    cur,
    ano: int,
    seq: int,
    num: int,
    valor_total_homologado: Optional[Decimal],
) -> None:
    cur.execute(
        """
        UPDATE itens_compra
           SET percentual_economia = CASE
                 WHEN valor_total_estimado IS NULL
                      OR %s IS NULL
                      OR valor_total_estimado = 0
                   THEN NULL
                 ELSE ROUND(
                     ((valor_total_estimado - %s) / NULLIF(valor_total_estimado, 0)) * 100,
                     2
                 )
             END
         WHERE ano_compra = %s
           AND sequencial_compra = %s
           AND numero_item = %s;
        """,
        (
            valor_total_homologado,
            valor_total_homologado,
            ano,
            seq,
            num,
        ),
    )


def upsert_resultado(
    cur,
    ano: int,
    seq: int,
    num: int,  # numero_item do item de compra
    cnpj_fornecedor: Optional[str],
    valor_total: Optional[Any],
    quantidade_homologada: Optional[Any],
    valor_unitario_homologado: Optional[Any],
    status: Optional[str],
) -> None:
    # resultado_id deve ser: ano::sequencial::numero_item
    # IMPORTANTE: num deve ser o numero_item REAL do item de compra (ex: 32), não um sequencial (1, 2, 3...)
    numero_item = int(num)  # Garante que seja inteiro
    resultado_id = f"{ano}::{seq}::{numero_item}"
    logger.debug(
        f"[DEBUG] Criando resultado_id: {resultado_id} "
        f"(ano={ano}, seq={seq}, numero_item={numero_item}, num_original={num})"
    )
    cur.execute(
        """
        INSERT INTO resultados_item (
            resultado_id,
            ano_compra,
            sequencial_compra,
            numero_item,
            cnpj_fornecedor,
            valor_total_homologado,
            quantidade_homologada,
            valor_unitario_homologado,
            status,
            marca,
            modelo
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, ''), '', '')
        ON CONFLICT (ano_compra, sequencial_compra, numero_item) DO UPDATE
          SET cnpj_fornecedor = EXCLUDED.cnpj_fornecedor,
              valor_total_homologado = EXCLUDED.valor_total_homologado,
              quantidade_homologada = EXCLUDED.quantidade_homologada,
              valor_unitario_homologado = EXCLUDED.valor_unitario_homologado,
              status = EXCLUDED.status;
        """,
        (
            resultado_id,
            ano,
            seq,
            numero_item,  # Usa numero_item ao invés de num
            cnpj_fornecedor,
            _to_decimal(valor_total),
            _to_int(quantidade_homologada),
            _to_decimal(valor_unitario_homologado),
            status.strip() if isinstance(status, str) else None,
        ),
    )


async def fetch_resultados(
    session: aiohttp.ClientSession,
    orgao_cnpj: str,
    ano: int,
    seq: int,
    numero_item: int,
    max_retries: int = 3,
) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/orgaos/{orgao_cnpj}/compras/{ano}/{seq}/itens/{numero_item}/resultados"

    for attempt in range(1, max_retries + 1):
        async with limiter:
            async with session.get(url, headers=UA, timeout=60) as resp:
                if resp.status == 404:
                    return []
                if resp.status == 429:
                    retry_after = int(resp.headers.get("Retry-After", "5"))
                    backoff = retry_after * 2 ** (attempt - 1) + random.uniform(0, 1)
                    logger.warning(
                        "429 recebido para %s (tentativa %s/%s). Aguardando %.1fs antes de tentar novamente.",
                        url,
                        attempt,
                        max_retries,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                resp.raise_for_status()
                data = await resp.json()

        if data is None:
            logger.debug(
                "Sem resultados para %s/%s/%s/%s", orgao_cnpj, ano, seq, numero_item
            )
            return []
        if isinstance(data, list):
            return [d for d in data if isinstance(d, dict)]
        if isinstance(data, dict):
            inner = data.get("data")
            if isinstance(inner, list):
                return [d for d in inner if isinstance(d, dict)]
        logger.warning(
            "Unexpected resultados structure for %s/%s/%s/%s: %r",
            orgao_cnpj,
            ano,
            seq,
            numero_item,
            data,
        )
        return []

    logger.error(
        "Falha ao obter resultados para %s após %s tentativas", url, max_retries
    )
    raise RuntimeError(f"Too many 429 responses for {url}")


async def processar_resultados(
    data_inicial: str,
    data_final: str,
    modalidades: List[str],
    orgao_cnpj: str,
):
    itens = get_itens_para_resultados(
        data_inicial, data_final, modalidades, orgao_cnpj
    )
    if not itens:
        print("[Etapa 3] Nenhum item encontrado para buscar resultados.")
        return

    conn = get_connection()
    cur = conn.cursor()

    total_res = forn_up = falhas = 0
    concurrency = 5
    max_retries = 3
    sem = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession(headers=UA, trust_env=True) as session:
        async def worker(it):
            async with sem:
                ano = it["ano_compra"]
                seq = it["sequencial_compra"]
                num = it["numero_item"]
                cnpj = it["orgao_cnpj"]
                try:
                    resultados = await fetch_resultados(
                        session,
                        cnpj,
                        ano,
                        seq,
                        num,
                        max_retries=max_retries,
                    )
                    return it, None, resultados
                except Exception as e:
                    return it, e, []

        tasks = [asyncio.create_task(worker(it)) for it in itens]

        for coro in asyncio.as_completed(tasks):
            it, err, resultados = await coro
            ano = it["ano_compra"]
            seq = it["sequencial_compra"]
            num = it["numero_item"]  # numero_item do item de compra
            cnpj = it["orgao_cnpj"]
            print(
                f"[Etapa 3] Resultados do item {num} — compra {ano}/{seq} (órgão {cnpj})..."
            )

            if err:
                print(f"  ! Falha ao buscar resultados {ano}/{seq}/{num}: {err}")
                falhas += 1
                continue

            for r in resultados:
                if not isinstance(r, dict):
                    logger.debug("Ignorando resultado inválido: %r", r)
                    continue
                cnpj_f = r.get("niFornecedor")
                razao_f = r.get("nomeRazaoSocialFornecedor")
                valor_total = _to_decimal(r.get("valorTotalHomologado"))
                if cnpj_f:
                    upsert_fornecedor(cur, cnpj_f, razao_f)
                    forn_up += 1
                quantidade = r.get("quantidadeHomologada")
                valor_unitario_homologado = r.get("valorUnitarioHomologado")
                situacao = r.get("situacaoCompraItemResultadoNome") or r.get(
                    "situacaoCompraItemResultadoId"
                )
                # IMPORTANTE: num deve ser o numero_item REAL do item de compra (ex: 32)
                # Este valor vem da query SQL que busca itens da tabela itens_compra
                # NÃO deve ser um sequencial (1, 2, 3...)
                logger.debug(
                    f"[DEBUG] Processando resultado para item: "
                    f"ano={ano}, seq={seq}, numero_item={num} "
                    f"(este deve ser o numero_item REAL do item de compra, não um sequencial)"
                )
                upsert_resultado(
                    cur,
                    ano,
                    seq,
                    num,  # numero_item do item de compra (vem da query SQL - deve ser o valor REAL, ex: 32)
                    cnpj_f,
                    valor_total,
                    quantidade,
                    valor_unitario_homologado,
                    str(situacao) if situacao is not None else None,
                )
                atualizar_percentual_item(cur, ano, seq, num, valor_total)
                total_res += 1

            conn.commit()

    cur.close()
    conn.close()

    print(
        f"[Etapa 3] resultados upsertados: {total_res}, fornecedores upsertados: {forn_up}, falhas: {falhas}"
    )


def _chunk_anos(ano_inicial: int, ano_final: int, chunk_size: int):
    if chunk_size <= 0:
        yield ano_inicial, ano_final
        return
    atual = ano_inicial
    while atual <= ano_final:
        fim = min(atual + chunk_size - 1, ano_final)
        yield atual, fim
        atual = fim + 1


async def _cli_main():
    import argparse
    from datetime import date

    parser = argparse.ArgumentParser(
        description="Busca resultados dos itens (Etapa 3 do worker)."
    )
    def _parse_data(value: str) -> date:
        value = value.strip()
        try:
            return date.fromisoformat(value)
        except Exception:
            raise argparse.ArgumentTypeError(
                f"Data inválida: {value!r}. Use AAAA-MM-DD."
            )

    def _meses_entre(inicio: date, fim: date) -> int:
        return (fim.year - inicio.year) * 12 + (fim.month - inicio.month)

    parser.add_argument(
        "data_inicial",
        type=_parse_data,
        help="Data inicial da busca (inclusive). Formato AAAA-MM-DD.",
    )
    parser.add_argument(
        "data_final",
        type=_parse_data,
        help="Data final da busca (inclusive). Formato AAAA-MM-DD.",
    )
    parser.add_argument(
        "modalidade_nome",
        type=str,
        help=(
            "Modalidade da compra (nome exato ou código numérico, "
            "ex: 6 = Pregão - Eletrônico)."
        ),
    )
    parser.add_argument(
        "orgao_cnpj",
        type=str,
        help="CNPJ do órgão (sem máscara).",
    )
    args, extras = parser.parse_known_args()
    if extras:
        print(
            "[Etapa 3] Aviso: argumentos extras ignorados:",
            " ".join(extras),
        )

    if args.data_final < args.data_inicial:
        raise SystemExit("[Etapa 3] data_final deve ser maior ou igual a data_inicial.")

    if _meses_entre(args.data_inicial, args.data_final) > 12:
        raise SystemExit(
            "[Etapa 3] O período informado deve ser de no máximo 12 meses."
        )

    MODALIDADES_ALIASES = {
        8: ["Dispensa", "Dispensa de Licitação"],
    }

    modalidade_raw = args.modalidade_nome.strip()
    if modalidade_raw.isdigit():
        codigo = int(modalidade_raw)
        if codigo not in MODALIDADES:
            raise SystemExit(
                f"[Etapa 3] Código de modalidade inválido: {codigo}."
            )
        modalidades = MODALIDADES_ALIASES.get(codigo, [MODALIDADES[codigo]])
    else:
        modalidades = [modalidade_raw]

    print(
        f"\n[Etapa 3] Intervalo em execução: {args.data_inicial} - {args.data_final}"
    )
    await processar_resultados(
        args.data_inicial.isoformat(),
        args.data_final.isoformat(),
        modalidades,
        args.orgao_cnpj.strip(),
    )


if __name__ == "__main__":
    asyncio.run(_cli_main())
