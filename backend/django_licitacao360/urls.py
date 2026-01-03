from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Personalização do Django Admin
admin.site.site_header = "Administração do Sistema de apoio ao Cemos"
admin.site.site_title = "Administração do Sistema de apoio ao Cemos"
admin.site.index_title = "Painel de Administração"

def health_check(request):
    return JsonResponse({"status": "healthy", "service": "licitacao360_backend"})

urlpatterns = [
    path('admin/', admin.site.urls),  # Usa admin.site padrão com configurações customizadas

    # Health Check
    path('api/health/', health_check, name='health_check'),

    # Autenticação JWT
    path('api/auth/', include('django_licitacao360.apps.core.auth.urls')),

    # Gestão de Contratos
    path('api/', include('django_licitacao360.apps.gestao_contratos.urls')),
]
