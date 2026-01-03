"""
URLs para gestão de contratos
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UasgViewSet,
    ContratoViewSet,
    ContratoDetalhesView,
    StatusContratoViewSet,
    RegistroStatusViewSet,
    RegistroMensagemViewSet,
    LinksContratoViewSet,
    FiscalizacaoContratoViewSet,
    HistoricoContratoViewSet,
    EmpenhoViewSet,
    ItemContratoViewSet,
    ArquivoContratoViewSet,
)

router = DefaultRouter()
router.register(r'uasgs', UasgViewSet, basename='uasg')
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'status', StatusContratoViewSet, basename='status-contrato')
router.register(r'registros-status', RegistroStatusViewSet, basename='registro-status')
router.register(r'registros-mensagem', RegistroMensagemViewSet, basename='registro-mensagem')
router.register(r'links', LinksContratoViewSet, basename='links-contrato')
router.register(r'fiscalizacao', FiscalizacaoContratoViewSet, basename='fiscalizacao-contrato')
router.register(r'historico', HistoricoContratoViewSet, basename='historico-contrato')
router.register(r'empenhos', EmpenhoViewSet, basename='empenho')
router.register(r'itens', ItemContratoViewSet, basename='item-contrato')
router.register(r'arquivos', ArquivoContratoViewSet, basename='arquivo-contrato')

urlpatterns = [
    path('', include(router.urls)),
]

