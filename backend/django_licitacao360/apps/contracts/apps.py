from django.apps import AppConfig

class PerguntasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_licitacao360.apps.perguntas'        
    verbose_name = "Gerenciamento de Perguntas"

    def ready(self):
        import django_licitacao360.apps.perguntas.signals  # noqa
