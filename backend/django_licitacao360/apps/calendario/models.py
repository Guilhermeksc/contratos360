from django.db import models


class CalendarioEvento(models.Model):
    """Guarda eventos do calendário."""

    nome = models.CharField(max_length=255, verbose_name="Nome do Evento")
    data = models.DateField(verbose_name="Data do Evento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    cor = models.CharField(
        max_length=7,
        default="#3788d8",
        help_text="Cor do evento em formato hexadecimal (ex: #3788d8)",
        verbose_name="Cor"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        verbose_name = "Evento do Calendário"
        verbose_name_plural = "Eventos do Calendário"
        ordering = ["-data", "nome"]
        db_table = "calendario_evento"

    def __str__(self):
        return f"{self.nome} - {self.data}"
