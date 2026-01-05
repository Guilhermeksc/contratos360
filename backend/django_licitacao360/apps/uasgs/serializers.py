"""Serializers reutilizáveis para ComimSup e UASG."""

from rest_framework import serializers

from .models import ComimSup, Uasg


class ComimSupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComimSup
        fields = ['id', 'uasg', 'sigla_comimsup', 'indicativo_comimsup', 'nome_comimsup']


class UasgSerializer(serializers.ModelSerializer):
    comimsup_nome = serializers.CharField(source='comimsup.nome_comimsup', read_only=True)

    class Meta:
        model = Uasg
        fields = [
            'id_uasg',
            'uasg',
            'sigla_om',
            'nome_om',
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
        read_only_fields = ['id_uasg', 'comimsup_nome']
