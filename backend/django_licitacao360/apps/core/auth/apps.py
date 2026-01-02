from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_licitacao360.apps.core.auth'
    label = 'core_auth'  # Label único para evitar conflito com django.contrib.auth
    verbose_name = 'Autenticação Personalizada'