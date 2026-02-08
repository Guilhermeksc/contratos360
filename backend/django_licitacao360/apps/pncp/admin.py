from django.contrib import admin
from .models import AmparoLegal, Compra, ItemCompra, Modalidade, ModoDisputa, ResultadoItem, Fornecedor


@admin.register(AmparoLegal)
class AmparoLegalAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "status_ativo", "data_atualizacao")
    list_filter = ("status_ativo",)
    search_fields = ("nome", "descricao")
    readonly_fields = ("data_inclusao", "data_atualizacao")


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "status_ativo", "data_atualizacao")
    list_filter = ("status_ativo",)
    search_fields = ("nome", "descricao")
    readonly_fields = ("data_inclusao", "data_atualizacao")


@admin.register(ModoDisputa)
class ModoDisputaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "status_ativo", "data_atualizacao")
    list_filter = ("status_ativo",)
    search_fields = ("nome", "descricao")
    readonly_fields = ("data_inclusao", "data_atualizacao")


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("cnpj_fornecedor", "razao_social")
    search_fields = ("cnpj_fornecedor", "razao_social")


class ItemCompraInline(admin.TabularInline):
    model = ItemCompra
    extra = 0
    show_change_link = True


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        "numero_compra",
        "ano_compra",
        "sequencial_compra",
        "modalidade",
        "amparo_legal",
        "modo_disputa",
        "data_publicacao_pncp",
        "valor_total_estimado",
    )
    list_filter = ("ano_compra", "modalidade", "amparo_legal", "modo_disputa", "data_publicacao_pncp")
    search_fields = ("numero_compra", "objeto_compra", "numero_processo", "sequencial_compra")
    inlines = [ItemCompraInline]


class ResultadoItemInline(admin.TabularInline):
    model = ResultadoItem
    extra = 0


@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = (
        "item_id",
        "numero_item",
        "compra",
        "compra_ano_sequencial",
        "unidade_medida",
        "quantidade",
        "tem_resultado",
    )
    list_filter = ("tem_resultado", "situacao_compra_item_nome", "compra__ano_compra", "compra__modalidade")
    search_fields = ("item_id", "descricao", "compra__numero_compra", "compra__sequencial_compra", "compra__ano_compra")
    inlines = [ResultadoItemInline]
    
    def compra_ano_sequencial(self, obj):
        """Exibe ano e sequencial da compra"""
        if obj.compra:
            return f"{obj.compra.ano_compra}/{obj.compra.sequencial_compra}"
        return "-"
    compra_ano_sequencial.short_description = "Ano/Sequencial"
    compra_ano_sequencial.admin_order_field = "compra__ano_compra"


@admin.register(ResultadoItem)
class ResultadoItemAdmin(admin.ModelAdmin):
    list_display = (
        "resultado_id",
        "item_compra",
        "item_compra_info",
        "fornecedor",
        "valor_total_homologado",
        "status",
    )
    list_filter = ("status", "item_compra__compra__ano_compra", "item_compra__compra__modalidade")
    search_fields = (
        "marca",
        "modelo",
        "fornecedor__razao_social",
        "item_compra__compra__numero_compra",
        "item_compra__compra__sequencial_compra",
    )
    
    def item_compra_info(self, obj):
        """Exibe informações da compra relacionada ao item"""
        if obj.item_compra and obj.item_compra.compra:
            compra = obj.item_compra.compra
            return f"{compra.ano_compra}/{compra.sequencial_compra} - Item {obj.item_compra.numero_item}"
        return "-"
    item_compra_info.short_description = "Compra/Item"
    item_compra_info.admin_order_field = "item_compra__compra__ano_compra"
