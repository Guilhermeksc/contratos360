"""
Management command para carregar itens de compra do SQLite (pncp.db) para PostgreSQL
"""

import sqlite3
from pathlib import Path
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import Compra, ItemCompra


class Command(BaseCommand):
    help = 'Carrega itens de compra do arquivo SQLite pncp.db para PostgreSQL'
    
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
    
    def _parse_boolean(self, value):
        """Converte valor para boolean"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return str(value).lower() in ['true', '1', 'yes', 'sim', 's']
        return False
    
    def _truncate_field(self, value, max_length):
        """Trunca string para o tamanho máximo permitido"""
        if value is None or value == '':
            return ''
        value_str = str(value).strip()
        if len(value_str) > max_length:
            return value_str[:max_length]
        return value_str
    
    def _migrate_itens_compra(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela itens_compra"""
        self.stdout.write('Migrando itens de compra...')
        cursor = conn.cursor()
        # Faz JOIN para garantir que a compra existe e pegar o compra_id correto
        cursor.execute("""
            SELECT i.item_id, c.compra_id, i.numero_item,
                   i.descricao, i.unidade_medida, i.valor_unitario_estimado,
                   i.valor_total_estimado, i.quantidade, i.percentual_economia,
                   i.situacao_compra_item_nome, i.tem_resultado
            FROM itens_compra i
            INNER JOIN compras c ON i.ano_compra = c.ano_compra 
                                 AND i.sequencial_compra = c.sequencial_compra
        """)
        rows = cursor.fetchall()
        
        count = 0
        skipped = 0
        batch = []
        
        for row in rows:
            (item_id, compra_id, numero_item,
             descricao, unidade_medida, valor_unitario_estimado,
             valor_total_estimado, quantidade, percentual_economia,
             situacao_compra_item_nome, tem_resultado) = row
            
            if not dry_run:
                try:
                    compra = Compra.objects.get(compra_id=str(compra_id).strip())
                except Compra.DoesNotExist:
                    skipped += 1
                    continue
                
                batch.append({
                    'item_id': self._truncate_field(item_id, 100),
                    'compra': compra,
                    'numero_item': int(numero_item) if numero_item else None,
                    'descricao': str(descricao).strip() if descricao else '',
                    'unidade_medida': self._truncate_field(unidade_medida, 50),
                    'valor_unitario_estimado': self._parse_decimal(valor_unitario_estimado),
                    'valor_total_estimado': self._parse_decimal(valor_total_estimado),
                    'quantidade': self._parse_decimal(quantidade) or Decimal('0'),
                    'percentual_economia': self._parse_decimal(percentual_economia, max_digits=7, decimal_places=4),
                    'situacao_compra_item_nome': self._truncate_field(situacao_compra_item_nome, 100),
                    'tem_resultado': self._parse_boolean(tem_resultado),
                })
                
                if len(batch) >= batch_size:
                    self._bulk_create_itens_compra(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1
        
        if batch and not dry_run:
            self._bulk_create_itens_compra(batch)
            count += len(batch)
        
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Pulados {skipped} itens (compra não encontrada)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrados {count} itens de compra'))
        return count
    
    def _bulk_create_itens_compra(self, batch):
        """Cria itens de compra em lote usando update_or_create"""
        for item in batch:
            try:
                compra = item.pop('compra')
                ItemCompra.objects.update_or_create(
                    item_id=item['item_id'],
                    defaults={**item, 'compra': compra}
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar item {item.get("item_id", "N/A")}: {str(e)}')
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
                itens_count = self._migrate_itens_compra(conn, dry_run, batch_size)
            else:
                with transaction.atomic():
                    itens_count = self._migrate_itens_compra(conn, dry_run, batch_size)
            
            conn.close()
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ Validação concluída (DRY-RUN)!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Migração concluída com sucesso!'))
            self.stdout.write(f'  Itens de Compra: {itens_count}')
            
        except Exception as e:
            raise CommandError(f'Erro durante a migração: {str(e)}') from e
