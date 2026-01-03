"""
Model para Links de Contratos
"""

from django.db import models


class LinksContrato(models.Model):
    """
    Links relacionados a um contrato.
    Relacionamento 1:1 com Contrato.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='links',
        db_column='contrato_id',
        unique=True,
        verbose_name="Contrato"
    )
    link_contrato = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Link do Contrato"
    )
    link_ta = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link do Termo Aditivo",
        verbose_name="Link do Termo Aditivo"
    )
    link_portaria = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Link da Portaria"
    )
    link_pncp_espc = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link PNCP específico",
        verbose_name="Link PNCP Específico"
    )
    link_portal_marinha = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Link Portal da Marinha"
    )
    
    class Meta:
        db_table = 'links_contratos'
        verbose_name = 'Links do Contrato'
        verbose_name_plural = 'Links dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
    
    def __str__(self):
        return f"Links - Contrato {self.contrato_id}"

