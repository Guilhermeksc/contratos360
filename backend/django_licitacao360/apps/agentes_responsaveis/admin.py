from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    AgenteResponsavel,
    AgenteResponsavelFuncao,
    PostoGraduacao,
    Especializacao,
)
from .resources import (
    AgenteResponsavelResource,
    AgenteResponsavelFuncaoResource,
    PostoGraduacaoResource,
    EspecializacaoResource,
)


@admin.register(PostoGraduacao)
class PostoGraduacaoAdmin(ImportExportModelAdmin):
    resource_class = PostoGraduacaoResource
    list_display = ('id_posto', 'nome', 'abreviatura')
    search_fields = ('nome', 'abreviatura')


@admin.register(Especializacao)
class EspecializacaoAdmin(ImportExportModelAdmin):
    resource_class = EspecializacaoResource
    list_display = ('id_especializacao', 'nome', 'abreviatura')
    search_fields = ('nome', 'abreviatura')


@admin.register(AgenteResponsavelFuncao)
class AgenteResponsavelFuncaoAdmin(ImportExportModelAdmin):
    resource_class = AgenteResponsavelFuncaoResource
    list_display = ('id_funcao', 'nome')
    search_fields = ('nome',)


@admin.register(AgenteResponsavel)
class AgenteResponsavelAdmin(ImportExportModelAdmin):
    resource_class = AgenteResponsavelResource
    list_display = (
        'id_agente_responsavel',
        'nome_de_guerra',
        'posto_graduacao',
        'especializacao',
        'departamento',
        'divisao',
        'os_funcao',
        'os_qualificacao',
        'ativo',
    )
    search_fields = (
        'nome_de_guerra',
        'departamento',
        'divisao',
        'os_funcao',
        'os_qualificacao',
    )
    list_filter = (
        'posto_graduacao',
        'especializacao',
        'departamento',
        'divisao',
        'ativo',
    )
    filter_horizontal = ('funcoes',)