from django.apps import AppConfig


class EmpresasSancionadasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_licitacao360.apps.empresas_sancionadas"
    verbose_name = "Empresas Sancionadas"
    
    def ready(self):
        """Importa os signals quando o app estiver pronto."""
        import django_licitacao360.apps.empresas_sancionadas.signals  # noqa