"""
Comando para normalizar todas as datas pub_date para o formato YYYY-MM-DD.
Converte datas de DD/MM/YYYY para YYYY-MM-DD.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django_licitacao360.apps.imprensa_nacional.models import InlabsArticle
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def normalize_date(date_str: str) -> str | None:
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
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            pass
    
    # Tenta formato DD/MM/YYYY
    if len(date_str) == 10 and date_str.count('/') == 2:
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    # Tenta outros formatos comuns
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
    
    logger.warning(f"Não foi possível normalizar a data: {date_str}")
    return None


class Command(BaseCommand):
    help = 'Normaliza todas as datas pub_date para o formato YYYY-MM-DD'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco de dados',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Tamanho do lote para processamento (padrão: 1000)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('Normalizando datas pub_date para YYYY-MM-DD'))
        self.stdout.write('=' * 80)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN - Nenhuma alteração será feita'))
        
        # Busca todos os artigos
        total_articles = InlabsArticle.objects.count()
        self.stdout.write(f'\nTotal de artigos no banco: {total_articles}')
        
        # Estatísticas
        converted_count = 0
        already_normalized = 0
        error_count = 0
        skipped_count = 0
        
        # Processa em lotes usando iterator para melhor performance
        from django.db import connection
        
        # Busca apenas artigos que precisam ser normalizados (não estão em formato YYYY-MM-DD)
        # Usa SQL direto para melhor performance com PostgreSQL
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM inlabs_articles 
                WHERE pub_date !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
            """)
            article_ids = [row[0] for row in cursor.fetchall()]
        
        total_to_process = len(article_ids)
        self.stdout.write(f'Artigos que precisam normalização: {total_to_process}')
        
        total_to_process = articles_query.count()
        self.stdout.write(f'Artigos que precisam normalização: {total_to_process}')
        
        if total_to_process == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ Todas as datas já estão normalizadas!'))
            return
        
        # Processa em lotes
        processed = 0
        batch_updates = []
        
        # Busca artigos em lotes pelos IDs
        for i in range(0, len(article_ids), batch_size):
            batch_ids = article_ids[i:i + batch_size]
            articles = InlabsArticle.objects.filter(id__in=batch_ids)
            
            for article in articles:
                original_date = article.pub_date
                
                # Normaliza a data
                normalized_date = normalize_date(original_date)
                
                if not normalized_date:
                    error_count += 1
                    if error_count <= 10:  # Limita logs de erro
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Erro ao normalizar data: {original_date} (ID: {article.id})')
                        )
                    continue
                
                if normalized_date != original_date:
                    converted_count += 1
                    batch_updates.append((article.id, normalized_date))
                    
                    # Processa em lotes de atualização
                    if len(batch_updates) >= batch_size and not dry_run:
                        self._bulk_update_dates(batch_updates, connection)
                        batch_updates = []
                else:
                    already_normalized += 1
                
                processed += 1
                if processed % 1000 == 0:
                    self.stdout.write(f'Processados {processed}/{total_to_process} artigos...')
        
        # Processa lote final
        if batch_updates and not dry_run:
            self._bulk_update_dates(batch_updates, connection)
        
        # Resumo final
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('RESUMO DA NORMALIZAÇÃO'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total de artigos processados: {processed}')
        self.stdout.write(f'  ✓ Já normalizados: {already_normalized}')
        self.stdout.write(f'  ✓ Convertidos: {converted_count}')
        self.stdout.write(f'  ⚠ Erros: {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY-RUN - Nenhuma alteração foi feita'))
            self.stdout.write('Execute sem --dry-run para aplicar as alterações')
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ Normalização concluída!'))
            self.stdout.write(f'   {converted_count} datas foram convertidas para YYYY-MM-DD')
    
    def _bulk_update_dates(self, batch_updates, connection):
        """Atualiza datas em lote usando SQL direto"""
        try:
            with connection.cursor() as cursor:
                # Usa executemany para melhor performance
                cursor.executemany(
                    "UPDATE inlabs_articles SET pub_date = %s WHERE id = %s",
                    [(normalized_date, article_id) for article_id, normalized_date in batch_updates]
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Erro ao atualizar lote: {str(e)}')
            )
