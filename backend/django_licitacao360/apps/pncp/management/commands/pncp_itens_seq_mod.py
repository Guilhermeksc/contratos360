import asyncio
import os
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from db import get_connection

UA = {"User-Agent": "GerATA Worker/1.0 (+https://example.local)"}
MAX_CONCURRENCY = 5
MAX_RETRIES = 5
PAGE_SIZE = 999_999_999  # força a API a retornar todos os itens em uma única página
DEBUG = os.getenv("PNCP_DEBUG", "1").lower() not in ("0", "false", "no")

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


def _debug(msg: str) -> None:
    if DEBUG:
        print(f"[Etapa 2][DEBUG] {msg}")


def get_compras_para_itens(
    data_inicial: str,
    data_final: str,
    modalidades: List[str],
    orgao_cnpj: str,
) -> List[Dict[str, Any]]:
    """
    Busca as compras no banco, já com o CNPJ do órgão, necessárias para montar a URL dos itens:
      /api/pncp/v1/orgaos/{cnpj_orgao}/compras/{ano}/{sequencial}/itens
    """
    from django.db import connection
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
        _debug(f"Nenhuma modalidade encontrada para: {modalidades}")
        return []
    
    placeholders = ", ".join(["%s"] * len(modalidades_ids))
    params: List[Any] = [data_inicial, data_final, *modalidades_ids, orgao_cnpj]

    sql = f"""
    SELECT c.ano_compra, c.sequencial_compra,
           uc.codigo_unidade,
           o.cnpj AS orgao_cnpj
      FROM compras c
      JOIN unidades_compradoras uc ON uc.codigo_unidade = c.codigo_unidade
      JOIN orgaos o ON o.cnpj = uc.orgao_cnpj
         WHERE c.data_publicacao_pncp BETWEEN %s AND %s
             AND c.modalidade_id IN ({placeholders})
             AND o.cnpj = %s
    ORDER BY c.ano_compra DESC, c.sequencial_compra DESC;
    """
    _debug(
        "Filtro compras: "
        f"data_publicacao_pncp BETWEEN {data_inicial} AND {data_final}, "
        f"modalidades_ids={modalidades_ids}, modalidades_nomes={modalidades}, orgao_cnpj={orgao_cnpj}"
    )

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()

    if not rows:
        _debug("Nenhuma compra com o filtro. Listando modalidades no período/órgão...")
        # Busca modalidades usando SQL direto
        cur.execute(
            """
            SELECT DISTINCT m.nome
              FROM compras c
              JOIN unidades_compradoras uc ON uc.codigo_unidade = c.codigo_unidade
              JOIN orgaos o ON o.cnpj = uc.orgao_cnpj
              LEFT JOIN pncp_modalidade m ON m.id = c.modalidade_id
             WHERE c.data_publicacao_pncp BETWEEN %s AND %s
               AND o.cnpj = %s
               AND m.nome IS NOT NULL
             ORDER BY m.nome;
            """,
            [data_inicial, data_final, orgao_cnpj],
        )
        modalidades_encontradas = [r[0] for r in cur.fetchall() if r[0]]
        _debug(f"Modalidades encontradas no período/órgão: {modalidades_encontradas}")
    cur.close()
    conn.close()

    out = []
    for ano, seq, cod_unid, orgao_cnpj in rows:
        out.append(
            {
                "ano_compra": int(ano),
                "sequencial_compra": int(seq),
                "codigo_unidade": cod_unid,
                "orgao_cnpj": str(orgao_cnpj).zfill(14),
            }
        )
    return out


def upsert_item(
    cur,
    ano: int,
    seq: int,
    numero_item: int,
    descricao: Optional[str],
    unidade_medida: Optional[str],
    valor_unitario_estimado: Optional[Decimal],
    valor_total_estimado: Optional[Decimal],
    quantidade: Optional[Decimal],
    situacao_compra_item_nome: Optional[str],
    tem_resultado: Optional[int],
) -> None:
    # IMPORTANTE: numero_item deve ser o número REAL do item (ex: 32), não um sequencial
    item_id = f"{ano}::{seq}::{numero_item}"
    _debug(
        f"[DEBUG] upsert_item: item_id={item_id}, "
        f"ano={ano}, seq={seq}, numero_item={numero_item}"
    )
    cur.execute(
        """
        INSERT INTO itens_compra (
            item_id,
            ano_compra,
            sequencial_compra,
            numero_item,
            descricao,
            unidade_medida,
            valor_unitario_estimado,
            valor_total_estimado,
            quantidade,
            percentual_economia,
            situacao_compra_item_nome,
            tem_resultado
        )
        VALUES (%s, %s, %s, %s, COALESCE(%s,''), COALESCE(%s,''), %s, %s, %s, %s, COALESCE(%s,''), %s)
        ON CONFLICT (ano_compra, sequencial_compra, numero_item) DO UPDATE
          SET descricao = EXCLUDED.descricao,
              unidade_medida = EXCLUDED.unidade_medida,
              valor_unitario_estimado = EXCLUDED.valor_unitario_estimado,
              valor_total_estimado = EXCLUDED.valor_total_estimado,
              quantidade = EXCLUDED.quantidade,
              percentual_economia = EXCLUDED.percentual_economia,
              situacao_compra_item_nome = EXCLUDED.situacao_compra_item_nome,
              tem_resultado = EXCLUDED.tem_resultado;
        """,
        (
            item_id,
            ano,
            seq,
            numero_item,
            descricao,
            unidade_medida,
            valor_unitario_estimado,
            valor_total_estimado,
            quantidade,
            None,
            situacao_compra_item_nome,
            tem_resultado,
        ),
    )


def _to_decimal(value: Optional[Any]) -> Optional[Decimal]:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


async def fetch_itens(
    session: aiohttp.ClientSession,
    orgao_cnpj: str,
    ano: int,
    seq: int,
    max_retries: int = MAX_RETRIES,
) -> List[Dict[str, Any]]:
    """
    Busca TODOS os itens da compra da API do PNCP.
    IMPORTANTE: A API retorna TODOS os itens, não apenas os homologados.
    O numeroItem retornado deve ser o número REAL do item na compra.
    """
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{orgao_cnpj}/compras/{ano}/{seq}/itens"
    params = {"tamanhoPagina": PAGE_SIZE}
    _debug(f"GET {url} params={params} (buscando TODOS os itens da compra)")
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, timeout=60, params=params) as resp:
                _debug(
                    f"Resposta {resp.status} para {ano}/{seq} (tentativa {attempt}/{max_retries})"
                )
                if resp.status == 404:
                    _debug(f"Nenhum item (404) para {ano}/{seq}")
                    return []
                if resp.status == 429:
                    retry_after = resp.headers.get("Retry-After")
                    wait = (
                        int(retry_after)
                        if retry_after and retry_after.isdigit()
                        else 2 ** attempt
                    )
                    _debug(
                        f"Rate limit para {ano}/{seq}; aguardando {wait}s antes de retry"
                    )
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = await resp.json()
                itens_list = data if isinstance(data, list) else data.get("data", [])
                _debug(
                    f"Itens recebidos para {ano}/{seq}: {len(itens_list)}"
                )
                # Log detalhado dos primeiros itens para debug
                if itens_list and len(itens_list) <= 3:
                    for idx, item in enumerate(itens_list):
                        _debug(
                            f"  Item[{idx}]: numeroItem={item.get('numeroItem')}, "
                            f"descricao={item.get('descricao', '')[:50]}..."
                        )
                return itens_list
        except asyncio.CancelledError:
            _debug(f"Cancelado durante fetch {ano}/{seq}")
            raise
        except aiohttp.ClientError as e:
            _debug(
                f"Erro de rede em {ano}/{seq} (tentativa {attempt}/{max_retries}): {e}"
            )
            if attempt == max_retries:
                raise
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"Falha após {max_retries} tentativas")


async def worker(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    it: Dict[str, Any],
) -> Tuple[int, int, List[Dict[str, Any]], Optional[str]]:
    ano = it["ano_compra"]
    seq = it["sequencial_compra"]
    cnpj = it["orgao_cnpj"]
    try:
        _debug(f"Iniciando worker {ano}/{seq} orgao={cnpj}")
        async with sem:
            itens = await fetch_itens(session, cnpj, ano, seq)
        _debug(f"Worker concluido {ano}/{seq} itens={len(itens)}")
        return ano, seq, itens, None
    except asyncio.CancelledError:
        _debug(f"Worker cancelado {ano}/{seq}")
        raise
    except Exception as e:
        _debug(f"Worker falhou {ano}/{seq}: {e}")
        return ano, seq, [], str(e)


async def processar_itens(
    data_inicial: str,
    data_final: str,
    modalidades: List[str],
    orgao_cnpj: str,
) -> None:
    compras = get_compras_para_itens(
        data_inicial, data_final, modalidades, orgao_cnpj
    )
    if not compras:
        print("[Etapa 2] Nenhuma compra encontrada para buscar itens.")
        return

    _debug(
        f"Compras carregadas: {len(compras)} | intervalo={data_inicial}-{data_final}"
    )
    _debug(f"MAX_CONCURRENCY={MAX_CONCURRENCY} MAX_RETRIES={MAX_RETRIES}")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE itens_compra ADD COLUMN tem_resultado INTEGER")
        conn.commit()
        _debug("Coluna tem_resultado criada em itens_compra.")
    except Exception as e:
        msg = str(e).lower()
        if "duplicate" not in msg and "exists" not in msg and "duplicate column" not in msg:
            raise
    total_upserts = 0
    falhas = 0

    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async with aiohttp.ClientSession(headers=UA, trust_env=True) as session:
        tasks = [
            asyncio.create_task(worker(session, sem, comp)) for comp in compras
        ]
        _debug(f"Tasks criadas: {len(tasks)}")
        try:
            for t in asyncio.as_completed(tasks):
                ano, seq, itens, err = await t
                if err:
                    print(f"  ! Falha ao buscar itens {ano}/{seq}: {err}")
                    falhas += 1
                    continue

                # IMPORTANTE: Quando há apenas um item homologado, a API pode retornar numeroItem: 1
                # mesmo que o item real seja outro número (ex: 30, 29, 28). Precisamos verificar
                # se há uma inconsistência e corrigir usando o número real do item.
                # Se houver apenas um item e numeroItem=1, pode ser um problema da API.
                # Vamos usar o valor da API mas adicionar logs para identificar o problema.
                
                # Verifica se há apenas um item e se numeroItem=1 (possível problema da API)
                # Quando há apenas um item homologado, a API pode retornar numeroItem=1
                # mesmo que o item real seja outro número. Nesse caso, precisamos verificar
                # se há outros itens na compra que não estão na lista retornada.
                total_itens_retornados = len(itens)
                itens_com_numero_1 = [item for item in itens if item.get("numeroItem") == 1]
                
                if total_itens_retornados == 1 and len(itens_com_numero_1) == 1:
                    _debug(
                        f"[AVISO] Compra {ano}/{seq} tem apenas 1 item retornado e numeroItem=1. "
                        f"Isso pode indicar que a API retornou um sequencial ao invés do número real do item. "
                        f"O item será salvo com numero_item=1, mas pode ser que o número real seja diferente. "
                        f"Verifique manualmente no PNCP se há outros itens nesta compra."
                    )
                
                for idx, item in enumerate(itens):
                    numero_item_raw = item.get("numeroItem")
                    if numero_item_raw is None:
                        _debug(f"Item {idx} sem numeroItem, pulando...")
                        continue
                    
                    # IMPORTANTE: numeroItem da API deve ser o número REAL do item (ex: 32)
                    # NÃO deve ser um sequencial (1, 2, 3...)
                    # Se a API retornou numeroItem=1 quando há apenas um item, pode ser um problema
                    # mas vamos usar o valor retornado pela API
                    numero_item = int(numero_item_raw)
                    
                    _debug(
                        f"[DEBUG] Processando item: compra={ano}/{seq}, "
                        f"total_itens_retornados={total_itens_retornados}, indice_array={idx}, "
                        f"numeroItem_API={numero_item_raw}, numero_item_final={numero_item}"
                    )
                    
                    descricao = (
                        item.get("descricao") or item.get("descricaoItem") or ""
                    )
                    unidade = item.get("unidadeMedida") or ""
                    valor_unitario_estimado = _to_decimal(
                        item.get("valorUnitarioEstimado")
                    )
                    valor_total_estimado = _to_decimal(item.get("valorTotal"))
                    quantidade = _to_decimal(item.get("quantidade"))
                    situacao_nome = item.get("situacaoCompraItemNome")
                    if situacao_nome is not None:
                        situacao_nome = str(situacao_nome).strip()
                    tem_resultado_raw = item.get("temResultado")
                    if tem_resultado_raw is None:
                        tem_resultado = None
                    else:
                        tem_resultado = 1 if bool(tem_resultado_raw) else 0
                    
                    _debug(
                        f"[DEBUG] Salvando item: ano={ano}, seq={seq}, "
                        f"numero_item={numero_item} (deve ser o número REAL do item)"
                    )
                    upsert_item(
                        cur,
                        ano,
                        seq,
                        numero_item,  # Usa numero_item diretamente da API
                        descricao,
                        unidade,
                        valor_unitario_estimado,
                        valor_total_estimado,
                        quantidade,
                        situacao_nome,
                        tem_resultado,
                    )
                    total_upserts += 1
                conn.commit()
        except asyncio.CancelledError:
            _debug("Cancelamento recebido; aguardando finalização das tasks...")
            raise
        finally:
            pendentes = [t for t in tasks if not t.done()]
            if pendentes:
                _debug(f"Cancelando tasks pendentes: {len(pendentes)}")
                for t in pendentes:
                    t.cancel()
                await asyncio.gather(*pendentes, return_exceptions=True)

    cur.close()
    conn.close()
    print(
        f"[Etapa 2] Itens upsertados: {total_upserts} | requisições com falha: {falhas}"
    )


async def _cli_main():
    import argparse
    from datetime import date

    parser = argparse.ArgumentParser(
        description="Busca itens das compras (Etapa 2 do worker)."
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
            "[Etapa 2] Aviso: argumentos extras ignorados:",
            " ".join(extras),
        )

    if args.data_final < args.data_inicial:
        raise SystemExit("[Etapa 2] data_final deve ser maior ou igual a data_inicial.")

    if _meses_entre(args.data_inicial, args.data_final) > 12:
        raise SystemExit(
            "[Etapa 2] O período informado deve ser de no máximo 12 meses."
        )

    print(
        f"\n[Etapa 2] Intervalo em execução: {args.data_inicial} - {args.data_final}"
    )
    MODALIDADES_ALIASES = {
        8: ["Dispensa", "Dispensa de Licitação"],
    }

    modalidade_raw = args.modalidade_nome.strip()
    if modalidade_raw.isdigit():
        codigo = int(modalidade_raw)
        if codigo not in MODALIDADES:
            raise SystemExit(
                f"[Etapa 2] Código de modalidade inválido: {codigo}."
            )
        modalidades = MODALIDADES_ALIASES.get(codigo, [MODALIDADES[codigo]])
    else:
        modalidades = [modalidade_raw]

    await processar_itens(
        args.data_inicial.isoformat(),
        args.data_final.isoformat(),
        modalidades,
        args.orgao_cnpj.strip(),
    )


if __name__ == "__main__":
    asyncio.run(_cli_main())
