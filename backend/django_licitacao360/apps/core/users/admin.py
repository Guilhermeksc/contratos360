from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ("username", "perfil", "is_active")
    list_filter = ("perfil", "is_active")
    search_fields = ("username",)
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informações do Usuário", {"fields": ("perfil",)}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'perfil', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
