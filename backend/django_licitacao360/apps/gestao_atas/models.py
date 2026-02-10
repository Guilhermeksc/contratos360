from django.db import models


class Ata(models.Model):
    """Ata de Registro de Preço"""
    numero_controle_pncp_ata = models.CharField("Número de Controle PNCP da Ata", max_length=100, primary_key=True)
    numero_ata_registro_preco = models.CharField("Número da Ata de Registro de Preço", max_length=100)
    ano_ata = models.IntegerField("Ano da Ata")
    numero_controle_pncp_compra = models.CharField("Número de Controle PNCP da Compra", max_length=100)
    cancelado = models.IntegerField("Cancelado", default=0)
    data_cancelamento = models.DateTimeField("Data de Cancelamento", null=True, blank=True)
    data_assinatura = models.DateTimeField("Data de Assinatura", null=True, blank=True)
    vigencia_inicio = models.DateTimeField("Vigência Início", null=True, blank=True)
    vigencia_fim = models.DateTimeField("Vigência Fim", null=True, blank=True)
    data_publicacao_pncp = models.DateTimeField("Data de Publicação no PNCP", null=True, blank=True)
    data_inclusao = models.DateTimeField("Data de Inclusão", null=True, blank=True)
    data_atualizacao = models.DateTimeField("Data de Atualização", null=True, blank=True)
    data_atualizacao_global = models.DateTimeField("Data de Atualização Global", null=True, blank=True)
    usuario = models.CharField("Usuário", max_length=255, blank=True)
    objeto_contratacao = models.TextField("Objeto da Contratação", blank=True)
    cnpj_orgao = models.CharField("CNPJ do Órgão", max_length=20, blank=True)
    nome_orgao = models.CharField("Nome do Órgão", max_length=255, blank=True)
    cnpj_orgao_subrogado = models.CharField("CNPJ do Órgão Subrogado", max_length=20, blank=True, null=True)
    nome_orgao_subrogado = models.CharField("Nome do Órgão Subrogado", max_length=255, blank=True, null=True)
    codigo_unidade_orgao = models.CharField("Código da Unidade do Órgão", max_length=50, blank=True)
    nome_unidade_orgao = models.CharField("Nome da Unidade do Órgão", max_length=255, blank=True)
    codigo_unidade_orgao_subrogado = models.CharField("Código da Unidade do Órgão Subrogado", max_length=50, blank=True, null=True)
    nome_unidade_orgao_subrogado = models.CharField("Nome da Unidade do Órgão Subrogado", max_length=255, blank=True, null=True)
    sequencial = models.CharField("Sequencial", max_length=50, blank=True)
    ano = models.IntegerField("Ano", null=True, blank=True)
    numero_compra = models.CharField("Número da Compra", max_length=100, blank=True)

    class Meta:
        verbose_name = "Ata"
        verbose_name_plural = "Atas"
        ordering = ["-ano_ata", "-data_assinatura"]

    def __str__(self):
        return f"{self.numero_ata_registro_preco}/{self.ano_ata} - {self.objeto_contratacao[:50] if self.objeto_contratacao else 'Sem objeto'}..."
