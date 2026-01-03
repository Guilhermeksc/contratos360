"""
Model para Itens de Contratos (dados offline)
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ItemContrato(models.Model):
    """
    Item relacionado a um contrato (dados offline da API).
    Relacionamento N:1 com Contrato.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='itens',
        db_column='contrato_id',
        db_index=True,
        verbose_name="Contrato"
    )
    
    # Classificadores
    tipo_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="ID do Tipo"
    )
    tipo_material = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Tipo de Material"
    )
    grupo_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="ID do Grupo"
    )
    catmatseritem_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="ID CatMatSerItem"
    )
    
    descricao_complementar = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição Complementar"
    )
    
    # Quantidades e valores (convertidos de string para DecimalField)
    quantidade = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name="Quantidade"
    )
    valorunitario = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Unitário"
    )
    valortotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Total"
    )
    
    numero_item_compra = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número do Item na Compra"
    )
    
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de itens",
        verbose_name="JSON Bruto"
    )
    
    class Meta:
        db_table = 'itens'
        verbose_name = 'Item do Contrato'
        verbose_name_plural = 'Itens dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
    
    def __str__(self):
        return f"Item {self.numero_item_compra or self.id} - Contrato {self.contrato_id}"

