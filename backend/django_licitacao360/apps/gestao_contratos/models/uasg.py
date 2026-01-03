"""
Model para UASG (Unidade Administrativa com Suporte Gerencial)
"""

from django.db import models


class Uasg(models.Model):
    """
    Representa uma UASG (Unidade Administrativa com Suporte Gerencial).
    Chave primária textual (código da UASG).
    """
    uasg_code = models.CharField(
        max_length=10,
        primary_key=True,
        db_index=True,
        verbose_name="Código UASG"
    )
    nome_resumido = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nome Resumido"
    )
    
    class Meta:
        db_table = 'uasgs'
        verbose_name = 'UASG'
        verbose_name_plural = 'UASGs'
        ordering = ['uasg_code']
    
    def __str__(self):
        return f"{self.uasg_code} - {self.nome_resumido or 'Sem nome'}"

