"""
Serializers para Fiscalização de Contratos
"""

from rest_framework import serializers
from ..models import FiscalizacaoContrato


class FiscalizacaoContratoSerializer(serializers.ModelSerializer):
    """Serializer para FiscalizacaoContrato"""
    
    class Meta:
        model = FiscalizacaoContrato
        fields = [
            'id',
            'contrato',
            'gestor',
            'gestor_substituto',
            'fiscal_tecnico',
            'fiscal_tec_substituto',
            'fiscal_administrativo',
            'fiscal_admin_substituto',
            'observacoes',
            'data_criacao',
            'data_atualizacao',
        ]
        read_only_fields = ['id', 'contrato']

