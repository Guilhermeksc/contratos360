from django.contrib import admin
from .models import Ata


@admin.register(Ata)
class AtaAdmin(admin.ModelAdmin):
    list_display = (
        "numero_ata_registro_preco",
        "ano_ata",
        "numero_controle_pncp_ata",
        "nome_orgao",
        "nome_unidade_orgao",
        "data_assinatura",
        "vigencia_fim",
        "cancelado",
    )
    list_filter = (
        "ano_ata",
        "cancelado",
        "data_assinatura",
        "vigencia_fim",
        "nome_orgao",
    )
    search_fields = (
        "numero_ata_registro_preco",
        "numero_controle_pncp_ata",
        "numero_controle_pncp_compra",
        "objeto_contratacao",
        "nome_orgao",
        "nome_unidade_orgao",
        "cnpj_orgao",
        "codigo_unidade_orgao",
    )
    readonly_fields = (
        "data_inclusao",
        "data_atualizacao",
        "data_atualizacao_global",
    )
    fieldsets = (
        ("Identificação", {
            "fields": (
                "numero_controle_pncp_ata",
                "numero_ata_registro_preco",
                "ano_ata",
                "sequencial",
                "ano",
                "numero_compra",
            )
        }),
        ("Compra Relacionada", {
            "fields": (
                "numero_controle_pncp_compra",
            )
        }),
        ("Órgão", {
            "fields": (
                "cnpj_orgao",
                "nome_orgao",
                "codigo_unidade_orgao",
                "nome_unidade_orgao",
            )
        }),
        ("Órgão Subrogado", {
            "fields": (
                "cnpj_orgao_subrogado",
                "nome_orgao_subrogado",
                "codigo_unidade_orgao_subrogado",
                "nome_unidade_orgao_subrogado",
            ),
            "classes": ("collapse",),
        }),
        ("Dados da Ata", {
            "fields": (
                "objeto_contratacao",
                "data_assinatura",
                "vigencia_inicio",
                "vigencia_fim",
                "cancelado",
                "data_cancelamento",
            )
        }),
        ("Publicação e Controle", {
            "fields": (
                "data_publicacao_pncp",
                "usuario",
                "data_inclusao",
                "data_atualizacao",
                "data_atualizacao_global",
            )
        }),
    )
