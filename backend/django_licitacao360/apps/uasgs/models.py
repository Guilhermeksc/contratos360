"""Modelos de ComimSup e UASG disponíveis para múltiplos apps."""

from django.db import models


class ComimSup(models.Model):
    """Comando imediato superior vinculado a UASGs."""

    id = models.AutoField(primary_key=True)
    uasg = models.CharField(max_length=50, unique=True)
    sigla_comimsup = models.CharField(max_length=50)
    indicativo_comimsup = models.CharField(max_length=50)
    nome_comimsup = models.CharField(max_length=255)

    class Meta:
        db_table = 'comimsup'
        verbose_name = 'Comando Imediato Superior (ComImSup)'
        verbose_name_plural = 'Comando Imediato Superior (ComImSup)'
        ordering = ['sigla_comimsup']

    def __str__(self):
        return f"{self.sigla_comimsup} - {self.nome_comimsup}"


class Uasg(models.Model):
    """Organização militar/administrativa que referencia contratos e perfis."""

    id_uasg = models.IntegerField(primary_key=True)
    uasg = models.IntegerField(unique=True)
    nome_om = models.CharField(max_length=255, blank=True, null=True)
    indicativo_om = models.CharField(max_length=50, blank=True, null=True)
    sigla_om = models.CharField(max_length=50)
    uasg_centralizadora = models.BooleanField(default=False)
    uasg_centralizada = models.BooleanField(default=False)
    uf = models.CharField(max_length=2, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    classificacao = models.CharField(max_length=100, default='Nao informado')
    endereco = models.TextField(blank=True, null=True)
    cep = models.CharField(max_length=20, blank=True, null=True)
    secom = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=25, blank=True, null=True)
    ddi = models.CharField(max_length=20, blank=True, null=True)
    ddd = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=50, blank=True, null=True)
    intranet = models.CharField(max_length=255, blank=True, null=True)
    internet = models.CharField(max_length=255, blank=True, null=True)
    distrito = models.CharField(max_length=100, blank=True, null=True)
    ods = models.CharField(max_length=100, blank=True, null=True)
    situacao = models.BooleanField(default=True)
    ativa = models.BooleanField(default=True)

    comimsup = models.ForeignKey(
        ComimSup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinadas',
    )

    class Meta:
        db_table = 'organizacoes_militares'
        verbose_name = 'Organização Militar'
        verbose_name_plural = 'Organizações Militares'
        ordering = ['uasg']

    def __str__(self):
        nome = self.nome_om or 'Sem nome'
        return f"{self.sigla_om} - {nome}"

    @property
    def nome_resumido(self):
        """Compatibilidade com código legado que usava nome_resumido."""
        return self.nome_om

    @property
    def uasg_code(self):
        """Compatibilidade com referências antigas ao código textual."""
        return str(self.uasg)
