"""Serializers reutilizáveis para ComimSup e UASG."""

from rest_framework import serializers

from .models import ComimSup, Uasg


class ComimSupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComimSup
        fields = ['id', 'uasg', 'sigla_comimsup', 'indicativo_comimsup', 'nome_comimsup']


class UasgSerializer(serializers.ModelSerializer):
    comimsup_nome = serializers.CharField(source='comimsup.nome_comimsup', read_only=True)
    uasg_code = serializers.SerializerMethodField()
    nome_resumido = serializers.SerializerMethodField()

    class Meta:
        model = Uasg
        fields = [
            'id_uasg',
            'uasg',
            'uasg_code',  # Propriedade para compatibilidade com frontend
            'sigla_om',
            'nome_om',
            'nome_resumido',  # Propriedade para compatibilidade com frontend
            'indicativo_om',
            'uasg_centralizadora',
            'uasg_centralizada',
            'uf',
            'cidade',
            'bairro',
            'classificacao',
            'endereco',
            'cep',
            'secom',
            'cnpj',
            'ddi',
            'ddd',
            'telefone',
            'intranet',
            'internet',
            'distrito',
            'ods',
            'situacao',
            'ativa',
            'comimsup',
            'comimsup_nome',
        ]
        read_only_fields = ['id_uasg', 'comimsup_nome', 'uasg_code', 'nome_resumido']
    
    def get_uasg_code(self, obj):
        """Retorna o código UASG como string"""
        return str(obj.uasg) if obj.uasg else None
    
    def get_nome_resumido(self, obj):
        """Retorna o nome resumido (nome_om)"""
        return obj.nome_om
