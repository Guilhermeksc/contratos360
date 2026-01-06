from rest_framework import serializers

from .models import InlabsArticle


class InlabsArticleSerializer(serializers.ModelSerializer):
    uasg = serializers.SerializerMethodField()
    om_name = serializers.SerializerMethodField()
    objeto = serializers.SerializerMethodField()

    class Meta:
        model = InlabsArticle
        fields = [
            "id",
            "article_id",
            "edition_date",
            "name",
            "id_oficio",
            "pub_name",
            "art_type",
            "pub_date",
            "art_class",
            "art_category",
            "art_notes",
            "pdf_page",
            "edition_number",
            "highlight_type",
            "highlight_priority",
            "highlight",
            "highlight_image",
            "highlight_image_name",
            "materia_id",
            "body_html",
            "source_filename",
            "source_zip",
            "raw_payload",
            "uasg",
            "om_name",
            "objeto",
            "created_at",
            "updated_at",
        ]

    def get_uasg(self, obj) -> str | None:
        """Extrai o número UASG do body_html."""
        return obj.extract_uasg()

    def get_om_name(self, obj) -> str | None:
        """Extrai o nome da OM da categoria."""
        return obj.extract_om_name()

    def get_objeto(self, obj) -> str | None:
        """Extrai o objeto quando for Aviso de Licitação-Pregão."""
        return obj.extract_objeto()
