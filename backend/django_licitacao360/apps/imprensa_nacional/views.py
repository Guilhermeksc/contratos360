from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .models import InlabsArticle, AvisoLicitacao, Credenciamento
from .serializers import (
    InlabsArticleSerializer,
    AvisoLicitacaoSerializer,
    CredenciamentoSerializer,
)


class InlabsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para artigos INLABS."""

    queryset = InlabsArticle.objects.all().order_by("-pub_date", "article_id")
    serializer_class = InlabsArticleSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = [
        # pub_date removido - será filtrado manualmente no get_queryset para aceitar múltiplos formatos
        "article_id",
        "pub_name",
        "art_type",
        "uasg",
        "nome_om",
        "materia_id",
    ]
    search_fields = [
        "name",
        "nome_om",
        "body_identifica",
        "body_texto",
    ]
    ordering_fields = [
        "pub_date",
        "article_id",
        "pub_name",
    ]
    ordering = ("-pub_date", "article_id")

    def get_queryset(self):
        """Permite filtrar por UASG, nome_om e pub_date."""
        queryset = super().get_queryset()
        
        # Filtro opcional por UASG
        uasg = self.request.query_params.get("uasg", None)
        if uasg:
            queryset = queryset.filter(uasg=uasg)
        
        # Filtro opcional por nome_om
        nome_om = self.request.query_params.get("nome_om", None)
        if nome_om:
            queryset = queryset.filter(nome_om__icontains=nome_om)
        
        # Filtro por pub_date - aceita formato YYYY-MM-DD (formato padrão)
        # Todas as datas no banco devem estar em formato YYYY-MM-DD após normalização
        pub_date = self.request.query_params.get("pub_date", None)
        if pub_date:
            # Normaliza o parâmetro recebido para YYYY-MM-DD se necessário
            from datetime import datetime
            
            normalized_date = pub_date
            # Se receber em formato DD/MM/YYYY, converte para YYYY-MM-DD
            if len(pub_date) == 10 and pub_date.count('/') == 2:
                try:
                    date_obj = datetime.strptime(pub_date, "%d/%m/%Y")
                    normalized_date = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            
            # Busca exata no formato YYYY-MM-DD
            queryset = queryset.filter(pub_date=normalized_date)
        
        return queryset


class AvisoLicitacaoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para avisos de licitação."""

    queryset = AvisoLicitacao.objects.all()
    serializer_class = AvisoLicitacaoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = [
        "modalidade",
        "numero",
        "ano",
        "uasg",
        "processo",
    ]
    search_fields = [
        "objeto",
        "nome_responsavel",
        "processo",
        "article_id",
    ]
    ordering_fields = [
        "ano",
        "numero",
        "article_id",
    ]
    ordering = ("-ano", "-numero")


class CredenciamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para credenciamentos."""

    queryset = Credenciamento.objects.all()
    serializer_class = CredenciamentoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = [
        "tipo",
        "numero",
        "ano",
        "uasg",
        "processo",
        "contratante",
        "contratado",
    ]
    search_fields = [
        "objeto",
        "nome_responsavel",
        "processo",
        "contratante",
        "contratado",
    ]
    ordering_fields = [
        "ano",
        "numero",
    ]
    ordering = ("-ano", "-numero")
