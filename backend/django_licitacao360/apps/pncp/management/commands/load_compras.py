"""
Management command para carregar compras do SQLite (pncp.db) para PostgreSQL
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from ...models import Compra


class Command(BaseCommand):
    help = 'Carrega compras do arquivo SQLite pncp.db para PostgreSQL'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--db-path',
            type=str,
            default=None,
            help='Caminho para o arquivo SQLite (padrão: apps/pncp/fixtures/pncp.db)',
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
        app_path = command_file.parent.parent.parent  # apps/pncp
        return app_path / 'fixtures' / 'pncp.db'
    
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
    
    def _parse_decimal(self, value, max_digits=None, decimal_places=None):
        """Converte valor numérico para Decimal com validação de limites"""
        if value is None or value == '':
            return None
        try:
            cleaned = str(value).replace(',', '.')
            decimal_value = Decimal(cleaned)
            
            if max_digits and decimal_places:
                integer_part_max = 10 ** (max_digits - decimal_places)
                max_value = Decimal(str(integer_part_max)) - Decimal('0.0001')
                min_value = -max_value
                
                quantize_str = '0.' + '0' * decimal_places
                decimal_value = decimal_value.quantize(Decimal(quantize_str))
                
                if decimal_value > max_value:
                    return max_value
                elif decimal_value < min_value:
                    return min_value
            
            return decimal_value
        except (InvalidOperation, ValueError, TypeError, OverflowError):
            return None
    
    def _truncate_field(self, value, max_length):
        """Trunca string para o tamanho máximo permitido"""
        if value is None or value == '':
            return ''
        value_str = str(value).strip()
        if len(value_str) > max_length:
            return value_str[:max_length]
        return value_str
    
    def _migrate_compras(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela compras"""
        self.stdout.write('Migrando compras...')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ano_compra, sequencial_compra, numero_compra, codigo_unidade,
                   objeto_compra, modalidade_nome, compra_id, numero_processo,
                   data_publicacao_pncp, data_atualizacao, valor_total_estimado,
                   valor_total_homologado, percentual_desconto
            FROM compras
        """)
        rows = cursor.fetchall()
        
        count = 0
        batch = []
        
        for row in rows:
            (ano_compra, sequencial_compra, numero_compra, codigo_unidade,
             objeto_compra, modalidade_nome, compra_id, numero_processo,
             data_publicacao_pncp, data_atualizacao, valor_total_estimado,
             valor_total_homologado, percentual_desconto) = row
            
            if not dry_run:
                batch.append({
                    'compra_id': self._truncate_field(compra_id, 100),
                    'ano_compra': int(ano_compra) if ano_compra else None,
                    'sequencial_compra': int(sequencial_compra) if sequencial_compra else None,
                    'numero_compra': self._truncate_field(numero_compra, 50),
                    'codigo_unidade': self._truncate_field(codigo_unidade, 50),
                    'objeto_compra': str(objeto_compra).strip() if objeto_compra else '',
                    'modalidade_nome': self._truncate_field(modalidade_nome, 100),
                    'numero_processo': self._truncate_field(numero_processo, 100),
                    'data_publicacao_pncp': self._parse_date(data_publicacao_pncp),
                    'data_atualizacao': self._parse_date(data_atualizacao),
                    'valor_total_estimado': self._parse_decimal(valor_total_estimado),
                    'valor_total_homologado': self._parse_decimal(valor_total_homologado),
                    'percentual_desconto': self._parse_decimal(percentual_desconto, max_digits=7, decimal_places=4),
                })
                
                if len(batch) >= batch_size:
                    self._bulk_create_compras(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1
        
        if batch and not dry_run:
            self._bulk_create_compras(batch)
            count += len(batch)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migradas {count} compras'))
        return count
    
    def _bulk_create_compras(self, batch):
        """Cria compras em lote usando update_or_create"""
        for item in batch:
            try:
                Compra.objects.update_or_create(
                    compra_id=item['compra_id'],
                    defaults=item
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar compra {item.get("compra_id", "N/A")}: {str(e)}')
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
                compras_count = self._migrate_compras(conn, dry_run, batch_size)
            else:
                with transaction.atomic():
                    compras_count = self._migrate_compras(conn, dry_run, batch_size)
            
            conn.close()
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ Validação concluída (DRY-RUN)!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Migração concluída com sucesso!'))
            self.stdout.write(f'  Compras: {compras_count}')
            
        except Exception as e:
            raise CommandError(f'Erro durante a migração: {str(e)}') from e
