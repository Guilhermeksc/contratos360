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

from ...models import AmparoLegal, Compra, Modalidade, ModoDisputa


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
    
    def _get_modalidade_by_name(self, nome):
        """Busca modalidade por nome"""
        if not nome:
            return None
        try:
            return Modalidade.objects.get(nome=nome.strip())
        except Modalidade.DoesNotExist:
            return None
        except Modalidade.MultipleObjectsReturned:
            return Modalidade.objects.filter(nome=nome.strip()).first()
    
    def _get_amparo_legal_by_codigo(self, codigo):
        """Busca amparo legal por código"""
        if not codigo:
            return None
        try:
            return AmparoLegal.objects.get(id=int(codigo))
        except (AmparoLegal.DoesNotExist, ValueError, TypeError):
            return None
    
    def _get_modo_disputa_by_id(self, modo_id):
        """Busca modo de disputa por ID"""
        if not modo_id:
            return None
        try:
            return ModoDisputa.objects.get(id=int(modo_id))
        except (ModoDisputa.DoesNotExist, ValueError, TypeError):
            return None
    
    def _migrate_compras(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela compras"""
        self.stdout.write('Migrando compras...')
        cursor = conn.cursor()
        
        # Verifica quais colunas existem na tabela SQLite
        cursor.execute("PRAGMA table_info(compras)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Monta query baseada nas colunas disponíveis
        select_fields = [
            'ano_compra', 'sequencial_compra', 'numero_compra', 'codigo_unidade',
            'objeto_compra', 'compra_id', 'numero_processo',
            'data_publicacao_pncp', 'data_atualizacao', 'valor_total_estimado',
            'valor_total_homologado', 'percentual_desconto'
        ]
        
        # Adiciona campos opcionais se existirem
        optional_fields = ['modalidade_nome', 'modalidade_id', 'amparo_legal_id', 'modo_disputa_id']
        
        available_fields = []
        for field in select_fields:
            if field in column_names:
                available_fields.append(field)
        
        for field in optional_fields:
            if field in column_names:
                available_fields.append(field)
        
        query = f"SELECT {', '.join(available_fields)} FROM compras"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        count = 0
        skipped = 0
        batch = []
        
        for row in rows:
            row_dict = dict(zip(available_fields, row))
            
            # Extrai valores
            ano_compra = row_dict.get('ano_compra')
            sequencial_compra = row_dict.get('sequencial_compra')
            numero_compra = row_dict.get('numero_compra')
            codigo_unidade = row_dict.get('codigo_unidade')
            objeto_compra = row_dict.get('objeto_compra')
            compra_id = row_dict.get('compra_id')
            numero_processo = row_dict.get('numero_processo')
            data_publicacao_pncp = row_dict.get('data_publicacao_pncp')
            data_atualizacao = row_dict.get('data_atualizacao')
            valor_total_estimado = row_dict.get('valor_total_estimado')
            valor_total_homologado = row_dict.get('valor_total_homologado')
            percentual_desconto = row_dict.get('percentual_desconto')
            
            # Busca relacionamentos
            modalidade = None
            if 'modalidade_id' in row_dict and row_dict.get('modalidade_id'):
                try:
                    modalidade = Modalidade.objects.get(id=int(row_dict['modalidade_id']))
                except (Modalidade.DoesNotExist, ValueError, TypeError):
                    pass
            elif 'modalidade_nome' in row_dict and row_dict.get('modalidade_nome'):
                modalidade = self._get_modalidade_by_name(row_dict['modalidade_nome'])
            
            amparo_legal = None
            if 'amparo_legal_id' in row_dict and row_dict.get('amparo_legal_id'):
                amparo_legal = self._get_amparo_legal_by_codigo(row_dict['amparo_legal_id'])
            
            modo_disputa = None
            if 'modo_disputa_id' in row_dict and row_dict.get('modo_disputa_id'):
                modo_disputa = self._get_modo_disputa_by_id(row_dict['modo_disputa_id'])
            
            if not dry_run:
                if not compra_id:
                    skipped += 1
                    continue
                
                batch.append({
                    'compra_id': self._truncate_field(compra_id, 100),
                    'ano_compra': int(ano_compra) if ano_compra else None,
                    'sequencial_compra': int(sequencial_compra) if sequencial_compra else None,
                    'numero_compra': self._truncate_field(numero_compra, 50),
                    'codigo_unidade': self._truncate_field(codigo_unidade, 50),
                    'objeto_compra': str(objeto_compra).strip() if objeto_compra else '',
                    'modalidade': modalidade,
                    'amparo_legal': amparo_legal,
                    'modo_disputa': modo_disputa,
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
        
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Puladas {skipped} compras (sem compra_id)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migradas {count} compras'))
        return count
    
    def _bulk_create_compras(self, batch):
        """Cria compras em lote usando update_or_create"""
        for item in batch:
            try:
                compra_id = item.pop('compra_id')
                Compra.objects.update_or_create(
                    compra_id=compra_id,
                    defaults=item
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar compra {compra_id}: {str(e)}')
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
