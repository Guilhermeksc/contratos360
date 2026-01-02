from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django_licitacao360.apps.core.users.models import Usuario


class MateriaModel(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, verbose_name="ID")
    materia = models.CharField(max_length=100, unique=True, verbose_name="Matéria")
    
    class Meta:
        verbose_name = "Matéria"
        verbose_name_plural = "Matérias"
        ordering = ['materia']
    
    def __str__(self):
        return self.materia


class BibliografiaModel(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, verbose_name="ID")
    titulo = models.CharField(max_length=255, verbose_name="Título")
    autor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Autor")
    materia = models.ForeignKey(
        MateriaModel,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Matéria",
        related_name="bibliografias"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = "Bibliografia"
        verbose_name_plural = "Bibliografias"
        ordering = ['id']
    
    def __str__(self):
        parts = [self.titulo]
        if self.autor:
            parts.append(f"- {self.autor}")
        if self.materia:
            parts.append(f"({self.materia.materia})")
        return " ".join(parts)

class FlashCardsModel(models.Model):
    bibliografia = models.ForeignKey(
        BibliografiaModel, 
        on_delete=models.CASCADE, 
        verbose_name="Bibliografia",
        related_name="+"
    )
    pergunta = models.TextField(verbose_name="Pergunta")
    resposta = models.TextField(verbose_name="Resposta")
    assunto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Assunto")
    prova = models.BooleanField(default=False, verbose_name="Caiu em Prova")
    ano = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Ano da Prova",
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    caveira = models.BooleanField(default=False, verbose_name="Caveira")
    
    class Meta:
        verbose_name = "Flash Cards"
        verbose_name_plural = "Flash Cards"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.bibliografia.titulo} - {self.pergunta}"

class PerguntasBaseModel(models.Model):
    TIPO_CHOICES = [
        ('multipla', 'Múltipla Escolha'),
        ('vf', 'Verdadeiro ou Falso'),
        ('correlacao', 'Correlação'),
    ]
    
    bibliografia = models.ForeignKey(
        BibliografiaModel, 
        on_delete=models.CASCADE, 
        verbose_name="Bibliografia",
        related_name="+"
    )
    paginas = models.CharField(max_length=100, blank=True, null=True, verbose_name="Páginas")
    assunto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Assunto")
    caiu_em_prova = models.BooleanField(default=False, verbose_name="Caiu em Prova")
    ano_prova = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Ano da Prova",
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    pergunta = models.TextField(verbose_name="Pergunta")
    justificativa_resposta_certa = models.TextField(verbose_name="Justificativa da Resposta Correta")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Pergunta")
    
    class Meta:
        abstract = True
        ordering = ['id']
    
    def __str__(self):
        return f"{self.bibliografia.titulo} - {self.get_tipo_display()}"


class PerguntaMultiplaModel(PerguntasBaseModel):
    RESPOSTA_CHOICES = [
        ('a', 'Alternativa A'),
        ('b', 'Alternativa B'),
        ('c', 'Alternativa C'),
        ('d', 'Alternativa D'),
    ]
    
    alternativa_a = models.CharField(max_length=255, verbose_name="Alternativa A")
    alternativa_b = models.CharField(max_length=255, verbose_name="Alternativa B")
    alternativa_c = models.CharField(max_length=255, verbose_name="Alternativa C")
    alternativa_d = models.CharField(max_length=255, verbose_name="Alternativa D")
    resposta_correta = models.CharField(
        max_length=1, 
        choices=RESPOSTA_CHOICES, 
        verbose_name="Resposta Correta"
    )
    
    class Meta:
        verbose_name = "Pergunta Múltipla Escolha"
        verbose_name_plural = "Perguntas Múltipla Escolha"
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        self.tipo = 'multipla'
        super().save(*args, **kwargs)


class PerguntaVFModel(PerguntasBaseModel):
    afirmacao_verdadeira = models.TextField(verbose_name="Afirmação Verdadeira", blank=True, null=True)
    afirmacao_falsa = models.TextField(verbose_name="Afirmação Falsa", blank=True, null=True)
    
    class Meta:
        verbose_name = "Pergunta Verdadeiro ou Falso"
        verbose_name_plural = "Perguntas Verdadeiro ou Falso"
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        self.tipo = 'vf'
        super().save(*args, **kwargs)
    
    @property
    def resposta_correta(self):
        """A resposta correta é sempre True (Verdadeiro), pois a afirmacao_verdadeira é a correta"""
        return True


class PerguntaCorrelacaoModel(PerguntasBaseModel):
    coluna_a = models.JSONField(
        verbose_name="Coluna A (Lista de itens)",
        help_text="Lista de itens da coluna A em formato JSON. Ex: ['Item 1', 'Item 2', 'Item 3']"
    )
    coluna_b = models.JSONField(
        verbose_name="Coluna B (Lista de itens)",
        help_text="Lista de itens da coluna B em formato JSON. Ex: ['Item A', 'Item B', 'Item C']"
    )
    resposta_correta = models.JSONField(
        verbose_name="Resposta Correta (Pares corretos)",
        help_text="Pares corretos em formato JSON. Ex: {'0': '1', '1': '0', '2': '2'}"
    )
    
    class Meta:
        verbose_name = "Pergunta de Correlação"
        verbose_name_plural = "Perguntas de Correlação"
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        self.tipo = 'correlacao'
        super().save(*args, **kwargs)


class RespostaUsuario(models.Model):
    """
    Modelo para armazenar respostas dos usuários às questões
    """
    TIPO_CHOICES = [
        ('multipla', 'Múltipla Escolha'),
        ('vf', 'Verdadeiro ou Falso'),
        ('correlacao', 'Correlação'),
    ]
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='respostas',
        verbose_name="Usuário"
    )
    
    # Identificação da questão
    pergunta_id = models.IntegerField(verbose_name="ID da Pergunta")
    pergunta_tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo da Pergunta"
    )
    
    # Resposta do usuário (armazenada como JSON para flexibilidade)
    resposta_usuario = models.JSONField(verbose_name="Resposta do Usuário")
    
    # Resultado
    acertou = models.BooleanField(verbose_name="Acertou")
    
    # Metadados
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora da Resposta"
    )
    
    # Informações adicionais para estatísticas
    bibliografia_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID da Bibliografia"
    )
    assunto = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Assunto"
    )
    
    class Meta:
        verbose_name = "Resposta do Usuário"
        verbose_name_plural = "Respostas dos Usuários"
        ordering = ['-timestamp']
        # Índice composto para consultas eficientes
        indexes = [
            models.Index(fields=['usuario', 'pergunta_tipo', 'pergunta_id']),
            models.Index(fields=['usuario', 'acertou']),
            models.Index(fields=['usuario', 'timestamp']),
        ]
        # Evitar duplicatas: um usuário pode responder a mesma questão múltiplas vezes
        # Mas cada resposta deve ser registrada separadamente
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_pergunta_tipo_display()} #{self.pergunta_id} - {'✓' if self.acertou else '✗'}"


class QuestaoErradaAnonima(models.Model):
    """
    Modelo para armazenar questões erradas de forma anônima (sem informação do usuário)
    Usado para estatísticas gerais e ranking de matérias com mais erros
    """
    TIPO_CHOICES = [
        ('multipla', 'Múltipla Escolha'),
        ('vf', 'Verdadeiro ou Falso'),
        ('correlacao', 'Correlação'),
    ]
    
    # Identificação da questão
    pergunta_id = models.IntegerField(verbose_name="ID da Pergunta")
    pergunta_tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo da Pergunta"
    )
    
    # Informações para estatísticas
    bibliografia_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID da Bibliografia"
    )
    assunto = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Assunto"
    )
    
    # Metadados
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora do Erro"
    )
    
    class Meta:
        verbose_name = "Questão Errada Anônima"
        verbose_name_plural = "Questões Erradas Anônimas"
        ordering = ['-timestamp']
        # Índices para consultas eficientes
        indexes = [
            models.Index(fields=['pergunta_tipo', 'pergunta_id']),
            models.Index(fields=['bibliografia_id']),
            models.Index(fields=['assunto']),
            models.Index(fields=['timestamp']),
        ]
        # Evitar duplicatas: uma mesma questão pode ser registrada múltiplas vezes
        # (cada erro de cada usuário é registrado separadamente)
    
    def __str__(self):
        return f"Questão #{self.pergunta_id} ({self.get_pergunta_tipo_display()}) - Errada"
