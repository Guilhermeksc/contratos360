from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo do usuário com todos os campos"""
    nivel_acesso_display = serializers.CharField(source='get_nivel_display_name', read_only=True)
    modulos_acesso = serializers.ListField(source='get_modulos_acesso', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "nivel_acesso",
            "nivel_acesso_display",
            "acesso_planejamento",
            "acesso_contratos",
            "acesso_gerata",
            "acesso_empresas",
            "acesso_processo_sancionatorio",
            "acesso_controle_interno",
            "modulos_acesso",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = ["id", "modulos_acesso", "nivel_acesso_display"]


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""
    nivel_acesso_display = serializers.CharField(source='get_nivel_display_name', read_only=True)
    modulos_acesso = serializers.ListField(source='get_modulos_acesso', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "nivel_acesso",
            "nivel_acesso_display",
            "modulos_acesso",
            "is_active",
        ]
