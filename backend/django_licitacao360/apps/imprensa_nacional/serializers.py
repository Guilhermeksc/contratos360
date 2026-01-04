from rest_framework import serializers

from .models import InlabsArticle


class InlabsArticleSerializer(serializers.ModelSerializer):
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
            "created_at",
            "updated_at",
        ]
