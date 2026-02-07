from django.contrib import admin
from .models import Compra, ItemCompra, ResultadoItem, Fornecedor


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
        "modalidade_nome",
        "data_publicacao_pncp",
        "valor_total_estimado",
    )
    list_filter = ("ano_compra", "modalidade_nome", "data_publicacao_pncp")
    search_fields = ("numero_compra", "objeto_compra", "numero_processo")
    inlines = [ItemCompraInline]


class ResultadoItemInline(admin.TabularInline):
    model = ResultadoItem
    extra = 0


@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = ("numero_item", "compra", "unidade_medida", "quantidade", "tem_resultado")
    list_filter = ("tem_resultado", "situacao_compra_item_nome")
    search_fields = ("descricao", "compra__numero_compra")
    inlines = [ResultadoItemInline]


@admin.register(ResultadoItem)
class ResultadoItemAdmin(admin.ModelAdmin):
    list_display = ("resultado_id", "item_compra", "fornecedor", "valor_total_homologado", "status")
    list_filter = ("status",)
    search_fields = ("marca", "modelo", "fornecedor__razao_social")
