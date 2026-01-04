from django.contrib import admin

from .models import InlabsArticle


@admin.register(InlabsArticle)
class InlabsArticleAdmin(admin.ModelAdmin):
    list_display = ("article_id", "edition_date", "name", "pub_name")
    search_fields = ("article_id", "name", "art_category", "materia_id")
    list_filter = ("edition_date", "pub_name")
    ordering = ("-edition_date", "article_id")
    readonly_fields = ("created_at", "updated_at")
