"""
Serializers para Status de Contratos
"""

from rest_framework import serializers
from ..models import StatusContrato, RegistroStatus, RegistroMensagem


class StatusContratoSerializer(serializers.ModelSerializer):
    """Serializer para StatusContrato"""
    
    class Meta:
        model = StatusContrato
        fields = [
            'contrato',
            'uasg_code',
            'status',
            'objeto_editado',
            'portaria_edit',
            'termo_aditivo_edit',
            'radio_options_json',
            'data_registro',
        ]
        read_only_fields = ['contrato']


class RegistroStatusSerializer(serializers.ModelSerializer):
    """Serializer para RegistroStatus"""
    
    class Meta:
        model = RegistroStatus
        fields = ['id', 'contrato', 'uasg_code', 'texto']
        read_only_fields = ['id']


class RegistroMensagemSerializer(serializers.ModelSerializer):
    """Serializer para RegistroMensagem"""
    
    class Meta:
        model = RegistroMensagem
        fields = ['id', 'contrato', 'texto']
        read_only_fields = ['id']

