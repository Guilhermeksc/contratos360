"""
Model para Empenhos (dados offline)
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Empenho(models.Model):
    """
    Empenho relacionado a um contrato (dados offline da API).
    Relacionamento N:1 com Contrato.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='empenhos',
        db_column='contrato_id',
        db_index=True,
        verbose_name="Contrato"
    )
    
    unidade_gestora = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Unidade Gestora"
    )
    gestao = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Gestão"
    )
    numero = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número"
    )
    data_emissao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Emissão"
    )
    credor_cnpj = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="CNPJ do Credor"
    )
    credor_nome = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome do Credor"
    )
    
    # Valores monetários (convertidos de string para DecimalField)
    empenhado = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Empenhado"
    )
    liquidado = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Liquidado"
    )
    pago = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Pago"
    )
    
    informacao_complementar = models.TextField(
        blank=True,
        null=True,
        verbose_name="Informação Complementar"
    )
    
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de empenhos",
        verbose_name="JSON Bruto"
    )
    
    class Meta:
        db_table = 'empenhos'
        verbose_name = 'Empenho'
        verbose_name_plural = 'Empenhos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
    
    def __str__(self):
        return f"Empenho {self.numero or self.id} - Contrato {self.contrato_id}"

