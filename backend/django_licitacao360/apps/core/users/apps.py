from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_licitacao360.apps.core.users'
    verbose_name = "Gerenciamento de Usuários"

    def ready(self):
        import django_licitacao360.apps.core.users.signals
