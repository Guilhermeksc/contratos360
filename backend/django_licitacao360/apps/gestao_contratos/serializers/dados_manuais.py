"""
Serializers para Dados Manuais de Contratos
"""

from rest_framework import serializers
from ..models import DadosManuaisContrato


class DadosManuaisContratoSerializer(serializers.ModelSerializer):
    """Serializer para DadosManuaisContrato"""
    
    class Meta:
        model = DadosManuaisContrato
        fields = [
            'contrato',
            'sigla_om_resp',
            'orgao_responsavel',
            'portaria',
            'created_by',
        ]
        read_only_fields = ['contrato', 'created_by']

