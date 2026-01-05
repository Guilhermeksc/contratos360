from django.apps import AppConfig


class AgentesResponsaveisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_licitacao360.apps.agentes_responsaveis"
    verbose_name = "Cadastro de Agentes Responsáveis"

    def ready(self) -> None:
        # Importa sinais para carga automática de fixtures
        from . import signals  # noqa: F401

        return super().ready()
