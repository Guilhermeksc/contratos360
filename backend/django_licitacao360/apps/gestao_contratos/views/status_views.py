"""
Views para Status de Contratos
"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import StatusContrato, RegistroStatus, RegistroMensagem
from ..serializers import (
    StatusContratoSerializer,
    RegistroStatusSerializer,
    RegistroMensagemSerializer,
)


class StatusContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para StatusContrato
    """
    queryset = StatusContrato.objects.select_related('contrato').all()
    serializer_class = StatusContratoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['uasg_code', 'status']
    search_fields = ['status', 'objeto_editado']
    ordering_fields = ['data_registro']
    ordering = ['-data_registro']


class RegistroStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet para RegistroStatus
    """
    queryset = RegistroStatus.objects.select_related('contrato').all()
    serializer_class = RegistroStatusSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato', 'uasg_code']
    search_fields = ['texto']
    ordering_fields = ['id']
    ordering = ['-id']
    pagination_class = None  # Desabilita paginação para retornar array direto


class RegistroMensagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para RegistroMensagem
    """
    queryset = RegistroMensagem.objects.select_related('contrato').all()
    serializer_class = RegistroMensagemSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato']
    search_fields = ['texto']
    ordering_fields = ['id']
    ordering = ['-id']
    pagination_class = None  # Desabilita paginação para retornar array direto

