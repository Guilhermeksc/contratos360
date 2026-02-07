"""
Management command para carregar fornecedores do SQLite (pncp.db) para PostgreSQL
"""

import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import Fornecedor


class Command(BaseCommand):
    help = 'Carrega fornecedores do arquivo SQLite pncp.db para PostgreSQL'
    
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
    
    def _truncate_field(self, value, max_length):
        """Trunca string para o tamanho máximo permitido"""
        if value is None or value == '':
            return ''
        value_str = str(value).strip()
        if len(value_str) > max_length:
            return value_str[:max_length]
        return value_str
    
    def _get_db_path(self, db_path_option):
        """Obtém o caminho do arquivo SQLite"""
        if db_path_option:
            return Path(db_path_option)
        
        # Caminho padrão relativo ao arquivo do comando
        command_file = Path(__file__)
        app_path = command_file.parent.parent.parent  # apps/pncp
        return app_path / 'fixtures' / 'pncp.db'
    
    def _migrate_fornecedores(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela fornecedores"""
        self.stdout.write('Migrando fornecedores...')
        cursor = conn.cursor()
        cursor.execute("SELECT cnpj_fornecedor, razao_social FROM fornecedores")
        rows = cursor.fetchall()
        
        count = 0
        batch = []
        
        for row in rows:
            cnpj_fornecedor, razao_social = row
            
            if not dry_run:
                # Limpa e trunca CNPJ (max_length=20)
                cnpj_cleaned = self._truncate_field(cnpj_fornecedor, 20)
                # Limpa e trunca razão social (max_length=255)
                razao_cleaned = self._truncate_field(razao_social, 255)
                
                batch.append({
                    'cnpj_fornecedor': cnpj_cleaned,
                    'razao_social': razao_cleaned,
                })
                
                if len(batch) >= batch_size:
                    self._bulk_create_fornecedores(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1
        
        if batch and not dry_run:
            self._bulk_create_fornecedores(batch)
            count += len(batch)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrados {count} fornecedores'))
        return count
    
    def _bulk_create_fornecedores(self, batch):
        """Cria fornecedores em lote usando update_or_create"""
        for item in batch:
            try:
                Fornecedor.objects.update_or_create(
                    cnpj_fornecedor=item['cnpj_fornecedor'],
                    defaults={'razao_social': item['razao_social']}
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar fornecedor {item["cnpj_fornecedor"]}: {str(e)}')
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
                fornecedores_count = self._migrate_fornecedores(conn, dry_run, batch_size)
            else:
                with transaction.atomic():
                    fornecedores_count = self._migrate_fornecedores(conn, dry_run, batch_size)
            
            conn.close()
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ Validação concluída (DRY-RUN)!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Migração concluída com sucesso!'))
            self.stdout.write(f'  Fornecedores: {fornecedores_count}')
            
        except Exception as e:
            raise CommandError(f'Erro durante a migração: {str(e)}') from e
