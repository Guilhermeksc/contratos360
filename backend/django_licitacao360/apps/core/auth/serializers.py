from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django_licitacao360.apps.core.users.models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Campos adicionais no payload JWT:
        token['username'] = user.username
        token['nivel_acesso'] = user.nivel_acesso
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        # Adiciona permissões por módulo no token
        token['acesso_planejamento'] = user.acesso_planejamento
        token['acesso_contratos'] = user.acesso_contratos
        token['acesso_gerata'] = user.acesso_gerata
        token['acesso_empresas'] = user.acesso_empresas
        token['acesso_processo_sancionatorio'] = user.acesso_processo_sancionatorio
        token['acesso_controle_interno'] = user.acesso_controle_interno
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Preparar dados das UASGs se existirem
        uasg_centralizadora_data = None
        if self.user.uasg_centralizadora:
            uasg_centralizadora_data = {
                'codigo': self.user.uasg_centralizadora.uasg,
                'nome': self.user.uasg_centralizadora.nome_om or self.user.uasg_centralizadora.sigla_om,
                'sigla': self.user.uasg_centralizadora.sigla_om,
            }
        
        uasg_centralizada_data = None
        if self.user.uasg_centralizada:
            uasg_centralizada_data = {
                'codigo': self.user.uasg_centralizada.uasg,
                'nome': self.user.uasg_centralizada.nome_om or self.user.uasg_centralizada.sigla_om,
                'sigla': self.user.uasg_centralizada.sigla_om,
            }
        
        # Adicionar dados do usuário na resposta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'nivel_acesso': self.user.nivel_acesso,
            'nivel_acesso_display': self.user.get_nivel_display_name(),
            'modulos_acesso': self.user.get_modulos_acesso(),
            'acesso_planejamento': self.user.acesso_planejamento,
            'acesso_contratos': self.user.acesso_contratos,
            'acesso_gerata': self.user.acesso_gerata,
            'acesso_empresas': self.user.acesso_empresas,
            'acesso_processo_sancionatorio': self.user.acesso_processo_sancionatorio,
            'acesso_controle_interno': self.user.acesso_controle_interno,
            'is_staff': self.user.is_staff,
            'is_active': self.user.is_active,
            'is_superuser': self.user.is_superuser,
            'uasg_centralizadora': uasg_centralizadora_data,
            'uasg_centralizada': uasg_centralizada_data,
            'controle_interno': bool(self.user.controle_interno),
        }
        
        return data
