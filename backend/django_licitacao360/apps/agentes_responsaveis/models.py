from django.db import models

class PostoGraduacao(models.Model):
    id_posto = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, verbose_name="Posto/Graduação")
    abreviatura = models.CharField(max_length=30, verbose_name="Abreviatura")

    class Meta:
        verbose_name = "Posto/Graduação"
        verbose_name_plural = "Postos/Graduações"
        db_table = 'postos_graduacao'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Especializacao(models.Model):
    id_especializacao = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, verbose_name="Especialização")
    abreviatura = models.CharField(max_length=30, verbose_name="Abreviatura")

    class Meta:
        verbose_name = "Especialização"
        verbose_name_plural = "Especializações"
        db_table = 'especializacoes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class AgenteResponsavelFuncao(models.Model):
    id_funcao = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, verbose_name="Função")

    class Meta:
        verbose_name = "Função de Agente Responsável"
        verbose_name_plural = "Funções de Agentes Responsáveis"
        db_table = 'agentes_responsaveis_funcao'

    def __str__(self):
        return self.nome


class AgenteResponsavel(models.Model):
    id_agente_responsavel = models.AutoField(primary_key=True)
    nome_de_guerra = models.CharField(max_length=100, verbose_name="Nome de Guerra")

    posto_graduacao = models.ForeignKey(
        PostoGraduacao,
        on_delete=models.PROTECT,
        related_name="agentes_responsaveis",
        verbose_name="Posto/Graduação",
    )

    especializacao = models.ForeignKey(
        Especializacao,
        on_delete=models.PROTECT,
        related_name="agentes_responsaveis",
        verbose_name="Especialização",
        blank=True,
        null=True,
    )

    departamento = models.CharField(max_length=100, verbose_name="Departamento", blank=True, null=True)
    divisao = models.CharField(max_length=100, verbose_name="Divisão", blank=True, null=True)

    os_funcao = models.CharField(max_length=50, verbose_name="OS Função", blank=True, null=True)
    os_qualificacao = models.CharField(max_length=20, verbose_name="OS Qualificação", blank=True, null=True)

    funcoes = models.ManyToManyField(
        AgenteResponsavelFuncao,
        related_name="agentes_responsaveis",
        verbose_name="Funções",
    )

    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Agente Responsável"
        verbose_name_plural = "Agentes Responsáveis"
        db_table = 'agentes_responsaveis'

    def __str__(self):
        return self.nome_de_guerra