"""
Model para Fiscalização de Contratos
"""

from django.db import models


class FiscalizacaoContrato(models.Model):
    """
    Dados de fiscalização de um contrato.
    Relacionamento 1:1 com Contrato.
    Tabela definida no ORM mas não criada no SQLite atual.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='fiscalizacao',
        db_column='contrato_id',
        unique=True,
        db_index=True,
        verbose_name="Contrato"
    )
    
    # Responsáveis e substitutos
    gestor = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Gestor"
    )
    gestor_substituto = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Gestor Substituto"
    )
    fiscal_tecnico = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Fiscal Técnico"
    )
    fiscal_tec_substituto = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Fiscal Técnico Substituto"
    )
    fiscal_administrativo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Fiscal Administrativo"
    )
    fiscal_admin_substituto = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Fiscal Administrativo Substituto"
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    # Timestamps (convertidos de string para DateTimeField)
    data_criacao = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Data de criação do registro",
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Última atualização",
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        db_table = 'fiscalizacao'
        verbose_name = 'Fiscalização do Contrato'
        verbose_name_plural = 'Fiscalizações dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
    
    def __str__(self):
        return f"Fiscalização - Contrato {self.contrato_id}"

