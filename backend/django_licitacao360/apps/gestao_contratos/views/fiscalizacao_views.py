"""
Views para Fiscalização de Contratos
"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..models import FiscalizacaoContrato
from ..serializers import FiscalizacaoContratoSerializer


class FiscalizacaoContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para FiscalizacaoContrato
    """
    queryset = FiscalizacaoContrato.objects.select_related('contrato').all()
    serializer_class = FiscalizacaoContratoSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['contrato']

