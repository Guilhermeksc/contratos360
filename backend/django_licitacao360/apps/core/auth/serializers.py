from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django_licitacao360.apps.core.users.models import Usuario

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Campos adicionais no payload JWT:
        token['username'] = user.username
        token['perfil'] = user.perfil
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Adicionar dados do usuário na resposta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'perfil': self.user.perfil,
            'is_staff': self.user.is_staff,
            'is_active': self.user.is_active,
        }
        
        return data
