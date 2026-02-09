from django.contrib import admin

from .models import InlabsArticle, AvisoLicitacao, Credenciamento


@admin.register(InlabsArticle)
class InlabsArticleAdmin(admin.ModelAdmin):
    """Admin para artigos INLABS."""

    list_display = ("article_id", "pub_date", "name", "pub_name", "art_type", "uasg", "nome_om")
    search_fields = ("article_id", "name", "nome_om", "materia_id", "uasg")
    list_filter = ("pub_date", "pub_name", "art_type", "nome_om")
    ordering = ("-pub_date", "article_id")
    readonly_fields = ("article_id", "pub_date", "materia_id")
    fieldsets = (
        ("Identificação", {
            "fields": ("article_id", "pub_date", "materia_id", "name", "id_oficio")
        }),
        ("Publicação", {
            "fields": ("pub_name", "art_type", "edition_number", "number_page", "pdf_page")
        }),
        ("Organização", {
            "fields": ("nome_om", "uasg")
        }),
        ("Conteúdo", {
            "fields": ("body_identifica", "body_texto"),
            "classes": ("collapse",)
        }),
        ("Destaques", {
            "fields": (
                "highlight_type",
                "highlight_priority",
                "highlight",
                "highlight_image",
                "highlight_image_name",
            ),
            "classes": ("collapse",)
        }),
    )


@admin.register(AvisoLicitacao)
class AvisoLicitacaoAdmin(admin.ModelAdmin):
    """Admin para avisos de licitação."""

    list_display = (
        "article_id",
        "get_pub_date",
        "modalidade",
        "numero",
        "ano",
        "uasg",
        "processo",
        "nome_responsavel",
    )

    def get_pub_date(self, obj):
        """Retorna a data de publicação do artigo relacionado."""
        article = obj.article
        return article.pub_date if article else "-"
    get_pub_date.short_description = "Data Publicação"
    search_fields = (
        "article_id",
        "modalidade",
        "numero",
        "processo",
        "uasg",
        "objeto",
        "nome_responsavel",
    )
    list_filter = ("modalidade", "ano", "uasg")
    ordering = ("-ano", "-numero")
    readonly_fields = ("article_id",)
    fieldsets = (
        ("Identificação", {
            "fields": ("article_id", "modalidade", "numero", "ano", "uasg", "processo")
        }),
        ("Detalhes", {
            "fields": ("objeto", "itens_licitados", "publicacao")
        }),
        ("Datas", {
            "fields": ("entrega_propostas", "abertura_propostas")
        }),
        ("Responsável", {
            "fields": ("nome_responsavel", "cargo")
        }),
    )


@admin.register(Credenciamento)
class CredenciamentoAdmin(admin.ModelAdmin):
    """Admin para credenciamentos."""

    list_display = (
        "article_id",
        "get_pub_date",
        "tipo",
        "numero",
        "ano",
        "uasg",
        "contratante",
        "contratado",
        "nome_responsavel",
    )

    def get_pub_date(self, obj):
        """Retorna a data de publicação do artigo relacionado."""
        article = obj.article
        return article.pub_date if article else "-"
    get_pub_date.short_description = "Data Publicação"
    search_fields = (
        "article_id",
        "tipo",
        "numero",
        "processo",
        "uasg",
        "contratante",
        "contratado",
        "objeto",
        "nome_responsavel",
    )
    list_filter = ("tipo", "ano", "uasg")
    ordering = ("-ano", "-numero")
    readonly_fields = ("article_id",)
    fieldsets = (
        ("Identificação", {
            "fields": ("article_id", "tipo", "numero", "ano", "uasg", "processo")
        }),
        ("Processo", {
            "fields": ("tipo_processo", "numero_processo", "ano_processo")
        }),
        ("Partes", {
            "fields": ("contratante", "contratado")
        }),
        ("Detalhes", {
            "fields": ("objeto", "fundamento_legal", "vigencia", "valor_total", "data_assinatura")
        }),
        ("Responsável", {
            "fields": ("nome_responsavel", "cargo")
        }),
    )
