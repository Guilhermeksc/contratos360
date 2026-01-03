"""
Model para Dados Manuais de Contratos
"""

from django.conf import settings
from django.db import models


class DadosManuaisContrato(models.Model):
    """
    Dados adicionais para contratos criados manualmente.
    Relacionamento 1:1 com Contrato.
    """
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='dados_manuais',
        primary_key=True,
        verbose_name="Contrato"
    )
    sigla_om_resp = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Sigla OM Responsável"
    )
    orgao_responsavel = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Órgão Responsável"
    )
    portaria = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Portaria"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contratos_manuais_criados',
        verbose_name="Criado Por"
    )
    
    class Meta:
        db_table = 'dados_manuais_contrato'
        verbose_name = 'Dados Manuais do Contrato'
        verbose_name_plural = 'Dados Manuais dos Contratos'
    
    def __str__(self):
        return f"Dados Manuais - Contrato {self.contrato_id}"

