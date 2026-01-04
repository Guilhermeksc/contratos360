from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .models import InlabsArticle
from .serializers import InlabsArticleSerializer


class InlabsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InlabsArticle.objects.all().order_by("-edition_date", "article_id")
    serializer_class = InlabsArticleSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = [
        "edition_date",
        "article_id",
        "pub_name",
        "art_type",
    ]
    search_fields = [
        "name",
        "art_category",
        "art_notes",
        "body_html",
    ]
    ordering_fields = [
        "edition_date",
        "article_id",
        "pub_name",
        "created_at",
    ]
    ordering = ("-edition_date", "article_id")
