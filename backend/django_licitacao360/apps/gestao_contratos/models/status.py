"""
Models para Status de Contratos
"""

from django.db import models


class StatusContrato(models.Model):
    """
    Status e informações editadas de um contrato.
    Relacionamento 1:1 com Contrato.
    """
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='status',
        primary_key=True,
        db_column='contrato_id',
        verbose_name="Contrato"
    )
    uasg_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Redundância para filtros rápidos",
        verbose_name="Código UASG"
    )
    status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='SEÇÃO CONTRATOS',
        help_text="Ex: ALERTA PRAZO, PORTARIA, PRORROGADO",
        verbose_name="Status"
    )
    objeto_editado = models.TextField(
        blank=True,
        null=True,
        help_text="Objeto ajustado para exibição",
        verbose_name="Objeto Editado"
    )
    portaria_edit = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Valor exibido em interface",
        verbose_name="Portaria Editada"
    )
    termo_aditivo_edit = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Termo aditivo editado (presente no ORM mas ausente no SQLite)",
        verbose_name="Termo Aditivo Editado"
    )
    radio_options_json = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON com flags: Pode Renovar?, Custeio?, Natureza Continuada?, etc.",
        verbose_name="Opções de Radio (JSON)"
    )
    data_registro = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Timestamp textual no formato DD/MM/AAAA HH:MM:SS",
        verbose_name="Data de Registro"
    )
    
    class Meta:
        db_table = 'status_contratos'
        verbose_name = 'Status do Contrato'
        verbose_name_plural = 'Status dos Contratos'
    
    def __str__(self):
        return f"Status {self.status} - Contrato {self.contrato_id}"


class RegistroStatus(models.Model):
    """
    Registros cronológicos de status de um contrato.
    Relacionamento N:1 com Contrato.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='registros_status',
        db_column='contrato_id',
        db_index=True,
        verbose_name="Contrato"
    )
    uasg_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Código UASG"
    )
    texto = models.TextField(
        unique=True,
        help_text="Linha formatada: 'DD/MM/AAAA - mensagem - STATUS'",
        verbose_name="Texto do Registro"
    )
    
    class Meta:
        db_table = 'registros_status'
        verbose_name = 'Registro de Status'
        verbose_name_plural = 'Registros de Status'
        indexes = [
            models.Index(fields=['contrato']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['contrato', 'texto'],
                name='unique_registro_status_contrato_texto'
            )
        ]
    
    def __str__(self):
        return f"Registro {self.id} - {self.texto[:50]}..."


class RegistroMensagem(models.Model):
    """
    Mensagens soltas ligadas a um contrato.
    Relacionamento N:1 com Contrato.
    """
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='registros_mensagem',
        db_column='contrato_id',
        db_index=True,
        verbose_name="Contrato"
    )
    texto = models.TextField(
        unique=True,
        help_text="Mensagens soltas ligadas ao contrato",
        verbose_name="Texto da Mensagem"
    )
    
    class Meta:
        db_table = 'registro_mensagem'
        verbose_name = 'Registro de Mensagem'
        verbose_name_plural = 'Registros de Mensagem'
        indexes = [
            models.Index(fields=['contrato']),
        ]
    
    def __str__(self):
        return f"Mensagem {self.id} - {self.texto[:50]}..."

