import logging
from pathlib import Path
import pandas as pd
from django.db import transaction, connection
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from psycopg2 import sql as psycopg2_sql

from .models import (
    AgenteResponsavel,
    AgenteResponsavelFuncao,
    PostoGraduacao,
    Especializacao,
)

logger = logging.getLogger(__name__)

FIXTURE_DIR = Path(__file__).resolve().parent / 'fixtures'


def _as_int(v):
    if pd.isna(v):
        return None
    try:
        return int(float(v))
    except Exception:
        return None


def _as_clean_str(v):
    """Converte valores do Excel para string sem sufixo '.0' quando for inteiro."""
    if pd.isna(v) or v is None:
        return None
    try:
        f = float(v)
        if f.is_integer():
            return str(int(f))
        return str(f)
    except Exception:
        s = str(v).strip()
        # fallback: remove '.0' final se existir
        if s.endswith('.0'):
            try:
                f = float(s)
                if float(f).is_integer():
                    return str(int(f))
            except Exception:
                pass
        return s or None


def _require_fields(row, cols, ctx, row_index=None, string_fields=None):
    """Valida se os campos obrigatórios estão presentes e corretos."""
    if string_fields is None:
        string_fields = []

    missing = {}
    for c in cols:
        if c in string_fields:
            # Para campos string, apenas verifica se não é NaN/vazio
            if pd.isna(row.get(c)) or str(row.get(c)).strip() == '':
                missing[c] = row.get(c)
        else:
            # Para campos numéricos, tenta converter para int
            if _as_int(row.get(c)) is None:
                missing[c] = row.get(c)

    if missing:
        id_info = f"ID={row.get('id')}" if 'id' in row else f"linha={row_index}"
        logger.warning(f"⏭️ Linha ignorada em {ctx} ({id_info}): campos inválidos {missing}")
        return False
    return True


def load_fixture(filename, required_columns=None):
    """Carrega fixture XLSX ou CSV."""
    # Tenta XLSX primeiro
    base_name = filename.replace('.xlsx', '')
    xlsx_path = FIXTURE_DIR / f"{base_name}.xlsx"
    csv_path = FIXTURE_DIR / f"{base_name}.csv"

    df = None
    file_type = ""

    if xlsx_path.exists():
        try:
            df = pd.read_excel(xlsx_path)
            file_type = "XLSX"
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar XLSX {filename}: {e}")

    if df is None and csv_path.exists():
        try:
            df = pd.read_csv(csv_path, sep=',')
            file_type = "CSV"
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar CSV {filename}: {e}")

    if df is None:
        logger.warning(f"❌ Nenhum arquivo encontrado: {xlsx_path} ou {csv_path}")
        return None

    df.columns = df.columns.str.strip()

    if required_columns:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"❌ Colunas obrigatórias ausentes em {filename}: {missing_cols}")
            logger.error(f"📋 Colunas disponíveis: {list(df.columns)}")
            return None

    logger.info(f"📄 Carregado {filename} ({file_type}): {len(df)} linhas, colunas: {list(df.columns)}")
    return df


@receiver(post_migrate)
def load_fixtures_agentes_responsaveis(sender, **kwargs):
    if sender.name != 'django_licitacao360.apps.agentes_responsaveis':
        return

    logger.info("📥 Iniciando carga de fixtures XLSX para Cadastro de Agentes Responsáveis...")

    try:
        with transaction.atomic():
            # 1. Postos
            df = load_fixture('postos_graduacao.xlsx', ['id_posto', 'nome'])
            if df is not None:
                logger.info("📄 Processando postos de graduação...")
                for _, row in df.iterrows():
                    if not PostoGraduacao.objects.filter(id_posto=row['id_posto']).exists():
                        obj, created = PostoGraduacao.objects.update_or_create(
                            id_posto=row['id_posto'],
                            defaults={
                                'nome': row['nome'],
                                'abreviatura': row.get('abreviatura', '')
                            }
                        )
                        if created:
                            logger.info(f"✅ Criado posto: {obj.nome} (id={obj.id_posto})")

            # 2. Especializações
            df = load_fixture('especializacoes.xlsx', ['id_especializacao', 'nome'])
            if df is not None:
                logger.info("📄 Processando especializações...")
                for _, row in df.iterrows():
                    if not Especializacao.objects.filter(id_especializacao=row['id_especializacao']).exists():
                        obj, created = Especializacao.objects.update_or_create(
                            id_especializacao=row['id_especializacao'],
                            defaults={
                                'nome': row['nome'],
                                'abreviatura': row.get('abreviatura', '')
                            }
                        )
                        if created:
                            logger.info(f"✅ Criada especialização: {obj.nome} (id={obj.id_especializacao})")

            # 3. Funções
            df = load_fixture('agentes_resposaveis_funcao.xlsx', ['id_funcao', 'nome'])
            if df is not None:
                logger.info("📄 Processando funções de agentes responsáveis...")
                for _, row in df.iterrows():
                    if not AgenteResponsavelFuncao.objects.filter(id_funcao=row['id_funcao']).exists():
                        obj, created = AgenteResponsavelFuncao.objects.update_or_create(
                            id_funcao=row['id_funcao'],
                            defaults={'nome': row['nome']}
                        )
                        if created:
                            logger.info(f"✅ Criada função: {obj.nome} (id={obj.id_funcao})")

            # 4. Agentes Responsáveis
            df = load_fixture('agentes_resposaveis.xlsx', ['id_agente_responsavel', 'nome_de_guerra', 'posto_graduacao'])
            if df is not None:
                logger.info("📄 Processando agentes responsáveis...")
                loaded_count = 0

                for idx, row in df.iterrows():
                    if not _require_fields(
                        row,
                        ['id_agente_responsavel', 'nome_de_guerra', 'posto_graduacao'],
                        'agentes_resposaveis.xlsx',
                        row_index=idx + 2,
                        string_fields=['nome_de_guerra']
                    ):
                        logger.warning(f"❌ Linha {idx + 1} rejeitada pela validação")
                        continue

                    try:
                        agente_id = _as_int(row['id_agente_responsavel'])
                        posto_id = _as_int(row['posto_graduacao'])
                        posto_graduacao = PostoGraduacao.objects.get(id_posto=posto_id)

                        especializacao = None
                        especializacao_id = None
                        if 'especializacao' in row and not pd.isna(row['especializacao']):
                            especializacao_id = _as_int(row['especializacao'])
                            if especializacao_id:
                                especializacao = Especializacao.objects.get(id_especializacao=especializacao_id)

                        logger.info("🔍 DEBUG: Criando/atualizando agente responsável...")
                        logger.info(
                            f"🔍 DEBUG: nome_de_guerra='{row['nome_de_guerra']}', "
                            f"posto_graduacao={posto_graduacao}, especializacao={especializacao}"
                        )

                        obj, created = AgenteResponsavel.objects.update_or_create(
                            id_agente_responsavel=agente_id,
                            defaults={
                                'nome_de_guerra': row['nome_de_guerra'],
                                'posto_graduacao': posto_graduacao,
                                'especializacao': especializacao,
                                'departamento': _as_clean_str(row.get('departamento')),
                                'divisao': _as_clean_str(row.get('divisao')),
                                'os_funcao': _as_clean_str(row.get('os_funcao')),
                                'os_qualificacao': _as_clean_str(row.get('os_qualificacao'))
                            }
                        )

                        if created:
                            logger.info(f"✅ Criado agente responsável: {obj.nome_de_guerra} (id={obj.id_agente_responsavel})")
                            loaded_count += 1
                        else:
                            logger.info(f"🔄 Atualizado agente responsável: {obj.nome_de_guerra} (id={obj.id_agente_responsavel})")

                        # Funções
                        if 'funcoes' in row and not pd.isna(row['funcoes']):
                            funcoes_ids = str(row['funcoes']).split(',')
                            funcoes_list = []
                            for fid in funcoes_ids:
                                fid = fid.strip()
                                if fid:
                                    try:
                                        funcao = AgenteResponsavelFuncao.objects.get(id_funcao=int(fid))
                                        funcoes_list.append(funcao)
                                    except (ValueError, AgenteResponsavelFuncao.DoesNotExist):
                                        logger.warning(f"⚠️ Função não encontrada: {fid}")
                            if funcoes_list:
                                obj.funcoes.set(funcoes_list)

                        logger.info(f"🎉 Agente Responsável {obj.nome_de_guerra} processado com sucesso!")

                    except PostoGraduacao.DoesNotExist as e:
                        logger.error(f"❌ Posto/Graduação não encontrado (id={posto_id}): {e}")
                    except Especializacao.DoesNotExist as e:
                        logger.error(f"❌ Especialização não encontrada (id={especializacao_id}): {e}")
                    except Exception as e:
                        logger.exception(f"❌ Erro ao importar Agente Responsável ID={row.get('id_agente_responsavel')}: {e}")

                logger.info(f"✅ Carregados {loaded_count} agentes responsáveis!")

            logger.info("✅ Carga de fixtures XLSX concluída!")

            # Ajusta sequences do Postgres para modelos que foram criados com ids fixos
            try:
                models_to_fix = [PostoGraduacao, Especializacao, AgenteResponsavelFuncao, AgenteResponsavel]
                for mdl in models_to_fix:
                    table = mdl._meta.db_table
                    pk = mdl._meta.pk.name
                    with connection.cursor() as cursor:
                        # usa psycopg2.sql para montar identifiers/strings corretamente:
                        # - pg_get_serial_sequence espera literais para table/column (ex: 'my_table','id')
                        # - SELECT MAX(column) FROM table precisa de identifiers (sem aspas)
                        cursor.execute(
                            psycopg2_sql.SQL(
                                "SELECT setval(pg_get_serial_sequence({table_lit}, {pk_lit}), "
                                "COALESCE((SELECT MAX({pk_ident}) FROM {table_ident}), 1), true);"
                            ).format(
                                table_lit=psycopg2_sql.Literal(table),
                                pk_lit=psycopg2_sql.Literal(pk),
                                pk_ident=psycopg2_sql.Identifier(pk),
                                table_ident=psycopg2_sql.Identifier(table),
                            )
                        )
                        logger.info(f"🔧 Sequence ajustada para {table}.{pk}")
            except Exception as e:
                logger.exception(f"❌ Não foi possível ajustar sequences: {e}")

    except Exception as e:
        logger.exception(f"❌ Erro ao carregar fixtures de agentes responsáveis: {e}")