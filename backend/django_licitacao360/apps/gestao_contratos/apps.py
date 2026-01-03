from django.apps import AppConfig


class GestaoContratosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_licitacao360.apps.gestao_contratos"
    verbose_name = "Gestão de Contratos e UASG"

    def ready(self):
        from . import signals  # noqa: F401
