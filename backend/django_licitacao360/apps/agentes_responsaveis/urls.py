"""URLs do app uasgs."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AgentesResponsaveisViewSet, AgenteResponsavelFuncaoViewSet

router = DefaultRouter()
router.register(r'agentes_responsaveis', AgentesResponsaveisViewSet, basename='agentes_responsaveis')
router.register(
    r'agentes_responsaveis-funcoes',
    AgenteResponsavelFuncaoViewSet,
    basename='agentes_responsaveis_funcoes',
)
urlpatterns = [
    path('', include(router.urls)),
]

