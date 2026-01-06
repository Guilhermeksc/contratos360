from django.contrib import admin
from django.utils.html import format_html

from .models import CalendarioEvento


@admin.register(CalendarioEvento)
class CalendarioEventoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "data", "cor_display", "descricao_resumida", "created_at")
    search_fields = ("nome", "descricao")
    list_filter = ("data", "created_at")
    ordering = ("-data", "nome")
    date_hierarchy = "data"
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("nome", "data", "cor")
        }),
        ("Descrição", {
            "fields": ("descricao",)
        }),
        ("Metadados", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    def cor_display(self, obj):
        """Exibe a cor como um quadrado colorido."""
        if obj.cor:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span> {}',
                obj.cor,
                obj.cor
            )
        return "-"
    cor_display.short_description = "Cor"
    
    def descricao_resumida(self, obj):
        """Retorna uma versão resumida da descrição."""
        if obj.descricao:
            return obj.descricao[:50] + "..." if len(obj.descricao) > 50 else obj.descricao
        return "-"
    descricao_resumida.short_description = "Descrição"
