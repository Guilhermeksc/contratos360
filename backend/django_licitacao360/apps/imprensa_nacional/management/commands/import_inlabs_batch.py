from __future__ import annotations

import time
from datetime import date, timedelta
from typing import List

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...services.inlabs_downloader import ingest_inlabs_articles, InlabsDownloadError


class Command(BaseCommand):
    help = "Importa artigos do INLABS para um intervalo de datas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-date",
            dest="start_date",
            required=True,
            help="Data inicial (YYYY-MM-DD) do intervalo a importar.",
        )
        parser.add_argument(
            "--end-date",
            dest="end_date",
            help="Data final (YYYY-MM-DD) do intervalo. Se omitido, usa a data atual.",
        )
        parser.add_argument(
            "--dates",
            dest="dates",
            nargs="+",
            help="Lista específica de datas (YYYY-MM-DD) para importar. Sobrescreve start-date e end-date.",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Pula datas que já possuem artigos no banco de dados.",
        )
        parser.add_argument(
            "--delay",
            type=int,
            default=2,
            help="Delay em segundos entre cada importação (padrão: 2).",
        )
        parser.add_argument(
            "--continue-on-error",
            action="store_true",
            help="Continua importação mesmo quando ocorre erro em uma data.",
        )

    def handle(self, *args, **options):
        dates_to_import: List[date] = []

        # Se lista específica de datas foi fornecida
        if options.get("dates"):
            for date_str in options["dates"]:
                try:
                    dates_to_import.append(date.fromisoformat(date_str))
                except ValueError as exc:
                    raise CommandError(f"Data inválida: {date_str}. Use formato YYYY-MM-DD.") from exc
        else:
            # Gerar intervalo de datas
            try:
                start_date = date.fromisoformat(options["start_date"])
            except ValueError as exc:
                raise CommandError("start-date inválida. Use formato YYYY-MM-DD.") from exc

            if options.get("end_date"):
                try:
                    end_date = date.fromisoformat(options["end_date"])
                except ValueError as exc:
                    raise CommandError("end-date inválida. Use formato YYYY-MM-DD.") from exc
            else:
                end_date = timezone.localdate()

            if start_date > end_date:
                raise CommandError("start-date deve ser anterior ou igual a end-date.")

            # Gerar todas as datas no intervalo
            current_date = start_date
            while current_date <= end_date:
                dates_to_import.append(current_date)
                current_date += timedelta(days=1)

        if not dates_to_import:
            raise CommandError("Nenhuma data para importar.")

        # Filtrar datas existentes se solicitado
        if options.get("skip_existing"):
            from ...models import InlabsArticle

            existing_dates = set(
                InlabsArticle.objects.filter(edition_date__in=dates_to_import)
                .values_list("edition_date", flat=True)
                .distinct()
            )
            dates_to_import = [d for d in dates_to_import if d not in existing_dates]
            self.stdout.write(
                self.style.WARNING(f"Pulando {len(existing_dates)} datas que já possuem artigos.")
            )

        total_dates = len(dates_to_import)
        self.stdout.write(
            self.style.SUCCESS(f"Iniciando importação em lote: {total_dates} datas")
        )
        self.stdout.write(
            f"Intervalo: {min(dates_to_import)} até {max(dates_to_import)}"
        )

        # Estatísticas
        success_count = 0
        error_count = 0
        skipped_count = 0
        total_articles = 0
        errors: List[tuple[date, str]] = []

        delay = options.get("delay", 2)
        continue_on_error = options.get("continue_on_error", False)

        # Processar cada data
        for idx, target_date in enumerate(dates_to_import, 1):
            self.stdout.write(
                self.style.NOTICE(
                    f"\n[{idx}/{total_dates}] Processando {target_date.isoformat()}..."
                )
            )

            try:
                result = ingest_inlabs_articles(target_date)
                success_count += 1
                articles_count = result.get("saved_articles", 0)
                total_articles += articles_count
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {target_date}: {articles_count} artigos salvos"
                    )
                )
            except InlabsDownloadError as exc:
                error_msg = str(exc)
                error_count += 1
                errors.append((target_date, error_msg))

                if "Nenhum arquivo disponível" in error_msg or "HTTP 404" in error_msg:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {target_date}: Arquivo não disponível (pulando)")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {target_date}: {error_msg}")
                    )

                if not continue_on_error:
                    raise CommandError(f"Erro ao importar {target_date}: {error_msg}") from exc
            except Exception as exc:
                error_msg = f"Erro inesperado: {exc}"
                error_count += 1
                errors.append((target_date, error_msg))
                self.stdout.write(self.style.ERROR(f"❌ {target_date}: {error_msg}"))

                if not continue_on_error:
                    raise CommandError(f"Erro ao importar {target_date}: {error_msg}") from exc

            # Delay entre importações (exceto na última)
            if idx < total_dates and delay > 0:
                time.sleep(delay)

        # Resumo final
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("RESUMO DA IMPORTAÇÃO EM LOTE"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total de datas processadas: {total_dates}")
        self.stdout.write(self.style.SUCCESS(f"✅ Sucessos: {success_count}"))
        self.stdout.write(self.style.WARNING(f"⚠️  Puladas (arquivo não disponível): {skipped_count}"))
        self.stdout.write(self.style.ERROR(f"❌ Erros: {error_count}"))
        self.stdout.write(f"📊 Total de artigos salvos: {total_articles}")

        if errors:
            self.stdout.write("\n" + self.style.ERROR("ERROS ENCONTRADOS:"))
            for error_date, error_msg in errors:
                self.stdout.write(f"  - {error_date}: {error_msg}")

        if error_count > 0 and not continue_on_error:
            raise CommandError(f"Importação concluída com {error_count} erro(s).")
