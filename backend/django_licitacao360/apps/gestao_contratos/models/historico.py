"""
Model para Histórico de Contratos (dados offline)
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class HistoricoContrato(models.Model):
    """
    Histórico de um contrato (dados offline da API).
    Relacionamento N:1 com Contrato.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='historicos',
        db_column='contrato_id',
        db_index=True,
        verbose_name="Contrato"
    )
    
    # Dados do histórico
    receita_despesa = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Receita/Despesa"
    )
    numero = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número"
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observação"
    )
    ug = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="UG"
    )
    gestao = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Gestão"
    )
    fornecedor_cnpj = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="CNPJ do Fornecedor"
    )
    fornecedor_nome = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome do Fornecedor"
    )
    tipo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tipo"
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Categoria"
    )
    processo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Processo"
    )
    objeto = models.TextField(
        blank=True,
        null=True,
        verbose_name="Objeto"
    )
    modalidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Modalidade"
    )
    licitacao_numero = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número da Licitação"
    )
    
    # Datas (convertidas de string para DateField)
    data_assinatura = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Assinatura"
    )
    data_publicacao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Publicação"
    )
    vigencia_inicio = models.DateField(
        blank=True,
        null=True,
        verbose_name="Início da Vigência"
    )
    vigencia_fim = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fim da Vigência"
    )
    
    # Valor (convertido de string para DecimalField)
    valor_global = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Global"
    )
    
    # Snapshot do payload
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de histórico",
        verbose_name="JSON Bruto"
    )
    
    class Meta:
        db_table = 'historico'
        verbose_name = 'Histórico do Contrato'
        verbose_name_plural = 'Históricos dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
    
    def __str__(self):
        return f"Histórico {self.id} - Contrato {self.contrato_id}"

