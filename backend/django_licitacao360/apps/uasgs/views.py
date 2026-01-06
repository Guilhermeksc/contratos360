"""ViewSets reutilizáveis para ComimSup e UASGs."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import ComimSup, Uasg
from .serializers import ComimSupSerializer, UasgSerializer


class ComimSupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ComimSup.objects.all()
    serializer_class = ComimSupSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['sigla_comimsup', 'nome_comimsup', 'uasg']
    ordering_fields = ['sigla_comimsup', 'nome_comimsup', 'uasg']
    ordering = ['sigla_comimsup']


class UasgViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Uasg.objects.select_related('comimsup').all()
    serializer_class = UasgSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['uf', 'uasg_centralizadora', 'uasg_centralizada', 'comimsup']
    search_fields = ['uasg', 'sigla_om', 'nome_om', 'cidade', 'bairro']
    ordering_fields = ['uasg', 'sigla_om', 'nome_om']
    ordering = ['uasg']
    pagination_class = None  # Desabilita paginação para retornar todas as UASGs
