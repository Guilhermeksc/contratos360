from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo do usuário com todos os campos"""
    nivel_acesso_display = serializers.CharField(source='get_nivel_display_name', read_only=True)
    modulos_acesso = serializers.ListField(source='get_modulos_acesso', read_only=True)
    perfis_especiais = serializers.ListField(source='get_perfis_especiais', read_only=True)
    uasg_centralizadora_info = serializers.SerializerMethodField()
    uasg_centralizada_info = serializers.SerializerMethodField()
    
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
            "uasg_centralizadora",
            "uasg_centralizada",
            "uasg_centralizadora_info",
            "uasg_centralizada_info",
            "controle_interno",
            "modulos_acesso",
            "perfis_especiais",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = [
            "id",
            "modulos_acesso",
            "nivel_acesso_display",
            "perfis_especiais",
            "uasg_centralizadora_info",
            "uasg_centralizada_info",
        ]

    def _uasg_to_dict(self, uasg):
        if not uasg:
            return None
        return {
            "id": uasg.id_uasg,
            "uasg": uasg.uasg,
            "sigla": uasg.sigla_om,
            "nome": uasg.nome_om,
        }

    def get_uasg_centralizadora_info(self, obj):
        return self._uasg_to_dict(obj.uasg_centralizadora)

    def get_uasg_centralizada_info(self, obj):
        return self._uasg_to_dict(obj.uasg_centralizada)


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""
    nivel_acesso_display = serializers.CharField(source='get_nivel_display_name', read_only=True)
    modulos_acesso = serializers.ListField(source='get_modulos_acesso', read_only=True)
    perfis_especiais = serializers.ListField(source='get_perfis_especiais', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "nivel_acesso",
            "nivel_acesso_display",
            "modulos_acesso",
            "uasg_centralizadora",
            "uasg_centralizada",
            "controle_interno",
            "perfis_especiais",
            "is_active",
        ]
