from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny

from .models import EmpresasSancionadas
from .serializers import EmpresasSancionadasSerializer


class EmpresasSancionadasViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmpresasSancionadas.objects.all().order_by("-data_inicio_sancao", "codigo_sancao")
    serializer_class = EmpresasSancionadasSerializer
    permission_classes = [AllowAny]  # Temporário para debug
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = [
        "tipo_pessoa",
        "categoria_sancao",
        "esfera_orgao_sancionador",
        "uf_orgao_sancionador",
        "data_inicio_sancao",
        "data_final_sancao",
        "cpf_cnpj",
    ]
    search_fields = [
        "nome_sancionado",
        "cpf_cnpj",
        "codigo_sancao",
        "razao_social",
        "nome_fantasia",
        "numero_processo",
        "orgao_sancionador",
    ]
    ordering_fields = [
        "data_inicio_sancao",
        "data_final_sancao",
        "nome_sancionado",
        "codigo_sancao",
        "created_at",
    ]
    ordering = ("-data_inicio_sancao", "codigo_sancao")
