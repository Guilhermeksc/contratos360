"""
Management command para carregar resultados de itens do SQLite (pncp.db) para PostgreSQL
"""

import sqlite3
from pathlib import Path
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import Fornecedor, ItemCompra, ResultadoItem


class Command(BaseCommand):
    help = 'Carrega resultados de itens do arquivo SQLite pncp.db para PostgreSQL'
    
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
    
    def _parse_decimal(self, value):
        """Converte valor numérico para Decimal"""
        if value is None or value == '':
            return None
        try:
            cleaned = str(value).replace(',', '.')
            return Decimal(cleaned)
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
    
    def _migrate_resultados_item(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela resultados_item"""
        self.stdout.write('Migrando resultados de itens...')
        cursor = conn.cursor()
        # Faz JOIN para garantir que o item existe e pegar o item_id correto
        cursor.execute("""
            SELECT r.resultado_id, i.item_id, r.cnpj_fornecedor,
                   r.valor_total_homologado, r.quantidade_homologada,
                   r.valor_unitario_homologado, r.status, r.marca, r.modelo
            FROM resultados_item r
            INNER JOIN itens_compra i ON r.ano_compra = i.ano_compra 
                                      AND r.sequencial_compra = i.sequencial_compra
                                      AND r.numero_item = i.numero_item
        """)
        rows = cursor.fetchall()
        
        count = 0
        skipped = 0
        batch = []
        
        for row in rows:
            (resultado_id, item_id, cnpj_fornecedor,
             valor_total_homologado, quantidade_homologada,
             valor_unitario_homologado, status, marca, modelo) = row
            
            if not dry_run:
                # Busca o item de compra relacionado
                try:
                    item_compra = ItemCompra.objects.get(item_id=str(item_id).strip())
                except ItemCompra.DoesNotExist:
                    skipped += 1
                    continue
                
                # Busca o fornecedor
                try:
                    fornecedor = Fornecedor.objects.get(cnpj_fornecedor=str(cnpj_fornecedor).strip())
                except Fornecedor.DoesNotExist:
                    skipped += 1
                    continue
                
                batch.append({
                    'resultado_id': self._truncate_field(resultado_id, 100),
                    'item_compra': item_compra,
                    'fornecedor': fornecedor,
                    'valor_total_homologado': self._parse_decimal(valor_total_homologado) or Decimal('0'),
                    'quantidade_homologada': int(quantidade_homologada) if quantidade_homologada else 0,
                    'valor_unitario_homologado': self._parse_decimal(valor_unitario_homologado) or Decimal('0'),
                    'status': self._truncate_field(status, 100),
                    'marca': self._truncate_field(marca, 100) if marca else None,
                    'modelo': self._truncate_field(modelo, 100) if modelo else None,
                })
                
                if len(batch) >= batch_size:
                    self._bulk_create_resultados_item(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1
        
        if batch and not dry_run:
            self._bulk_create_resultados_item(batch)
            count += len(batch)
        
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Pulados {skipped} resultados (item ou fornecedor não encontrado)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrados {count} resultados de itens'))
        return count
    
    def _bulk_create_resultados_item(self, batch):
        """Cria resultados de item em lote usando update_or_create"""
        for item in batch:
            try:
                item_compra = item.pop('item_compra')
                fornecedor = item.pop('fornecedor')
                ResultadoItem.objects.update_or_create(
                    resultado_id=item['resultado_id'],
                    defaults={**item, 'item_compra': item_compra, 'fornecedor': fornecedor}
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar resultado {item.get("resultado_id", "N/A")}: {str(e)}')
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
                resultados_count = self._migrate_resultados_item(conn, dry_run, batch_size)
            else:
                with transaction.atomic():
                    resultados_count = self._migrate_resultados_item(conn, dry_run, batch_size)
            
            conn.close()
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ Validação concluída (DRY-RUN)!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Migração concluída com sucesso!'))
            self.stdout.write(f'  Resultados de Itens: {resultados_count}')
            
        except Exception as e:
            raise CommandError(f'Erro durante a migração: {str(e)}') from e
