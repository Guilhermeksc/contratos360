from rest_framework import serializers
from .models import (
    AgenteResponsavel,
    AgenteResponsavelFuncao,
    PostoGraduacao,
    Especializacao,
)


class PostoGraduacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostoGraduacao
        fields = ['id_posto', 'nome', 'abreviatura']


class EspecializacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especializacao
        fields = ['id_especializacao', 'nome', 'abreviatura']


class AgenteResponsavelFuncaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenteResponsavelFuncao
        fields = ['id_funcao', 'nome']


class AgenteResponsavelSerializer(serializers.ModelSerializer):
    posto_graduacao = PostoGraduacaoSerializer(read_only=True)
    posto_graduacao_id = serializers.PrimaryKeyRelatedField(
        source='posto_graduacao',
        queryset=PostoGraduacao.objects.all(),
        write_only=True
    )
    especializacao = EspecializacaoSerializer(read_only=True)
    especializacao_id = serializers.PrimaryKeyRelatedField(
        source='especializacao',
        queryset=Especializacao.objects.all(),
        write_only=True,
        required=False
    )
    funcoes = AgenteResponsavelFuncaoSerializer(many=True, read_only=True)
    funcoes_ids = serializers.PrimaryKeyRelatedField(
        source='funcoes',
        queryset=AgenteResponsavelFuncao.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = AgenteResponsavel
        fields = [
            'id_agente_responsavel',
            'nome_de_guerra',
            'posto_graduacao', 'posto_graduacao_id',
            'especializacao', 'especializacao_id',
            'departamento',
            'divisao',
            'os_funcao',
            'os_qualificacao',
            'ativo', 
            'funcoes', 'funcoes_ids',
        ]


class AgenteResponsavelDetailSerializer(serializers.ModelSerializer):
    posto_graduacao = PostoGraduacaoSerializer(read_only=True)
    especializacao = EspecializacaoSerializer(read_only=True)
    funcoes = AgenteResponsavelFuncaoSerializer(many=True, read_only=True)

    class Meta:
        model = AgenteResponsavel
        fields = [
            'id_agente_responsavel',
            'nome_de_guerra',
            'posto_graduacao',
            'especializacao',
            'departamento',
            'divisao',
            'os_funcao',
            'os_qualificacao',
            'ativo', 
            'funcoes',
        ]