"""
Model para Contrato
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Contrato(models.Model):
    """
    Representa um contrato administrativo.
    ID é string (vem da API pública do ComprasNet).
    """
    id = models.CharField(
        max_length=255,
        primary_key=True,
        db_index=True,
        verbose_name="ID do Contrato"
    )
    uasg = models.ForeignKey(
        'Uasg',
        on_delete=models.CASCADE,
        related_name='contratos',
        db_column='uasg_code',
        to_field='uasg_code',
        verbose_name="UASG"
    )
    
    # Identificadores administrativos
    numero = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número do Contrato"
    )
    licitacao_numero = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número da Licitação"
    )
    processo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Processo"
    )
    
    # Dados do fornecedor
    fornecedor_nome = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome do Fornecedor"
    )
    fornecedor_cnpj = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="CNPJ do Fornecedor"
    )
    
    # Objeto e valores
    objeto = models.TextField(
        blank=True,
        null=True,
        verbose_name="Objeto do Contrato"
    )
    valor_global = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Valor monetário do contrato",
        verbose_name="Valor Global"
    )
    
    # Vigência
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
    
    # Classificações
    tipo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tipo"
    )
    modalidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Modalidade"
    )
    
    # Dados do contratante
    contratante_orgao_unidade_gestora_codigo = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_column='contratante_orgao_unidade_gestora_codigo',
        verbose_name="Código UG do Contratante"
    )
    contratante_orgao_unidade_gestora_nome_resumido = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column='contratante_orgao_unidade_gestora_nome_resumido',
        verbose_name="Nome Resumido UG do Contratante"
    )
    
    # Flag manual (presente no ORM mas não criado no SQLite)
    manual = models.BooleanField(
        default=False,
        help_text="True se criado manualmente, False se importado da API",
        verbose_name="Contrato Manual"
    )
    
    # Snapshot do payload completo
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload completo do contrato da API ComprasNet",
        verbose_name="JSON Bruto"
    )
    
    # Campos de status de sincronização detalhada
    historico_atualizado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Histórico Atualizado Em",
        help_text="Data/hora da última sincronização do histórico"
    )
    empenhos_atualizados_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Empenhos Atualizados Em",
        help_text="Data/hora da última sincronização dos empenhos"
    )
    itens_atualizados_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Itens Atualizados Em",
        help_text="Data/hora da última sincronização dos itens"
    )
    arquivos_atualizados_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Arquivos Atualizados Em",
        help_text="Data/hora da última sincronização dos arquivos"
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        db_table = 'contratos'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        indexes = [
            models.Index(fields=['uasg', 'vigencia_fim']),
            models.Index(fields=['manual']),
            models.Index(fields=['vigencia_fim']),
            models.Index(fields=['fornecedor_cnpj']),
            models.Index(fields=['processo']),
        ]
        ordering = ['-vigencia_fim', 'numero']
    
    def clean(self):
        """Validações de negócio"""
        from django.core.exceptions import ValidationError
        
        if self.vigencia_fim and self.vigencia_inicio:
            if self.vigencia_fim < self.vigencia_inicio:
                raise ValidationError({
                    'vigencia_fim': 'Data de fim não pode ser anterior à data de início'
                })
        
        if self.manual and not self.numero:
            raise ValidationError({
                'numero': 'Contratos manuais devem ter número'
            })
    
    def __str__(self):
        return f"{self.numero or self.id} - {self.fornecedor_nome or 'Sem fornecedor'}"

