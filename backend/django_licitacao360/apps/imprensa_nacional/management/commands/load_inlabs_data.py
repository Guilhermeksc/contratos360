"""
Management command para carregar dados do SQLite (inlabs_articles.db) para PostgreSQL
"""

import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import InlabsArticle, AvisoLicitacao, Credenciamento


class Command(BaseCommand):
    help = 'Carrega dados do arquivo SQLite inlabs_articles.db para PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--db-path',
            type=str,
            default=None,
            help='Caminho para o arquivo SQLite (padrão: apps/imprensa_nacional/fixtures/inlabs_articles.db)',
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
        parser.add_argument(
            '--table',
            type=str,
            choices=['all', 'articles', 'avisos', 'credenciamentos'],
            default='all',
            help='Tabela específica para carregar (padrão: all)',
        )

    def _get_db_path(self, db_path_option):
        """Obtém o caminho do arquivo SQLite"""
        if db_path_option:
            return Path(db_path_option)

        # Caminho padrão relativo ao arquivo do comando
        command_file = Path(__file__)
        app_path = command_file.parent.parent.parent  # apps/imprensa_nacional
        return app_path / 'fixtures' / 'inlabs_articles.db'

    def _truncate_field(self, value, max_length):
        """Trunca string para o tamanho máximo permitido"""
        if value is None or value == '':
            return None
        value_str = str(value).strip()
        if len(value_str) > max_length:
            return value_str[:max_length]
        return value_str

    def _normalize_pub_date(self, date_str):
        """
        Normaliza uma data para o formato YYYY-MM-DD.
        Aceita formatos: DD/MM/YYYY, YYYY-MM-DD, ou outros formatos comuns.
        """
        if not date_str or not isinstance(date_str, str):
            return None
        
        date_str = date_str.strip()
        
        # Se já está no formato YYYY-MM-DD, retorna como está
        if len(date_str) == 10 and date_str.count('-') == 2:
            try:
                from datetime import datetime
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                pass
        
        # Tenta formato DD/MM/YYYY
        if len(date_str) == 10 and date_str.count('/') == 2:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        # Tenta outros formatos comuns
        from datetime import datetime
        formats = [
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%Y.%m.%d",
            "%d.%m.%Y",
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Se não conseguir converter, retorna como está (pode ser inválida)
        self.stdout.write(self.style.WARNING(f"Não foi possível normalizar a data: {date_str}, usando como está"))
        return date_str

    def _migrate_articles(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela inlabs_articles"""
        self.stdout.write('Migrando artigos INLABS...')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM inlabs_articles")
        rows = cursor.fetchall()

        # Obtém nomes das colunas
        column_names = [description[0] for description in cursor.description]

        count = 0
        skipped = 0
        batch = []

        for row in rows:
            row_dict = dict(zip(column_names, row))

            # Extrai valores e aplica truncamento quando necessário
            article_id = self._truncate_field(row_dict.get('article_id'), 64)
            pub_date_raw = self._truncate_field(row_dict.get('pub_date'), 32)
            materia_id = self._truncate_field(row_dict.get('materia_id'), 64)

            if not article_id or not pub_date_raw:
                skipped += 1
                continue

            # Normaliza pub_date para formato YYYY-MM-DD
            pub_date = self._normalize_pub_date(pub_date_raw)

            if not dry_run:
                batch.append({
                    'article_id': article_id,
                    'name': self._truncate_field(row_dict.get('name'), 255),
                    'id_oficio': self._truncate_field(row_dict.get('id_oficio'), 100),
                    'pub_name': self._truncate_field(row_dict.get('pub_name'), 100),
                    'art_type': self._truncate_field(row_dict.get('art_type'), 100),
                    'pub_date': pub_date,
                    'nome_om': self._truncate_field(row_dict.get('nome_om'), 255),
                    'number_page': self._truncate_field(row_dict.get('number_page'), 255),
                    'pdf_page': self._truncate_field(row_dict.get('pdf_page'), 255),
                    'edition_number': self._truncate_field(row_dict.get('edition_number'), 32),
                    'highlight_type': self._truncate_field(row_dict.get('highlight_type'), 64),
                    'highlight_priority': self._truncate_field(row_dict.get('highlight_priority'), 64),
                    'highlight': row_dict.get('highlight'),
                    'highlight_image': self._truncate_field(row_dict.get('highlight_image'), 255),
                    'highlight_image_name': self._truncate_field(row_dict.get('highlight_image_name'), 255),
                    'materia_id': materia_id,
                    'body_identifica': row_dict.get('body_identifica'),
                    'uasg': self._truncate_field(row_dict.get('uasg'), 64),
                    'body_texto': row_dict.get('body_texto'),
                })

                if len(batch) >= batch_size:
                    self._bulk_create_articles(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1

        if batch and not dry_run:
            self._bulk_create_articles(batch)
            count += len(batch)

        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Pulados {skipped} artigos (sem article_id ou pub_date)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrados {count} artigos'))
        return count

    def _bulk_create_articles(self, batch):
        """Cria artigos em lote usando update_or_create"""
        for item in batch:
            try:
                article_id = item.pop('article_id')
                pub_date = item.pop('pub_date')
                materia_id = item.pop('materia_id')

                InlabsArticle.objects.update_or_create(
                    article_id=article_id,
                    pub_date=pub_date,
                    materia_id=materia_id,
                    defaults=item
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar artigo {article_id}: {str(e)}')
                )
                raise

    def _migrate_avisos(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela aviso_licitacao"""
        self.stdout.write('Migrando avisos de licitação...')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM aviso_licitacao")
        rows = cursor.fetchall()

        # Obtém nomes das colunas
        column_names = [description[0] for description in cursor.description]

        count = 0
        skipped = 0
        batch = []

        for row in rows:
            row_dict = dict(zip(column_names, row))

            article_id = self._truncate_field(row_dict.get('article_id'), 64)

            if not article_id:
                skipped += 1
                continue

            if not dry_run:
                batch.append({
                    'article_id': article_id,
                    'modalidade': self._truncate_field(row_dict.get('modalidade'), 255),
                    'numero': self._truncate_field(row_dict.get('numero'), 64),
                    'ano': self._truncate_field(row_dict.get('ano'), 4),
                    'uasg': self._truncate_field(row_dict.get('uasg'), 64),
                    'processo': self._truncate_field(row_dict.get('processo'), 255),
                    'objeto': row_dict.get('objeto'),
                    'itens_licitados': self._truncate_field(row_dict.get('itens_licitados'), 255),
                    'publicacao': self._truncate_field(row_dict.get('publicacao'), 255),
                    'entrega_propostas': self._truncate_field(row_dict.get('entrega_propostas'), 255),
                    'abertura_propostas': self._truncate_field(row_dict.get('abertura_propostas'), 255),
                    'nome_responsavel': self._truncate_field(row_dict.get('nome_responsavel'), 255),
                    'cargo': self._truncate_field(row_dict.get('cargo'), 255),
                })

                if len(batch) >= batch_size:
                    self._bulk_create_avisos(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1

        if batch and not dry_run:
            self._bulk_create_avisos(batch)
            count += len(batch)

        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Pulados {skipped} avisos (sem article_id)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrados {count} avisos de licitação'))
        return count

    def _bulk_create_avisos(self, batch):
        """Cria avisos em lote usando update_or_create"""
        for item in batch:
            try:
                article_id = item.pop('article_id')

                AvisoLicitacao.objects.update_or_create(
                    article_id=article_id,
                    defaults=item
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar aviso {article_id}: {str(e)}')
                )
                raise

    def _migrate_credenciamentos(self, conn, dry_run=False, batch_size=1000):
        """Migra tabela credenciamento"""
        self.stdout.write('Migrando credenciamentos...')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM credenciamento")
        rows = cursor.fetchall()

        # Obtém nomes das colunas
        column_names = [description[0] for description in cursor.description]

        count = 0
        skipped = 0
        batch = []

        for row in rows:
            row_dict = dict(zip(column_names, row))

            article_id = self._truncate_field(row_dict.get('article_id'), 64)

            if not article_id:
                skipped += 1
                continue

            if not dry_run:
                batch.append({
                    'article_id': article_id,
                    'tipo': self._truncate_field(row_dict.get('tipo'), 255),
                    'numero': self._truncate_field(row_dict.get('numero'), 64),
                    'ano': self._truncate_field(row_dict.get('ano'), 4),
                    'uasg': self._truncate_field(row_dict.get('uasg'), 64),
                    'processo': self._truncate_field(row_dict.get('processo'), 255),
                    'tipo_processo': self._truncate_field(row_dict.get('tipo_processo'), 255),
                    'numero_processo': self._truncate_field(row_dict.get('numero_processo'), 64),
                    'ano_processo': self._truncate_field(row_dict.get('ano_processo'), 4),
                    'contratante': self._truncate_field(row_dict.get('contratante'), 255),
                    'contratado': self._truncate_field(row_dict.get('contratado'), 255),
                    'objeto': row_dict.get('objeto'),
                    'fundamento_legal': row_dict.get('fundamento_legal'),
                    'vigencia': self._truncate_field(row_dict.get('vigencia'), 255),
                    'valor_total': self._truncate_field(row_dict.get('valor_total'), 255),
                    'data_assinatura': self._truncate_field(row_dict.get('data_assinatura'), 255),
                    'nome_responsavel': self._truncate_field(row_dict.get('nome_responsavel'), 255),
                    'cargo': self._truncate_field(row_dict.get('cargo'), 255),
                })

                if len(batch) >= batch_size:
                    self._bulk_create_credenciamentos(batch)
                    count += len(batch)
                    batch = []
            else:
                count += 1

        if batch and not dry_run:
            self._bulk_create_credenciamentos(batch)
            count += len(batch)

        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ Pulados {skipped} credenciamentos (sem article_id)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrados {count} credenciamentos'))
        return count

    def _bulk_create_credenciamentos(self, batch):
        """Cria credenciamentos em lote usando update_or_create"""
        for item in batch:
            try:
                article_id = item.pop('article_id')

                Credenciamento.objects.update_or_create(
                    article_id=article_id,
                    defaults=item
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar credenciamento {article_id}: {str(e)}')
                )
                raise

    def handle(self, *args, **options):
        db_path = options.get('db_path')
        dry_run = options.get('dry_run', False)
        batch_size = options.get('batch_size', 1000)
        table = options.get('table', 'all')

        db_path = self._get_db_path(db_path)

        if not db_path.exists():
            raise CommandError(f'Arquivo SQLite não encontrado: {db_path}')

        self.stdout.write(self.style.NOTICE(f'Conectando ao SQLite: {db_path}'))

        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row

            if dry_run:
                self.stdout.write(self.style.WARNING('⚠ Modo DRY-RUN: nenhum dado será salvo'))

            articles_count = 0
            avisos_count = 0
            credenciamentos_count = 0

            if not dry_run:
                with transaction.atomic():
                    if table in ('all', 'articles'):
                        articles_count = self._migrate_articles(conn, dry_run, batch_size)
                    if table in ('all', 'avisos'):
                        avisos_count = self._migrate_avisos(conn, dry_run, batch_size)
                    if table in ('all', 'credenciamentos'):
                        credenciamentos_count = self._migrate_credenciamentos(conn, dry_run, batch_size)
            else:
                if table in ('all', 'articles'):
                    articles_count = self._migrate_articles(conn, dry_run, batch_size)
                if table in ('all', 'avisos'):
                    avisos_count = self._migrate_avisos(conn, dry_run, batch_size)
                if table in ('all', 'credenciamentos'):
                    credenciamentos_count = self._migrate_credenciamentos(conn, dry_run, batch_size)

            conn.close()

            if dry_run:
                self.stdout.write(self.style.SUCCESS('\n✅ Validação concluída (DRY-RUN)!'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Migração concluída com sucesso!'))
            self.stdout.write(f'  Artigos: {articles_count}')
            self.stdout.write(f'  Avisos de Licitação: {avisos_count}')
            self.stdout.write(f'  Credenciamentos: {credenciamentos_count}')

        except Exception as e:
            raise CommandError(f'Erro durante a migração: {str(e)}') from e
