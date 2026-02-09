from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...services.inlabs_downloader import ingest_inlabs_articles, InlabsDownloadError


class Command(BaseCommand):
    help = "Baixa e salva artigos do INLABS para uma data específica ou a data atual."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            dest="edition_date",
            help="Data (YYYY-MM-DD) da edição do INLABS a importar. Usa a data atual se omitido.",
        )

    def handle(self, *args, **options):
        date_str = options.get("edition_date")
        if date_str:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError as exc:
                raise CommandError("Informe a data no formato YYYY-MM-DD.") from exc
        else:
            target_date = timezone.localdate()

        self.stdout.write(self.style.NOTICE(f"Iniciando importação do INLABS para {target_date}..."))

        try:
            result = ingest_inlabs_articles(target_date)
        except InlabsDownloadError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Importação concluída:\n"
                f"  Arquivo: {result['downloaded_file']}\n"
                f"  Artigos: {result['saved_articles']}\n"
                f"  Avisos de Licitação: {result.get('saved_avisos', 0)}\n"
                f"  Credenciamentos: {result.get('saved_credenciamentos', 0)}"
            )
        )
