from django.apps import AppConfig


class PncpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_licitacao360.apps.pncp"
    verbose_name = "PNCP - Portal Nacional de Contratações Públicas"

    def ready(self) -> None:
        from . import signals  # noqa: F401
        return super().ready()
