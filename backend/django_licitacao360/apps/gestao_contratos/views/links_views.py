"""
Views para Links de Contratos
"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..models import LinksContrato
from ..serializers import LinksContratoSerializer


class LinksContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para LinksContrato
    """
    queryset = LinksContrato.objects.select_related('contrato').all()
    serializer_class = LinksContratoSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['contrato']

