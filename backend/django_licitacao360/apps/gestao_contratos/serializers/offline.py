"""
Serializers para dados offline (Histórico, Empenhos, Itens, Arquivos)
"""

from rest_framework import serializers
from ..models import HistoricoContrato, Empenho, ItemContrato, ArquivoContrato


class HistoricoContratoSerializer(serializers.ModelSerializer):
    """Serializer para HistoricoContrato"""
    
    class Meta:
        model = HistoricoContrato
        fields = [
            'id',
            'contrato',
            'receita_despesa',
            'numero',
            'observacao',
            'ug',
            'gestao',
            'fornecedor_cnpj',
            'fornecedor_nome',
            'tipo',
            'categoria',
            'processo',
            'objeto',
            'modalidade',
            'licitacao_numero',
            'data_assinatura',
            'data_publicacao',
            'vigencia_inicio',
            'vigencia_fim',
            'valor_global',
            'raw_json',
        ]
        read_only_fields = ['id']


class EmpenhoSerializer(serializers.ModelSerializer):
    """Serializer para Empenho"""
    
    class Meta:
        model = Empenho
        fields = [
            'id',
            'contrato',
            'unidade_gestora',
            'gestao',
            'numero',
            'data_emissao',
            'credor_cnpj',
            'credor_nome',
            'empenhado',
            'liquidado',
            'pago',
            'informacao_complementar',
            'raw_json',
        ]
        read_only_fields = ['id']


class ItemContratoSerializer(serializers.ModelSerializer):
    """Serializer para ItemContrato"""
    
    class Meta:
        model = ItemContrato
        fields = [
            'id',
            'contrato',
            'tipo_id',
            'tipo_material',
            'grupo_id',
            'catmatseritem_id',
            'descricao_complementar',
            'quantidade',
            'valorunitario',
            'valortotal',
            'numero_item_compra',
            'raw_json',
        ]
        read_only_fields = ['id']


class ArquivoContratoSerializer(serializers.ModelSerializer):
    """Serializer para ArquivoContrato"""
    
    class Meta:
        model = ArquivoContrato
        fields = [
            'id',
            'contrato',
            'tipo',
            'descricao',
            'path_arquivo',
            'origem',
            'link_sei',
            'raw_json',
        ]
        read_only_fields = ['id']

