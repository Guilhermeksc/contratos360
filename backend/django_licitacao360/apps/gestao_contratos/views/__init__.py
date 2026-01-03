"""
Views para gestão de contratos
"""

from .contrato_views import ContratoViewSet, ContratoDetalhesView
from .status_views import StatusContratoViewSet, RegistroStatusViewSet, RegistroMensagemViewSet
from .links_views import LinksContratoViewSet
from .fiscalizacao_views import FiscalizacaoContratoViewSet
from .offline_views import (
    HistoricoContratoViewSet,
    EmpenhoViewSet,
    ItemContratoViewSet,
    ArquivoContratoViewSet,
)
from .uasg_views import UasgViewSet

__all__ = [
    'UasgViewSet',
    'ContratoViewSet',
    'ContratoDetalhesView',
    'StatusContratoViewSet',
    'RegistroStatusViewSet',
    'RegistroMensagemViewSet',
    'LinksContratoViewSet',
    'FiscalizacaoContratoViewSet',
    'HistoricoContratoViewSet',
    'EmpenhoViewSet',
    'ItemContratoViewSet',
    'ArquivoContratoViewSet',
]

