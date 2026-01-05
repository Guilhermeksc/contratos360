from import_export import resources
from .models import (
    AgenteResponsavel,
    AgenteResponsavelFuncao,
    PostoGraduacao,
    Especializacao,
)


class PostoGraduacaoResource(resources.ModelResource):
    class Meta:
        model = PostoGraduacao
        fields = ("id_posto", "nome", "abreviatura")
        export_order = fields


class EspecializacaoResource(resources.ModelResource):
    class Meta:
        model = Especializacao
        fields = ("id_especializacao", "nome", "abreviatura")
        export_order = fields


class AgenteResponsavelFuncaoResource(resources.ModelResource):
    class Meta:
        model = AgenteResponsavelFuncao
        fields = ("id_funcao", "nome")
        export_order = fields


class AgenteResponsavelResource(resources.ModelResource):
    class Meta:
        model = AgenteResponsavel
        fields = (
            "id_agente_responsavel",
            "nome_de_guerra",
            "posto_graduacao__nome",
            "especializacao__nome",
            "departamento",
            "divisao",
            "os_funcao",
            "os_qualificacao",
            "ativo",
        )
        export_order = fields
