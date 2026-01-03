"""
Model para Arquivos de Contratos (dados offline)
"""

from django.db import models


class ArquivoContrato(models.Model):
    """
    Arquivo relacionado a um contrato (dados offline da API).
    Relacionamento N:1 com Contrato.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='arquivos',
        db_column='contrato_id',
        db_index=True,
        verbose_name="Contrato"
    )
    
    tipo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tipo"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição"
    )
    path_arquivo = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Caminho do Arquivo"
    )
    origem = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Origem"
    )
    link_sei = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Link SEI"
    )
    
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de arquivos",
        verbose_name="JSON Bruto"
    )
    
    class Meta:
        db_table = 'arquivos'
        verbose_name = 'Arquivo do Contrato'
        verbose_name_plural = 'Arquivos dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
    
    def __str__(self):
        return f"Arquivo {self.id} - {self.tipo or 'Sem tipo'} - Contrato {self.contrato_id}"

