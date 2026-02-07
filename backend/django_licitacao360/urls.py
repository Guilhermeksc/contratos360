from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
import os

# Personalização do Django Admin
admin.site.site_header = "Administração do Licitacação 360"
admin.site.site_title = "Administração do Licitacação 360"
admin.site.index_title = "Painel de Administração"

def health_check(request):
    """
    Endpoint de health check para Docker/Kubernetes
    Verifica status do banco de dados e Redis
    """
    checks = {
        "status": "healthy",
        "service": "licitacao360_backend",
        "database": "ok",
        "redis": "ok",
    }
    
    # Verificar banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        checks["status"] = "unhealthy"
    
    # Verificar Redis (opcional, apenas se disponível)
    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
        if redis_url.startswith("redis://"):
            # Tentar importar redis apenas se necessário
            from redis import Redis
            r = Redis.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
        # Não marcar como unhealthy se Redis falhar (pode não estar disponível)
    
    status_code = 200 if checks["status"] == "healthy" else 503
    return JsonResponse(checks, status=status_code)

urlpatterns = [
    path('admin/', admin.site.urls),  # Usa admin.site padrão com configurações customizadas

    # Health Check
    path('api/health/', health_check, name='health_check'),

    # Autenticação JWT
    path('api/auth/', include('django_licitacao360.apps.core.auth.urls')),

    # Files (servir arquivos protegidos)
    path('api/files/', include('django_licitacao360.apps.core.files.urls')),

    # Cadastro de Agentes Responsáveis
    path('api/', include('django_licitacao360.apps.agentes_responsaveis.urls')),

    # Gestão de Contratos
    path('api/', include('django_licitacao360.apps.gestao_contratos.urls')),

    # Imprensa Nacional (INLABS)
    path('api/inlabs/', include('django_licitacao360.apps.imprensa_nacional.urls')),
    
    # Empresas Sancionadas (CEIS)
    path('api/', include('django_licitacao360.apps.empresas_sancionadas.urls')),
    
    # PNCP (Portal Nacional de Contratações Públicas)
    path('api/pncp/', include('django_licitacao360.apps.pncp.urls')),
]
