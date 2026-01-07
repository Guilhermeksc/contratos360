from __future__ import annotations

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.conf import settings


class Command(BaseCommand):
    help = "Sincroniza tarefas periódicas do CELERY_BEAT_SCHEDULE para o banco de dados."

    def handle(self, *args, **options):
        if not hasattr(settings, "CELERY_BEAT_SCHEDULE"):
            self.stdout.write(self.style.WARNING("CELERY_BEAT_SCHEDULE não encontrado no settings."))
            return

        schedule = getattr(settings, "CELERY_BEAT_SCHEDULE", {})
        created_count = 0
        updated_count = 0
        disabled_count = 0

        # Obter nomes das tarefas que devem estar ativas
        active_task_names = set(schedule.keys())

        # Desabilitar tarefas que não estão mais no schedule (apenas para tarefas INLABS)
        inlabs_tasks = PeriodicTask.objects.filter(
            name__startswith="coletar_inlabs"
        ).exclude(name__in=active_task_names)
        
        for old_task in inlabs_tasks:
            old_task.enabled = False
            old_task.save()
            disabled_count += 1
            self.stdout.write(
                self.style.WARNING(f"⚠️  Tarefa desabilitada: {old_task.name}")
            )

        for task_name, task_config in schedule.items():
            task_path = task_config["task"]
            crontab_config = task_config["schedule"]

            # Extrair valores do crontab (podem ser None, "*", ou valores específicos)
            # O django_celery_beat espera strings no formato crontab
            def get_crontab_value(value):
                if value is None:
                    return "*"
                if isinstance(value, (list, tuple, set)):
                    # Se for uma lista/tuple/set com um único valor, retorna o valor como string
                    if len(value) == 1:
                        return str(list(value)[0])
                    # Se for múltiplos valores, retorna como string separada por vírgula
                    return ",".join(str(v) for v in sorted(value))
                # Se já for string, retorna como está
                if isinstance(value, str):
                    return value
                # Caso contrário, converte para string
                return str(value)

            minute = get_crontab_value(getattr(crontab_config, "minute", None))
            hour = get_crontab_value(getattr(crontab_config, "hour", None))
            day_of_week = get_crontab_value(getattr(crontab_config, "day_of_week", None))
            day_of_month = get_crontab_value(getattr(crontab_config, "day_of_month", None))
            month_of_year = get_crontab_value(getattr(crontab_config, "month_of_year", None))

            # Garantir que valores não especificados sejam "*"
            day_of_week = day_of_week if day_of_week != "*" or day_of_week is not None else "*"
            day_of_month = day_of_month if day_of_month != "*" or day_of_month is not None else "*"
            month_of_year = month_of_year if month_of_year != "*" or month_of_year is not None else "*"
            
            # Criar ou obter o CrontabSchedule
            crontab_schedule, created = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                timezone=settings.CELERY_TIMEZONE,
            )
            
            # Se já existia, atualizar para garantir que está correto
            if not created:
                crontab_schedule.day_of_week = day_of_week if day_of_week else "*"
                crontab_schedule.day_of_month = day_of_month if day_of_month else "*"
                crontab_schedule.month_of_year = month_of_year if month_of_year else "*"
                crontab_schedule.save()

            # Criar ou atualizar a PeriodicTask
            task, created = PeriodicTask.objects.update_or_create(
                name=task_name,
                defaults={
                    "task": task_path,
                    "crontab": crontab_schedule,
                    "enabled": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Tarefa criada: {task_name} ({task_path})")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"🔄 Tarefa atualizada: {task_name} ({task_path})")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Sincronização concluída: {created_count} criadas, {updated_count} atualizadas, {disabled_count} desabilitadas"
            )
        )

