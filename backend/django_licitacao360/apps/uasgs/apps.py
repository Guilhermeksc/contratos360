from django.apps import AppConfig


class UasgsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_licitacao360.apps.uasgs"
    verbose_name = "Cadastro de UASGs"

    def ready(self) -> None:
        # Garante o registro dos sinais de carga automática
        from . import signals  # noqa: F401

        return super().ready()

