"""
Serializers para UASG
"""

from rest_framework import serializers
from ..models import Uasg


class UasgSerializer(serializers.ModelSerializer):
    """Serializer para UASG"""
    
    class Meta:
        model = Uasg
        fields = ['uasg_code', 'nome_resumido']
        read_only_fields = ['uasg_code']

