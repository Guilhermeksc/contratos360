"""
Admin configuration para gestão de contratos
"""

from django.contrib import admin
from .models import (
    Contrato,
    StatusContrato,
    RegistroStatus,
    RegistroMensagem,
    LinksContrato,
    FiscalizacaoContrato,
    HistoricoContrato,
    Empenho,
    ItemContrato,
    ArquivoContrato,
    DadosManuaisContrato,
)


class StatusContratoInline(admin.StackedInline):
    model = StatusContrato
    extra = 0
    can_delete = False


class LinksContratoInline(admin.StackedInline):
    model = LinksContrato
    extra = 0
    can_delete = False


class FiscalizacaoContratoInline(admin.StackedInline):
    model = FiscalizacaoContrato
    extra = 0
    can_delete = False


class DadosManuaisContratoInline(admin.StackedInline):
    model = DadosManuaisContrato
    extra = 0
    can_delete = False


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'numero',
        'uasg',
        'fornecedor_nome',
        'valor_global',
        'vigencia_inicio',
        'vigencia_fim',
        'manual',
    ]
    list_filter = ['manual', 'tipo', 'modalidade', 'vigencia_fim']
    search_fields = [
        'id',
        'numero',
        'processo',
        'fornecedor_nome',
        'fornecedor_cnpj',
        'objeto',
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [
        StatusContratoInline,
        LinksContratoInline,
        FiscalizacaoContratoInline,
        DadosManuaisContratoInline,
    ]
    ordering = ['-vigencia_fim', 'numero']


@admin.register(RegistroStatus)
class RegistroStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'contrato', 'uasg_code', 'texto']
    list_filter = ['uasg_code']
    search_fields = ['texto', 'contrato__id', 'contrato__numero']
    raw_id_fields = ['contrato']


@admin.register(RegistroMensagem)
class RegistroMensagemAdmin(admin.ModelAdmin):
    list_display = ['id', 'contrato', 'texto']
    search_fields = ['texto', 'contrato__id', 'contrato__numero']
    raw_id_fields = ['contrato']


@admin.register(HistoricoContrato)
class HistoricoContratoAdmin(admin.ModelAdmin):
    list_display = ['id', 'contrato', 'numero', 'fornecedor_nome', 'valor_global']
    list_filter = ['tipo', 'categoria']
    search_fields = ['numero', 'processo', 'fornecedor_nome', 'contrato__id']
    raw_id_fields = ['contrato']


@admin.register(Empenho)
class EmpenhoAdmin(admin.ModelAdmin):
    list_display = ['id', 'contrato', 'numero', 'credor_nome', 'empenhado', 'liquidado', 'pago']
    search_fields = ['numero', 'credor_nome', 'credor_cnpj', 'contrato__id']
    raw_id_fields = ['contrato']


@admin.register(ItemContrato)
class ItemContratoAdmin(admin.ModelAdmin):
    list_display = ['id', 'contrato', 'numero_item_compra', 'quantidade', 'valortotal']
    search_fields = ['numero_item_compra', 'descricao_complementar', 'contrato__id']
    raw_id_fields = ['contrato']


@admin.register(ArquivoContrato)
class ArquivoContratoAdmin(admin.ModelAdmin):
    list_display = ['id', 'contrato', 'tipo', 'descricao', 'origem']
    list_filter = ['tipo', 'origem']
    search_fields = ['tipo', 'descricao', 'contrato__id']
    raw_id_fields = ['contrato']

