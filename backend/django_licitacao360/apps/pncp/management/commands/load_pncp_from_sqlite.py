"""
Management command para carregar dados do SQLite (pncp.db) para PostgreSQL
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from ...models import Fornecedor, Compra, ItemCompra, ResultadoItem


class Command(BaseCommand):
    help = 'Carrega dados do arquivo SQLite pncp.db para PostgreSQL'
    
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
    
    def _parse_date(self, date_str):
        """Converte string de data para datetime timezone-aware"""
        if not date_str:
            return None
        dt = None
        try:
            # Tenta formato ISO
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
            # Converte para timezone-aware se ainda não for
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
            
            # Valida limites se especificados
            if max_digits and decimal_places:
                # Calcula o valor máximo permitido
                # Para max_digits=7, decimal_places=4: máximo é 999.9999 (menor que 10^3)
                # Fórmula: 10^(max_digits - decimal_places) - 10^(-decimal_places)
                integer_part_max = 10 ** (max_digits - decimal_places)
                max_value = Decimal(str(integer_part_max)) - Decimal('0.0001')
                min_value = -max_value
                
                # Arredonda para o número de casas decimais permitidas
                quantize_str = '0.' + '0' * decimal_places
                decimal_value = decimal_value.quantize(Decimal(quantize_str))
                
                # Limita ao valor máximo/minimo permitido
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
                    'compra_id': self._truncate_field(compra_id, 100),  # max_length=100
                    'ano_compra': int(ano_compra) if ano_compra else None,
                    'sequencial_compra': int(sequencial_compra) if sequencial_compra else None,
                    'numero_compra': self._truncate_field(numero_compra, 50),  # max_length=50
                    'codigo_unidade': self._truncate_field(codigo_unidade, 50),  # max_length=50
                    'objeto_compra': str(objeto_compra).strip() if objeto_compra else '',  # TextField, sem limite
                    'modalidade_nome': self._truncate_field(modalidade_nome, 100),  # max_length=100
                    'numero_processo': self._truncate_field(numero_processo, 100),  # max_length=100
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
                    'item_id': self._truncate_field(item_id, 100),  # max_length=100
                    'compra': compra,
                    'numero_item': int(numero_item) if numero_item else None,
                    'descricao': str(descricao).strip() if descricao else '',  # TextField, sem limite
                    'unidade_medida': self._truncate_field(unidade_medida, 50),  # max_length=50
                    'valor_unitario_estimado': self._parse_decimal(valor_unitario_estimado),
                    'valor_total_estimado': self._parse_decimal(valor_total_estimado),
                    'quantidade': self._parse_decimal(quantidade) or Decimal('0'),
                    'percentual_economia': self._parse_decimal(percentual_economia, max_digits=7, decimal_places=4),
                    'situacao_compra_item_nome': self._truncate_field(situacao_compra_item_nome, 100),  # max_length=100
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
                    'resultado_id': self._truncate_field(resultado_id, 100),  # max_length=100
                    'item_compra': item_compra,
                    'fornecedor': fornecedor,
                    'valor_total_homologado': self._parse_decimal(valor_total_homologado) or Decimal('0'),
                    'quantidade_homologada': int(quantidade_homologada) if quantidade_homologada else 0,
                    'valor_unitario_homologado': self._parse_decimal(valor_unitario_homologado) or Decimal('0'),
                    'status': self._truncate_field(status, 100),  # max_length=100
                    'marca': self._truncate_field(marca, 100) if marca else None,  # max_length=100
                    'modelo': self._truncate_field(modelo, 100) if modelo else None,  # max_length=100
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
        
        # Define caminho padrão se não fornecido
        if not db_path:
            # Caminho relativo ao arquivo do comando
            # Funciona tanto no host quanto no Docker (volume montado)
            # __file__ está em: apps/pncp/management/commands/load_pncp_from_sqlite.py
            # Precisamos ir para: apps/pncp/fixtures/pncp.db
            command_file = Path(__file__)
            # parent = commands/, parent.parent = management/, parent.parent.parent = pncp/
            app_path = command_file.parent.parent.parent  # apps/pncp
            db_path = app_path / 'fixtures' / 'pncp.db'
        else:
            db_path = Path(db_path)
        
        if not db_path.exists():
            raise CommandError(f'Arquivo SQLite não encontrado: {db_path}')
        
        self.stdout.write(self.style.NOTICE(f'Conectando ao SQLite: {db_path}'))
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            
            if dry_run:
                self.stdout.write(self.style.WARNING('⚠ Modo DRY-RUN: nenhum dado será salvo'))
            
            if dry_run:
                # No dry-run, apenas conta sem salvar
                fornecedores_count = self._migrate_fornecedores(conn, dry_run, batch_size)
                compras_count = self._migrate_compras(conn, dry_run, batch_size)
                itens_count = self._migrate_itens_compra(conn, dry_run, batch_size)
                resultados_count = self._migrate_resultados_item(conn, dry_run, batch_size)
            else:
                # Em modo normal, usa transação atômica
                with transaction.atomic():
                    fornecedores_count = self._migrate_fornecedores(conn, dry_run, batch_size)
                    compras_count = self._migrate_compras(conn, dry_run, batch_size)
                    itens_count = self._migrate_itens_compra(conn, dry_run, batch_size)
                    resultados_count = self._migrate_resultados_item(conn, dry_run, batch_size)
            
            conn.close()
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ Validação concluída (DRY-RUN)!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Migração concluída com sucesso!'))
            self.stdout.write(f'  Fornecedores: {fornecedores_count}')
            self.stdout.write(f'  Compras: {compras_count}')
            self.stdout.write(f'  Itens de Compra: {itens_count}')
            self.stdout.write(f'  Resultados de Itens: {resultados_count}')
            
        except Exception as e:
            raise CommandError(f'Erro durante a migração: {str(e)}') from e


"""
# Migração normal (usa caminho padrão)
docker compose exec backend python manage.py load_pncp_from_sqlite

# Com caminho customizado
docker compose exec backend python manage.py load_pncp_from_sqlite --db-path /home/guilherme/Projetos/pv/projeto_pric-OBT/backend/django_licitacao360/apps/pncp/fixtures/pncp.db

# Validação sem salvar (dry-run)
docker compose exec backend python manage.py load_pncp_from_sqlite --dry-run
# Com tamanho de lote customizado
docker compose exec backend python manage.py load_pncp_from_sqlite --batch-size 500

"""