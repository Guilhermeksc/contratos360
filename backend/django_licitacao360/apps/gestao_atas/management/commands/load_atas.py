"""
Management command para carregar atas do SQLite (atas.db) para PostgreSQL
"""

import sqlite3
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from ...models import Ata


class Command(BaseCommand):
    help = 'Carrega atas do arquivo SQLite atas.db para PostgreSQL'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--db-path',
            type=str,
            default=None,
            help='Caminho para o arquivo SQLite (padrão: apps/gestao_atas/fixtures/atas.db)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar no banco (apenas valida)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Tamanho do lote para inserção em batch (padrão: 1000)',
        )
    
    def _get_db_path(self, db_path_option):
        """Obtém o caminho do arquivo SQLite"""
        if db_path_option:
            return Path(db_path_option)
        
        # Caminho padrão relativo ao arquivo do comando
        command_file = Path(__file__)
        app_path = command_file.parent.parent.parent  # apps/gestao_atas
        return app_path / 'fixtures' / 'atas.db'
    
    def _parse_date(self, date_str):
        """Converte string de data para datetime timezone-aware"""
        if not date_str:
            return None
        dt = None
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            except (ValueError, TypeError):
                try:
                    dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
                except (ValueError, TypeError):
                    try:
                        dt = datetime.strptime(date_str, '%d/%m/%Y')
                    except (ValueError, TypeError):
                        return None
        
        if dt:
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        return None
    
    def _parse_integer(self, value):
        """Converte valor para inteiro"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _truncate_field(self, value, max_length):
        """Trunca string para o tamanho máximo permitido"""
        if value is None or value == '':
            return ''
        value_str = str(value).strip()
        if len(value_str) > max_length:
            return value_str[:max_length]
        return value_str
    
    def _migrate_atas(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela ata"""
        self.stdout.write('Migrando atas...')
        cursor = conn.cursor()
        
        # Verifica quais colunas existem na tabela SQLite
        cursor.execute("PRAGMA table_info(ata)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Monta query baseada nas colunas disponíveis
        select_fields = [
            'numeroControlePNCPAta',
            'numeroAtaRegistroPreco',
            'anoAta',
            'numeroControlePNCPCompra',
            'cancelado',
            'dataCancelamento',
            'dataAssinatura',
            'vigenciaInicio',
            'vigenciaFim',
            'dataPublicacaoPncp',
            'dataInclusao',
            'dataAtualizacao',
            'dataAtualizacaoGlobal',
            'usuario',
            'objetoContratacao',
            'cnpjOrgao',
            'nomeOrgao',
            'cnpjOrgaoSubrogado',
            'nomeOrgaoSubrogado',
            'codigoUnidadeOrgao',
            'nomeUnidadeOrgao',
            'codigoUnidadeOrgaoSubrogado',
            'nomeUnidadeOrgaoSubrogado',
            'sequencial',
            'ano',
            'numero_compra',
        ]
        
        # Filtra apenas campos que existem na tabela
        available_fields = [field for field in select_fields if field in column_names]
        
        query = f"SELECT {', '.join(available_fields)} FROM ata"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        count = 0
        skipped = 0
        batch = []
        
        for row in rows:
            row_dict = dict(zip(available_fields, row))
            
            # Extrai valores
            numero_controle_pncp_ata = row_dict.get('numeroControlePNCPAta')
            
            if not numero_controle_pncp_ata:
                skipped += 1
                continue
            
            if not dry_run:
                batch.append({
                    'numero_controle_pncp_ata': self._truncate_field(numero_controle_pncp_ata, 100),
                    'numero_ata_registro_preco': self._truncate_field(row_dict.get('numeroAtaRegistroPreco'), 100),
                    'ano_ata': self._parse_integer(row_dict.get('anoAta')),
                    'numero_controle_pncp_compra': self._truncate_field(row_dict.get('numeroControlePNCPCompra'), 100),
                    'cancelado': self._parse_integer(row_dict.get('cancelado')) or 0,
                    'data_cancelamento': self._parse_date(row_dict.get('dataCancelamento')),
                    'data_assinatura': self._parse_date(row_dict.get('dataAssinatura')),
                    'vigencia_inicio': self._parse_date(row_dict.get('vigenciaInicio')),
                    'vigencia_fim': self._parse_date(row_dict.get('vigenciaFim')),
                    'data_publicacao_pncp': self._parse_date(row_dict.get('dataPublicacaoPncp')),
                    'data_inclusao': self._parse_date(row_dict.get('dataInclusao')),
                    'data_atualizacao': self._parse_date(row_dict.get('dataAtualizacao')),
                    'data_atualizacao_global': self._parse_date(row_dict.get('dataAtualizacaoGlobal')),
                    'usuario': self._truncate_field(row_dict.get('usuario'), 255),
                    'objeto_contratacao': str(row_dict.get('objetoContratacao', '')).strip(),
                    'cnpj_orgao': self._truncate_field(row_dict.get('cnpjOrgao'), 20),
                    'nome_orgao': self._truncate_field(row_dict.get('nomeOrgao'), 255),
                    'cnpj_orgao_subrogado': self._truncate_field(row_dict.get('cnpjOrgaoSubrogado'), 20) if row_dict.get('cnpjOrgaoSubrogado') else None,
                    'nome_orgao_subrogado': self._truncate_field(row_dict.get('nomeOrgaoSubrogado'), 255) if row_dict.get('nomeOrgaoSubrogado') else None,
                    'codigo_unidade_orgao': self._truncate_field(row_dict.get('codigoUnidadeOrgao'), 50),
                    'nome_unidade_orgao': self._truncate_field(row_dict.get('nomeUnidadeOrgao'), 255),
                    'codigo_unidade_orgao_subrogado': self._truncate_field(row_dict.get('codigoUnidadeOrgaoSubrogado'), 50) if row_dict.get('codigoUnidadeOrgaoSubrogado') else None,
                    'nome_unidade_orgao_subrogado': self._truncate_field(row_dict.get('nomeUnidadeOrgaoSubrogado'), 255) if row_dict.get('nomeUnidadeOrgaoSubrogado') else None,
                    'sequencial': self._truncate_field(row_dict.get('sequencial'), 50),
                    'ano': self._parse_integer(row_dict.get('ano')),
                    'numero_compra': self._truncate_field(row_dict.get('numero_compra'), 100),
                })
                
                if len(batch) >= batch_size:
                    self._bulk_create_atas(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1
        
        if batch and not dry_run:
            self._bulk_create_atas(batch)
            count += len(batch)
        
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Puladas {skipped} atas (sem numeroControlePNCPAta)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migradas {count} atas'))
        return count
    
    def _bulk_create_atas(self, batch):
        """Cria atas em lote usando update_or_create"""
        for item in batch:
            try:
                numero_controle_pncp_ata = item.pop('numero_controle_pncp_ata')
                Ata.objects.update_or_create(
                    numero_controle_pncp_ata=numero_controle_pncp_ata,
                    defaults=item
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar ata {numero_controle_pncp_ata}: {str(e)}')
                )
                raise
    
    def handle(self, *args, **options):
        db_path = options.get('db_path')
        dry_run = options.get('dry_run', False)
        batch_size = options.get('batch_size', 1000)
        
        db_path = self._get_db_path(db_path)
        
        if not db_path.exists():
            raise CommandError(f'Arquivo SQLite não encontrado: {db_path}')
        
        self.stdout.write(self.style.NOTICE(f'Conectando ao SQLite: {db_path}'))
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            
            if dry_run:
                self.stdout.write(self.style.WARNING('⚠ Modo DRY-RUN: nenhum dado será salvo'))
                atas_count = self._migrate_atas(conn, dry_run, batch_size)
            else:
                with transaction.atomic():
                    atas_count = self._migrate_atas(conn, dry_run, batch_size)
            
            conn.close()
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ Validação concluída (DRY-RUN)!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Migração concluída com sucesso!'))
            self.stdout.write(f'  Atas: {atas_count}')
            
        except Exception as e:
            raise CommandError(f'Erro durante a migração: {str(e)}') from e
