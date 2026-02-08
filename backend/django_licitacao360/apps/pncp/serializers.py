from rest_framework import serializers
from decimal import Decimal
from .models import AmparoLegal, Compra, ItemCompra, Modalidade, ModoDisputa, ResultadoItem, Fornecedor


class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = "__all__"


class ResultadoItemSerializer(serializers.ModelSerializer):
    fornecedor_detalhes = FornecedorSerializer(source="fornecedor", read_only=True)

    class Meta:
        model = ResultadoItem
        exclude = ['status', 'marca', 'modelo']


class ItemCompraSerializer(serializers.ModelSerializer):
    resultados = ResultadoItemSerializer(many=True, read_only=True)

    class Meta:
        model = ItemCompra
        exclude = ['compra', 'tem_resultado']


class ModalidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidade
        fields = ["id", "nome", "descricao"]


class AmparoLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmparoLegal
        fields = ["id", "nome", "descricao"]


class ModoDisputaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModoDisputa
        fields = ["id", "nome", "descricao"]


class CompraSerializer(serializers.ModelSerializer):
    itens = ItemCompraSerializer(many=True, read_only=True)
    modalidade = ModalidadeSerializer(read_only=True)
    amparo_legal = AmparoLegalSerializer(read_only=True)
    modo_disputa = ModoDisputaSerializer(read_only=True)

    class Meta:
        model = Compra
        fields = "__all__"


class ItemResultadoMergeSerializer(serializers.Serializer):
    """Serializer para o merge de itens com resultados"""
    ano_compra = serializers.IntegerField()
    sequencial_compra = serializers.IntegerField()
    numero_item = serializers.IntegerField()
    descricao = serializers.CharField()
    unidade_medida = serializers.CharField()
    valor_unitario_estimado = serializers.DecimalField(max_digits=19, decimal_places=4, allow_null=True)
    valor_total_estimado = serializers.DecimalField(max_digits=19, decimal_places=4, allow_null=True)
    quantidade = serializers.DecimalField(max_digits=19, decimal_places=4)
    situacao_compra_item_nome = serializers.CharField()
    cnpj_fornecedor = serializers.CharField(allow_null=True)
    valor_total_homologado = serializers.DecimalField(max_digits=19, decimal_places=4, allow_null=True)
    valor_unitario_homologado = serializers.DecimalField(max_digits=19, decimal_places=4, allow_null=True)
    quantidade_homologada = serializers.IntegerField(allow_null=True)
    percentual_desconto = serializers.DecimalField(max_digits=7, decimal_places=4, allow_null=True)
    razao_social = serializers.CharField(allow_null=True)


class ModalidadeAgregadaSerializer(serializers.Serializer):
    """Serializer para modalidades agregadas"""
    ano_compra = serializers.IntegerField()
    modalidade_id = serializers.IntegerField(allow_null=True, required=False)
    modalidade = ModalidadeSerializer(allow_null=True, required=False)
    quantidade_compras = serializers.IntegerField()
    valor_total_homologado = serializers.DecimalField(max_digits=19, decimal_places=4, allow_null=True)


class FornecedorAgregadoSerializer(serializers.Serializer):
    """Serializer para fornecedores agregados"""
    cnpj_fornecedor = serializers.CharField()
    razao_social = serializers.CharField(allow_null=True)
    valor_total_homologado = serializers.DecimalField(max_digits=19, decimal_places=4)
