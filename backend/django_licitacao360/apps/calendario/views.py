from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CalendarioEvento
from .serializers import CalendarioEventoSerializer


class CalendarioEventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar eventos do calendário.
    Permite CRUD completo de eventos.
    """
    queryset = CalendarioEvento.objects.all()
    serializer_class = CalendarioEventoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = [
        "data",
        "nome",
    ]
    search_fields = [
        "nome",
        "descricao",
    ]
    ordering_fields = [
        "data",
        "nome",
        "created_at",
    ]
    ordering = ["-data", "nome"]

    @action(detail=False, methods=["get"])
    def por_mes(self, request):
        """
        Retorna eventos filtrados por mês e ano.
        Query params: ano (YYYY), mes (MM)
        """
        ano = request.query_params.get("ano")
        mes = request.query_params.get("mes")
        
        queryset = self.get_queryset()
        
        if ano and mes:
            try:
                ano_int = int(ano)
                mes_int = int(mes)
                # Filtra eventos do mês/ano especificado
                queryset = queryset.filter(
                    data__year=ano_int,
                    data__month=mes_int
                )
            except ValueError:
                pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
