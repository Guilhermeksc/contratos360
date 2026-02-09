import re
from django.db import models


class InlabsArticle(models.Model):
    """Guarda matérias do INLABS filtradas pelo Comando da Marinha.
    
    Compatível com a tabela inlabs_articles do SQLite.
    """

    article_id = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    id_oficio = models.CharField(max_length=100, blank=True, null=True)
    pub_name = models.CharField(max_length=100, blank=True, null=True)
    art_type = models.CharField(max_length=100, blank=True, null=True)
    pub_date = models.CharField(max_length=32, db_index=True)
    nome_om = models.CharField(max_length=255, blank=True, null=True)
    number_page = models.CharField(max_length=255, blank=True, null=True)
    pdf_page = models.CharField(max_length=255, blank=True, null=True)
    edition_number = models.CharField(max_length=32, blank=True, null=True)
    highlight_type = models.CharField(max_length=64, blank=True, null=True)
    highlight_priority = models.CharField(max_length=64, blank=True, null=True)
    highlight = models.TextField(blank=True, null=True)
    highlight_image = models.CharField(max_length=255, blank=True, null=True)
    highlight_image_name = models.CharField(max_length=255, blank=True, null=True)
    materia_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    body_identifica = models.TextField(blank=True, null=True)
    uasg = models.CharField(max_length=64, blank=True, null=True)
    body_texto = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-pub_date", "article_id"]
        unique_together = ("article_id", "pub_date", "materia_id")
        verbose_name = "Matéria INLABS"
        verbose_name_plural = "Matérias INLABS"
        db_table = "inlabs_articles"

    def __str__(self) -> str:
        return f"{self.article_id} - {self.pub_date}"

    def extract_uasg(self) -> str | None:
        """Retorna o UASG extraído ou do campo uasg."""
        if self.uasg:
            return self.uasg
        
        # Tenta extrair do body_identifica se não estiver no campo uasg
        if self.body_identifica:
            uasg_match = re.search(r'\bUASG\s*(\d+)\b', self.body_identifica, re.IGNORECASE)
            if uasg_match:
                return uasg_match.group(1)
        
        return None

    def extract_om_name(self) -> str | None:
        """Retorna o nome da OM do campo nome_om."""
        return self.nome_om


class AvisoLicitacao(models.Model):
    """Avisos de Licitação extraídos dos artigos INLABS.
    
    Compatível com a tabela aviso_licitacao do SQLite.
    """

    article_id = models.CharField(max_length=64, unique=True, db_index=True)
    modalidade = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=64, blank=True, null=True)
    ano = models.CharField(max_length=4, blank=True, null=True)
    uasg = models.CharField(max_length=64, blank=True, null=True)
    processo = models.CharField(max_length=255, blank=True, null=True)
    objeto = models.TextField(blank=True, null=True)
    itens_licitados = models.CharField(max_length=255, blank=True, null=True)
    publicacao = models.CharField(max_length=255, blank=True, null=True)
    entrega_propostas = models.CharField(max_length=255, blank=True, null=True)
    abertura_propostas = models.CharField(max_length=255, blank=True, null=True)
    nome_responsavel = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Aviso de Licitação"
        verbose_name_plural = "Avisos de Licitação"
        db_table = "aviso_licitacao"

    def __str__(self) -> str:
        return f"{self.modalidade} Nº {self.numero}/{self.ano} - UASG {self.uasg}"

    @property
    def article(self):
        """Retorna o primeiro artigo relacionado (pode haver múltiplos com mesmo article_id)."""
        return InlabsArticle.objects.filter(article_id=self.article_id).first()


class Credenciamento(models.Model):
    """Credenciamentos extraídos dos artigos INLABS.
    
    Compatível com a tabela credenciamento do SQLite.
    """

    article_id = models.CharField(max_length=64, unique=True, db_index=True)
    tipo = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=64, blank=True, null=True)
    ano = models.CharField(max_length=4, blank=True, null=True)
    uasg = models.CharField(max_length=64, blank=True, null=True)
    processo = models.CharField(max_length=255, blank=True, null=True)
    tipo_processo = models.CharField(max_length=255, blank=True, null=True)
    numero_processo = models.CharField(max_length=64, blank=True, null=True)
    ano_processo = models.CharField(max_length=4, blank=True, null=True)
    contratante = models.CharField(max_length=255, blank=True, null=True)
    contratado = models.CharField(max_length=255, blank=True, null=True)
    objeto = models.TextField(blank=True, null=True)
    fundamento_legal = models.TextField(blank=True, null=True)
    vigencia = models.CharField(max_length=255, blank=True, null=True)
    valor_total = models.CharField(max_length=255, blank=True, null=True)
    data_assinatura = models.CharField(max_length=255, blank=True, null=True)
    nome_responsavel = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Credenciamento"
        verbose_name_plural = "Credenciamentos"
        db_table = "credenciamento"

    def __str__(self) -> str:
        return f"{self.tipo} Nº {self.numero}/{self.ano} - UASG {self.uasg}"

    @property
    def article(self):
        """Retorna o primeiro artigo relacionado (pode haver múltiplos com mesmo article_id)."""
        return InlabsArticle.objects.filter(article_id=self.article_id).first()
