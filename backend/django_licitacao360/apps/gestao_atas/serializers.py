from rest_framework import serializers
from .models import Ata


class AtaSerializer(serializers.ModelSerializer):
    """Serializer para Ata"""
    class Meta:
        model = Ata
        fields = "__all__"


class AtaListagemSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Atas"""
    class Meta:
        model = Ata
        fields = (
            "numero_controle_pncp_ata",
            "numero_ata_registro_preco",
            "ano_ata",
            "nome_orgao",
            "nome_unidade_orgao",
            "objeto_contratacao",
            "data_assinatura",
            "vigencia_inicio",
            "vigencia_fim",
            "cancelado",
            "data_cancelamento",
        )
