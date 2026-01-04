"""
Serializers para Status de Contratos
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from ..models import StatusContrato, RegistroStatus, RegistroMensagem, Contrato


class StatusContratoSerializer(serializers.ModelSerializer):
    """Serializer para StatusContrato"""
    uasg_nome = serializers.CharField(source='contrato.uasg.nome_resumido', read_only=True)
    
    class Meta:
        model = StatusContrato
        fields = [
            'contrato',
            'uasg_code',
            'uasg_nome',
            'status',
            'objeto_editado',
            'portaria_edit',
            'termo_aditivo_edit',
            'pode_renovar',
            'custeio',
            'natureza_continuada',
            'tipo_contrato',
            'data_registro',
        ]
        read_only_fields = ['uasg_nome']  # Campo calculado, sempre somente leitura
    
    def validate(self, attrs):
        """
        Valida os dados, mas não valida unicidade do campo contrato
        O método create fará update_or_create, então não precisamos validar unicidade aqui
        """
        return attrs
    
    def create(self, validated_data):
        """Cria ou atualiza um StatusContrato"""
        # O DRF já converteu o ID do contrato para uma instância durante a validação
        contrato = validated_data.pop('contrato')
        
        # Garante que status tenha um valor padrão se não foi fornecido
        if 'status' not in validated_data or not validated_data.get('status'):
            validated_data['status'] = 'SEÇÃO CONTRATOS'
        
        # Sempre usa update_or_create para lidar com relacionamento OneToOne
        # Isso evita erro de unicidade quando já existe um status para o contrato
        try:
            status_obj, created = StatusContrato.objects.update_or_create(
                contrato=contrato,
                defaults=validated_data
            )
            return status_obj
        except Exception as e:
            import traceback
            error_detail = str(e)
            traceback.print_exc()
            raise serializers.ValidationError({
                'non_field_errors': f'Erro ao salvar status: {error_detail}'
            })
    
    def update(self, instance, validated_data):
        """Atualiza um StatusContrato existente"""
        # Remove 'contrato' dos dados validados pois não pode ser alterado
        validated_data.pop('contrato', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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

