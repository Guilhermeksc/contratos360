"""Administração do app uasgs."""

from django.contrib import admin

from .models import ComimSup, Uasg


@admin.register(ComimSup)
class ComimSupAdmin(admin.ModelAdmin):
    list_display = ['sigla_comimsup', 'nome_comimsup', 'uasg']
    search_fields = ['sigla_comimsup', 'nome_comimsup', 'uasg']
    ordering = ['sigla_comimsup']


@admin.register(Uasg)
class UasgAdmin(admin.ModelAdmin):
    list_display = ['uasg', 'sigla_om', 'nome_om', 'uasg_centralizadora', 'uasg_centralizada', 'uf']
    search_fields = ['uasg', 'sigla_om', 'nome_om', 'cidade', 'bairro']
    list_filter = ['uf', 'uasg_centralizadora', 'uasg_centralizada', 'situacao', 'ativa']
    ordering = ['uasg']


