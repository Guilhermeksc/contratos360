"""
Views para UASG
"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Uasg
from ..serializers import UasgSerializer


class UasgViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para UASG (somente leitura)
    """
    queryset = Uasg.objects.all()
    serializer_class = UasgSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['uasg_code', 'nome_resumido']
    ordering_fields = ['uasg_code', 'nome_resumido']
    ordering = ['uasg_code']

