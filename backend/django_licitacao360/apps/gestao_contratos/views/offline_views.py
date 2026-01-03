"""
Views para dados offline (Histórico, Empenhos, Itens, Arquivos)
"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import HistoricoContrato, Empenho, ItemContrato, ArquivoContrato
from ..serializers import (
    HistoricoContratoSerializer,
    EmpenhoSerializer,
    ItemContratoSerializer,
    ArquivoContratoSerializer,
)


class HistoricoContratoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para HistoricoContrato (somente leitura)
    """
    queryset = HistoricoContrato.objects.select_related('contrato').all()
    serializer_class = HistoricoContratoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato', 'tipo', 'categoria']
    search_fields = ['numero', 'processo', 'fornecedor_nome', 'objeto']
    ordering_fields = ['data_assinatura', 'valor_global']
    ordering = ['-data_assinatura']


class EmpenhoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Empenho (somente leitura)
    """
    queryset = Empenho.objects.select_related('contrato').all()
    serializer_class = EmpenhoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato', 'unidade_gestora', 'gestao']
    search_fields = ['numero', 'credor_nome', 'credor_cnpj']
    ordering_fields = ['data_emissao', 'empenhado']
    ordering = ['-data_emissao']


class ItemContratoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ItemContrato (somente leitura)
    """
    queryset = ItemContrato.objects.select_related('contrato').all()
    serializer_class = ItemContratoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato', 'tipo_material']
    search_fields = ['numero_item_compra', 'descricao_complementar']
    ordering_fields = ['valortotal']
    ordering = ['-valortotal']


class ArquivoContratoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ArquivoContrato (somente leitura)
    """
    queryset = ArquivoContrato.objects.select_related('contrato').all()
    serializer_class = ArquivoContratoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato', 'tipo', 'origem']
    search_fields = ['tipo', 'descricao']
    ordering_fields = ['id']
    ordering = ['-id']

