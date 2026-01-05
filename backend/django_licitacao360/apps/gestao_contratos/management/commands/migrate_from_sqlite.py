"""
Management command para migrar dados do SQLite para PostgreSQL
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import (
    Uasg,
    Contrato,
    StatusContrato,
    RegistroStatus,
    RegistroMensagem,
    LinksContrato,
    FiscalizacaoContrato,
    HistoricoContrato,
    Empenho,
    ItemContrato,
    ArquivoContrato,
)


class Command(BaseCommand):
    help = 'Migra dados do SQLite para PostgreSQL'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--db-path',
            type=str,
            required=True,
            help='Caminho para o arquivo SQLite (ex: /path/to/gerenciador_uasg.db)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar no banco (apenas valida)',
        )
    
    def _parse_date(self, date_str):
        """Converte string de data para date"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Tenta formato brasileiro
            try:
                return datetime.strptime(date_str, '%d/%m/%Y').date()
            except (ValueError, TypeError):
                return None
    
    def _parse_decimal(self, value):
        """Converte string numérica para Decimal"""
        if not value:
            return None
        try:
            cleaned = str(value).replace(',', '.')
            return Decimal(cleaned)
        except (InvalidOperation, ValueError, TypeError):
            return None
    
    def _parse_datetime(self, datetime_str):
        """Converte string de datetime para datetime"""
        if not datetime_str:
            return None
        try:
            return datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
        except (ValueError, TypeError):
            return None
    
    def _migrate_uasgs(self, conn, dry_run=False):
        """Migra tabela uasgs"""
        cursor = conn.cursor()
        cursor.execute("SELECT uasg_code, nome_resumido FROM uasgs")
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            uasg_code, nome_resumido = row
            if not dry_run:
                try:
                    uasg_int = int(str(uasg_code))
                except (TypeError, ValueError):
                    self.stdout.write(f"⚠ Código de UASG inválido: {uasg_code}")
                    continue

                sigla = (nome_resumido or str(uasg_int))[:50]
                Uasg.objects.update_or_create(
                    id_uasg=uasg_int,
                    defaults={
                        'uasg': uasg_int,
                        'sigla_om': sigla,
                        'nome_om': nome_resumido,
                        'classificacao': 'Nao informado',
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} UASGs')
        return count
    
    def _migrate_contratos(self, conn, dry_run=False):
        """Migra tabela contratos"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, uasg_code, numero, licitacao_numero, processo,
                   fornecedor_nome, fornecedor_cnpj, objeto, valor_global,
                   vigencia_inicio, vigencia_fim, tipo, modalidade,
                   contratante_orgao_unidade_gestora_codigo,
                   contratante_orgao_unidade_gestora_nome_resumido,
                   manual, raw_json
            FROM contratos
        """)
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            (id, uasg_code, numero, licitacao_numero, processo,
             fornecedor_nome, fornecedor_cnpj, objeto, valor_global,
             vigencia_inicio, vigencia_fim, tipo, modalidade,
             contratante_orgao_unidade_gestora_codigo,
             contratante_orgao_unidade_gestora_nome_resumido,
             manual, raw_json) = row
            
            if not dry_run:
                try:
                    raw_json_data = json.loads(raw_json) if raw_json else None
                except (json.JSONDecodeError, TypeError):
                    raw_json_data = None

                try:
                    uasg_int = int(str(uasg_code))
                except (TypeError, ValueError):
                    self.stdout.write(f"⚠ Código de UASG inválido para contrato {id}: {uasg_code}")
                    continue

                Uasg.objects.get_or_create(
                    id_uasg=uasg_int,
                    defaults={
                        'uasg': uasg_int,
                        'sigla_om': str(uasg_int),
                        'nome_om': contratante_orgao_unidade_gestora_nome_resumido,
                        'classificacao': 'Nao informado',
                    }
                )
                
                Contrato.objects.update_or_create(
                    id=str(id),
                    defaults={
                        'uasg_id': uasg_int,
                        'numero': numero,
                        'licitacao_numero': licitacao_numero,
                        'processo': processo,
                        'fornecedor_nome': fornecedor_nome,
                        'fornecedor_cnpj': fornecedor_cnpj,
                        'objeto': objeto,
                        'valor_global': self._parse_decimal(valor_global),
                        'vigencia_inicio': self._parse_date(vigencia_inicio),
                        'vigencia_fim': self._parse_date(vigencia_fim),
                        'tipo': tipo,
                        'modalidade': modalidade,
                        'contratante_orgao_unidade_gestora_codigo': contratante_orgao_unidade_gestora_codigo,
                        'contratante_orgao_unidade_gestora_nome_resumido': contratante_orgao_unidade_gestora_nome_resumido,
                        'manual': bool(manual) if manual is not None else False,
                        'raw_json': raw_json_data,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} contratos')
        return count
    
    def _migrate_status_contratos(self, conn, dry_run=False):
        """Migra tabela status_contratos"""
        cursor = conn.cursor()
        
        # Verifica se a coluna termo_aditivo_edit existe
        cursor.execute("PRAGMA table_info(status_contratos)")
        columns = [col[1] for col in cursor.fetchall()]
        has_termo_aditivo = 'termo_aditivo_edit' in columns
        
        if has_termo_aditivo:
            cursor.execute("""
                SELECT contrato_id, uasg_code, status, objeto_editado,
                       portaria_edit, termo_aditivo_edit, radio_options_json, data_registro
                FROM status_contratos
            """)
        else:
            cursor.execute("""
                SELECT contrato_id, uasg_code, status, objeto_editado,
                       portaria_edit, NULL as termo_aditivo_edit, radio_options_json, data_registro
                FROM status_contratos
            """)
        
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            (contrato_id, uasg_code, status, objeto_editado,
             portaria_edit, termo_aditivo_edit, radio_options_json, data_registro) = row
            
            if not dry_run:
                # Extrai valores do JSON para os novos campos
                pode_renovar = False
                custeio = False
                natureza_continuada = False
                tipo_contrato = None
                
                if radio_options_json:
                    try:
                        radio_options = json.loads(radio_options_json) if isinstance(radio_options_json, str) else radio_options_json
                        
                        # Mapeia valores do JSON para os novos campos booleanos
                        # Aceita diferentes formatos de chave e valores
                        pode_renovar_val = radio_options.get('Pode Renovar?') or radio_options.get('pode_renovar') or radio_options.get('Pode Renovar')
                        if pode_renovar_val:
                            pode_renovar = str(pode_renovar_val).lower() in ['sim', 'yes', 'true', '1', 's']
                        
                        custeio_val = radio_options.get('Custeio?') or radio_options.get('custeio') or radio_options.get('Custeio')
                        if custeio_val:
                            custeio = str(custeio_val).lower() in ['sim', 'yes', 'true', '1', 's']
                        
                        natureza_continuada_val = radio_options.get('Natureza Continuada?') or radio_options.get('natureza_continuada') or radio_options.get('Natureza Continuada')
                        if natureza_continuada_val:
                            natureza_continuada = str(natureza_continuada_val).lower() in ['sim', 'yes', 'true', '1', 's']
                        
                        # Extrai tipo_contrato se existir no JSON
                        tipo_contrato_val = radio_options.get('Tipo Contrato') or radio_options.get('tipo_contrato') or radio_options.get('Tipo')
                        if tipo_contrato_val:
                            tipo_contrato_str = str(tipo_contrato_val).lower()
                            if tipo_contrato_str in ['material', 'm']:
                                tipo_contrato = 'material'
                            elif tipo_contrato_str in ['servico', 'serviço', 's']:
                                tipo_contrato = 'servico'
                    except (json.JSONDecodeError, TypeError, AttributeError):
                        # Se houver erro ao processar JSON, mantém valores padrão
                        pass
                
                StatusContrato.objects.update_or_create(
                    contrato_id=str(contrato_id),
                    defaults={
                        'uasg_code': uasg_code,
                        'status': status,
                        'objeto_editado': objeto_editado,
                        'portaria_edit': portaria_edit,
                        'termo_aditivo_edit': termo_aditivo_edit,
                        'pode_renovar': pode_renovar,
                        'custeio': custeio,
                        'natureza_continuada': natureza_continuada,
                        'tipo_contrato': tipo_contrato,
                        'data_registro': data_registro,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} status de contratos')
        return count
    
    def _migrate_registros_status(self, conn, dry_run=False):
        """Migra tabela registros_status"""
        cursor = conn.cursor()
        cursor.execute("SELECT id, contrato_id, uasg_code, texto FROM registros_status")
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            id, contrato_id, uasg_code, texto = row
            if not dry_run:
                RegistroStatus.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'uasg_code': uasg_code,
                        'texto': texto,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} registros de status')
        return count
    
    def _migrate_registro_mensagem(self, conn, dry_run=False):
        """Migra tabela registro_mensagem"""
        cursor = conn.cursor()
        cursor.execute("SELECT id, contrato_id, texto FROM registro_mensagem")
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            id, contrato_id, texto = row
            if not dry_run:
                RegistroMensagem.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'texto': texto,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} registros de mensagem')
        return count
    
    def _migrate_links_contratos(self, conn, dry_run=False):
        """Migra tabela links_contratos"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contrato_id, link_contrato, link_ta, link_portaria,
                   link_pncp_espc, link_portal_marinha
            FROM links_contratos
        """)
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            (id, contrato_id, link_contrato, link_ta, link_portaria,
             link_pncp_espc, link_portal_marinha) = row
            if not dry_run:
                LinksContrato.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'link_contrato': link_contrato,
                        'link_ta': link_ta,
                        'link_portaria': link_portaria,
                        'link_pncp_espc': link_pncp_espc,
                        'link_portal_marinha': link_portal_marinha,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} links de contratos')
        return count
    
    def _migrate_fiscalizacao(self, conn, dry_run=False):
        """Migra tabela fiscalizacao (se existir)"""
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='fiscalizacao'
        """)
        if not cursor.fetchone():
            self.stdout.write('  Tabela fiscalizacao não encontrada (pode não existir no SQLite)')
            return 0
        
        cursor.execute("""
            SELECT id, contrato_id, gestor, gestor_substituto, fiscal_tecnico,
                   fiscal_tec_substituto, fiscal_administrativo, fiscal_admin_substituto,
                   observacoes, data_criacao, data_atualizacao
            FROM fiscalizacao
        """)
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            (id, contrato_id, gestor, gestor_substituto, fiscal_tecnico,
             fiscal_tec_substituto, fiscal_administrativo, fiscal_admin_substituto,
             observacoes, data_criacao, data_atualizacao) = row
            if not dry_run:
                FiscalizacaoContrato.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'gestor': gestor,
                        'gestor_substituto': gestor_substituto,
                        'fiscal_tecnico': fiscal_tecnico,
                        'fiscal_tec_substituto': fiscal_tec_substituto,
                        'fiscal_administrativo': fiscal_administrativo,
                        'fiscal_admin_substituto': fiscal_admin_substituto,
                        'observacoes': observacoes,
                        'data_criacao': self._parse_datetime(data_criacao),
                        'data_atualizacao': self._parse_datetime(data_atualizacao),
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} registros de fiscalização')
        return count
    
    def _migrate_historico(self, conn, dry_run=False):
        """Migra tabela historico"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contrato_id, receita_despesa, numero, observacao, ug, gestao,
                   fornecedor_cnpj, fornecedor_nome, tipo, categoria, processo, objeto,
                   modalidade, licitacao_numero, data_assinatura, data_publicacao,
                   vigencia_inicio, vigencia_fim, valor_global, raw_json
            FROM historico
        """)
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            (id, contrato_id, receita_despesa, numero, observacao, ug, gestao,
             fornecedor_cnpj, fornecedor_nome, tipo, categoria, processo, objeto,
             modalidade, licitacao_numero, data_assinatura, data_publicacao,
             vigencia_inicio, vigencia_fim, valor_global, raw_json) = row
            
            if not dry_run:
                try:
                    raw_json_data = json.loads(raw_json) if raw_json else None
                except (json.JSONDecodeError, TypeError):
                    raw_json_data = None
                
                HistoricoContrato.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'receita_despesa': receita_despesa,
                        'numero': numero,
                        'observacao': observacao,
                        'ug': ug,
                        'gestao': gestao,
                        'fornecedor_cnpj': fornecedor_cnpj,
                        'fornecedor_nome': fornecedor_nome,
                        'tipo': tipo,
                        'categoria': categoria,
                        'processo': processo,
                        'objeto': objeto,
                        'modalidade': modalidade,
                        'licitacao_numero': licitacao_numero,
                        'data_assinatura': self._parse_date(data_assinatura),
                        'data_publicacao': self._parse_date(data_publicacao),
                        'vigencia_inicio': self._parse_date(vigencia_inicio),
                        'vigencia_fim': self._parse_date(vigencia_fim),
                        'valor_global': self._parse_decimal(valor_global),
                        'raw_json': raw_json_data,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} registros de histórico')
        return count
    
    def _migrate_empenhos(self, conn, dry_run=False):
        """Migra tabela empenhos"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contrato_id, unidade_gestora, gestao, numero, data_emissao,
                   credor_cnpj, credor_nome, empenhado, liquidado, pago,
                   informacao_complementar, raw_json
            FROM empenhos
        """)
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            (id, contrato_id, unidade_gestora, gestao, numero, data_emissao,
             credor_cnpj, credor_nome, empenhado, liquidado, pago,
             informacao_complementar, raw_json) = row
            
            if not dry_run:
                try:
                    raw_json_data = json.loads(raw_json) if raw_json else None
                except (json.JSONDecodeError, TypeError):
                    raw_json_data = None
                
                Empenho.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'unidade_gestora': unidade_gestora,
                        'gestao': gestao,
                        'numero': numero,
                        'data_emissao': self._parse_date(data_emissao),
                        'credor_cnpj': credor_cnpj,
                        'credor_nome': credor_nome,
                        'empenhado': self._parse_decimal(empenhado),
                        'liquidado': self._parse_decimal(liquidado),
                        'pago': self._parse_decimal(pago),
                        'informacao_complementar': informacao_complementar,
                        'raw_json': raw_json_data,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} empenhos')
        return count
    
    def _migrate_itens(self, conn, dry_run=False):
        """Migra tabela itens"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contrato_id, tipo_id, tipo_material, grupo_id, catmatseritem_id,
                   descricao_complementar, quantidade, valorunitario, valortotal,
                   numero_item_compra, raw_json
            FROM itens
        """)
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            (id, contrato_id, tipo_id, tipo_material, grupo_id, catmatseritem_id,
             descricao_complementar, quantidade, valorunitario, valortotal,
             numero_item_compra, raw_json) = row
            
            if not dry_run:
                try:
                    raw_json_data = json.loads(raw_json) if raw_json else None
                except (json.JSONDecodeError, TypeError):
                    raw_json_data = None
                
                ItemContrato.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'tipo_id': tipo_id,
                        'tipo_material': tipo_material,
                        'grupo_id': grupo_id,
                        'catmatseritem_id': catmatseritem_id,
                        'descricao_complementar': descricao_complementar,
                        'quantidade': self._parse_decimal(quantidade),
                        'valorunitario': self._parse_decimal(valorunitario),
                        'valortotal': self._parse_decimal(valortotal),
                        'numero_item_compra': numero_item_compra,
                        'raw_json': raw_json_data,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} itens')
        return count
    
    def _migrate_arquivos(self, conn, dry_run=False):
        """Migra tabela arquivos"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, contrato_id, tipo, descricao, path_arquivo, origem, link_sei, raw_json
            FROM arquivos
        """)
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            id, contrato_id, tipo, descricao, path_arquivo, origem, link_sei, raw_json = row
            
            if not dry_run:
                try:
                    raw_json_data = json.loads(raw_json) if raw_json else None
                except (json.JSONDecodeError, TypeError):
                    raw_json_data = None
                
                ArquivoContrato.objects.update_or_create(
                    id=id,
                    defaults={
                        'contrato_id': str(contrato_id),
                        'tipo': tipo,
                        'descricao': descricao,
                        'path_arquivo': path_arquivo,
                        'origem': origem,
                        'link_sei': link_sei,
                        'raw_json': raw_json_data,
                    }
                )
            count += 1
        
        self.stdout.write(f'  Migrados {count} arquivos')
        return count
    
    @transaction.atomic
    def handle(self, *args, **options):
        db_path = Path(options['db_path'])
        dry_run = options['dry_run']
        
        if not db_path.exists():
            raise CommandError(f'Arquivo SQLite não encontrado: {db_path}')
        
        self.stdout.write(f'Conectando ao SQLite: {db_path}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhum dado será salvo'))
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        try:
            self.stdout.write('\nIniciando migração...\n')
            
            self._migrate_uasgs(conn, dry_run)
            self._migrate_contratos(conn, dry_run)
            self._migrate_status_contratos(conn, dry_run)
            self._migrate_registros_status(conn, dry_run)
            self._migrate_registro_mensagem(conn, dry_run)
            self._migrate_links_contratos(conn, dry_run)
            self._migrate_fiscalizacao(conn, dry_run)
            self._migrate_historico(conn, dry_run)
            self._migrate_empenhos(conn, dry_run)
            self._migrate_itens(conn, dry_run)
            self._migrate_arquivos(conn, dry_run)
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Migração concluída com sucesso!')
            )
        
        finally:
            conn.close()

