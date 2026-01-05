from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ("username", "nivel_acesso_display", "modulos_acesso_display", "perfis_especiais_display", "is_active", "is_staff")
    list_filter = ("nivel_acesso", "is_active", "is_staff", 
                   "acesso_planejamento", "acesso_contratos", "acesso_gerata",
                   "acesso_empresas", "acesso_processo_sancionatorio", "acesso_controle_interno",
                   "controle_interno")
    search_fields = ("username",)
    ordering = ("username",)
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Nível de Acesso", {
            "fields": ("nivel_acesso",),
            "description": "Nível 1: Menos privilégios | Nível 2: Intermediário | Nível 3: Máximos privilégios"
        }),
        ("Permissões por Módulo", {
            "fields": (
                "acesso_planejamento",
                "acesso_contratos",
                "acesso_gerata",
                "acesso_empresas",
                "acesso_processo_sancionatorio",
                "acesso_controle_interno",
            ),
            "description": "Selecione os módulos aos quais o usuário terá acesso. Usuários de nível 3 têm acesso automático a todos."
        }),
        ("Perfis Especiais", {
            "fields": (
                "uasg_centralizadora",
                "uasg_centralizada",
                "controle_interno",
            ),
            "description": "Configure os perfis específicos (UASG Centralizadora/Centralizada ou Controle Interno)."
        }),
        ("Permissões do Sistema", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Informações Adicionais", {
            "fields": ("date_joined", "last_login"),
            "classes": ("collapse",)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'password1', 
                'password2',
                'nivel_acesso',
                'is_active', 
                'is_staff', 
                'is_superuser'
            ),
        }),
        ("Permissões por Módulo", {
            'classes': ('wide',),
            'fields': (
                'acesso_planejamento',
                'acesso_contratos',
                'acesso_gerata',
                'acesso_empresas',
                'acesso_processo_sancionatorio',
                'acesso_controle_interno',
            ),
        }),
        ("Perfis Especiais", {
            'classes': ('wide',),
            'fields': (
                'uasg_centralizadora',
                'uasg_centralizada',
                'controle_interno',
            ),
        }),
    )
    
    readonly_fields = ("date_joined", "last_login")
    
    def nivel_acesso_display(self, obj):
        """Exibe o nível de acesso com cor"""
        cores = {
            1: "gray",
            2: "orange", 
            3: "green"
        }
        cor = cores.get(obj.nivel_acesso, "black")
        nivel_nome = obj.get_nivel_display_name()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            cor,
            nivel_nome
        )
    nivel_acesso_display.short_description = "Nível de Acesso"
    
    def modulos_acesso_display(self, obj):
        """Exibe os módulos de acesso de forma compacta"""
        modulos = obj.get_modulos_acesso()
        if not modulos:
            return format_html('<span style="color: red;">Nenhum módulo</span>')
        
        # Nomes amigáveis
        nomes_modulos = {
            'planejamento': 'Planejamento',
            'contratos': 'Contratos',
            'gerata': 'Gerata',
            'empresas': 'Empresas',
            'processo_sancionatorio': 'Proc. Sancionatório',
            'controle_interno': 'Controle Interno',
        }
        
        modulos_formatados = [nomes_modulos.get(m, m) for m in modulos]
        return ', '.join(modulos_formatados)
    modulos_acesso_display.short_description = "Módulos com Acesso"

    def perfis_especiais_display(self, obj):
        """Exibe os perfis extras atribuídos ao usuário."""
        perfis = obj.get_perfis_especiais()
        if not perfis:
            return format_html('<span style="color: gray;">Sem perfis especiais</span>')
        labels = {
            'uasg_centralizadora': 'UASG Centralizadora',
            'uasg_centralizada': 'UASG Centralizada',
            'controle_interno': 'Controle Interno',
        }
        nomes = [labels.get(perfil, perfil.replace('_', ' ').title()) for perfil in perfis]
        return ', '.join(nomes)
    perfis_especiais_display.short_description = "Perfis Especiais"
    
    def get_readonly_fields(self, request, obj=None):
        """Torna os campos de módulo readonly para nível 3"""
        readonly = list(self.readonly_fields)
        if obj and obj.nivel_acesso == 3:
            readonly.extend([
                'acesso_planejamento',
                'acesso_contratos',
                'acesso_gerata',
                'acesso_empresas',
                'acesso_processo_sancionatorio',
                'acesso_controle_interno',
            ])
        return readonly
