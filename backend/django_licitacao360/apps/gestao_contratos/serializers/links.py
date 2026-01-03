"""
Serializers para Links de Contratos
"""

from rest_framework import serializers
from ..models import LinksContrato


class LinksContratoSerializer(serializers.ModelSerializer):
    """Serializer para LinksContrato"""
    
    class Meta:
        model = LinksContrato
        fields = [
            'id',
            'contrato',
            'link_contrato',
            'link_ta',
            'link_portaria',
            'link_pncp_espc',
            'link_portal_marinha',
        ]
        read_only_fields = ['id', 'contrato']

