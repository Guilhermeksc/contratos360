from django.contrib import admin

from .models import EmpresasSancionadas


@admin.register(EmpresasSancionadas)
class EmpresasSancionadasAdmin(admin.ModelAdmin):
    list_display = (
        "nome_sancionado",
        "cpf_cnpj",
        "codigo_sancao",
        "categoria_sancao",
        "data_inicio_sancao",
        "data_final_sancao",
        "orgao_sancionador",
    )
    search_fields = (
        "nome_sancionado",
        "cpf_cnpj",
        "codigo_sancao",
        "razao_social",
        "nome_fantasia",
        "numero_processo",
    )
    list_filter = (
        "tipo_pessoa",
        "categoria_sancao",
        "esfera_orgao_sancionador",
        "uf_orgao_sancionador",
        "data_inicio_sancao",
        "data_final_sancao",
    )
    ordering = ("-data_inicio_sancao", "nome_sancionado")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "data_inicio_sancao"
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": (
                "cadastro",
                "codigo_sancao",
                "tipo_pessoa",
                "cpf_cnpj",
                "nome_sancionado",
                "razao_social",
                "nome_fantasia",
            )
        }),
        ("Sanção", {
            "fields": (
                "categoria_sancao",
                "data_inicio_sancao",
                "data_final_sancao",
                "abrangencia_sancao",
                "fundamentacao_legal",
            )
        }),
        ("Órgão Sancionador", {
            "fields": (
                "orgao_sancionador",
                "nome_orgao_sancionador",
                "uf_orgao_sancionador",
                "esfera_orgao_sancionador",
            )
        }),
        ("Processo e Publicação", {
            "fields": (
                "numero_processo",
                "data_publicacao",
                "publicacao",
                "detalhamento_meio_publicacao",
                "data_transito_julgado",
            )
        }),
        ("Informações Adicionais", {
            "fields": (
                "origem_informacoes",
                "data_origem_informacao",
                "observacoes",
            )
        }),
        ("Controle", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
