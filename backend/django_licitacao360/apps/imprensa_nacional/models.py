import re
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

    def extract_uasg(self) -> str | None:
        """Extrai o número UASG do campo Identifica ou do texto completo no body_html."""
        if not self.body_html:
            return None
        
        # Primeiro tenta buscar no campo <Identifica>
        identifica_match = re.search(r'<Identifica>.*?UASG\s+(\d+).*?</Identifica>', self.body_html, re.IGNORECASE | re.DOTALL)
        if identifica_match:
            return identifica_match.group(1)
        
        # Se não encontrou no Identifica, busca no texto completo
        # Procura por padrão "UASG" seguido de números (pode ter hífen antes)
        patterns = [
            r'UASG\s+(\d+)',
            r'UASG\s+(\d{6})',  # UASG geralmente tem 6 dígitos
            r'- UASG\s+(\d+)',  # Formato "- UASG 123456"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.body_html, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

    def extract_om_name(self) -> str | None:
        """Extrai o nome da OM do último segmento após '/' em art_category."""
        if not self.art_category:
            return None
        
        # Divide por '/' e pega o último segmento
        parts = [p.strip() for p in self.art_category.split('/') if p.strip()]
        if parts:
            return parts[-1]
        return None

    def extract_objeto(self) -> str | None:
        """Extrai o objeto do texto quando art_type é 'Aviso de Licitação-Pregão'."""
        if self.art_type != "Aviso de Licitação-Pregão":
            return None
        
        if not self.body_html:
            return None
        
        # Remove tags HTML e decodifica entidades HTML
        import html
        text = html.unescape(self.body_html)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)  # Normaliza espaços
        
        # Procura por padrões comuns de objeto em avisos de licitação
        # Exemplo: "Objeto: Contratação de empresa..." ou "Objeto: Aquisição..."
        # O padrão busca até encontrar "Total de Itens", "Edital", etc ou até dois pontos seguidos
        patterns = [
            r'Objeto[:\s]+([^\.]+?)(?:\.{1,2}\s|\.{1,2}$|Total de Itens|Edital|Entrega|Abertura|Informações|Fundamento|Vigência|Valor)',
            r'Objeto da Licitação[:\s]+([^\.]+?)(?:\.{1,2}\s|\.{1,2}$|Total de Itens|Edital|Entrega|Abertura|Informações|Fundamento|Vigência|Valor)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                objeto = match.group(1).strip()
                # Remove espaços extras e pontos no final
                objeto = re.sub(r'\s+', ' ', objeto)
                objeto = objeto.rstrip('.')
                # Limita o tamanho
                if len(objeto) > 200:
                    objeto = objeto[:200] + '...'
                return objeto if objeto else None
        
        return None
