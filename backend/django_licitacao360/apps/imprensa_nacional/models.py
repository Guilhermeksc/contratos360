from django.db import models


class InlabsArticle(models.Model):
    """Guarda matérias do INLABS filtradas pelo Comando da Marinha."""

    article_id = models.CharField(max_length=64)
    edition_date = models.DateField(db_index=True)
    name = models.CharField(max_length=255, blank=True)
    id_oficio = models.CharField(max_length=100, blank=True)
    pub_name = models.CharField(max_length=100, blank=True)
    art_type = models.CharField(max_length=100, blank=True)
    pub_date = models.CharField(max_length=32, blank=True)
    art_class = models.CharField(max_length=255, blank=True)
    art_category = models.CharField(max_length=255, blank=True)
    art_notes = models.TextField(blank=True)
    pdf_page = models.CharField(max_length=255, blank=True)
    edition_number = models.CharField(max_length=32, blank=True)
    highlight_type = models.CharField(max_length=64, blank=True)
    highlight_priority = models.CharField(max_length=64, blank=True)
    highlight = models.TextField(blank=True)
    highlight_image = models.CharField(max_length=255, blank=True)
    highlight_image_name = models.CharField(max_length=255, blank=True)
    materia_id = models.CharField(max_length=64, blank=True)
    body_html = models.TextField(blank=True)
    source_filename = models.CharField(max_length=255, blank=True)
    source_zip = models.CharField(max_length=255, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-edition_date", "article_id"]
        unique_together = ("article_id", "edition_date")
        verbose_name = "Matéria INLABS"
        verbose_name_plural = "Matérias INLABS"

    def __str__(self) -> str:
        return f"{self.article_id} - {self.edition_date}"
