from rest_framework import serializers

from .models import EmpresasSancionadas


class EmpresasSancionadasSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpresasSancionadas
        fields = [
            "id",
            "cadastro",
            "codigo_sancao",
            "tipo_pessoa",
            "cpf_cnpj",
            "nome_sancionado",
            "nome_orgao_sancionador",
            "razao_social",
            "nome_fantasia",
            "numero_processo",
            "categoria_sancao",
            "data_inicio_sancao",
            "data_final_sancao",
            "data_publicacao",
            "publicacao",
            "detalhamento_meio_publicacao",
            "data_transito_julgado",
            "abrangencia_sancao",
            "orgao_sancionador",
            "uf_orgao_sancionador",
            "esfera_orgao_sancionador",
            "fundamentacao_legal",
            "data_origem_informacao",
            "origem_informacoes",
            "observacoes",
            "created_at",
            "updated_at",
        ]
