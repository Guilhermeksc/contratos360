from django.db import models


class EmpresasSancionadas(models.Model):
    """Cadastro de Empresas Inidôneas e Suspensas (CEIS)."""

    # Campos principais
    cadastro = models.CharField(max_length=50, blank=True, help_text="Tipo de cadastro (ex: CEIS)")
    codigo_sancao = models.CharField(max_length=50, db_index=True, help_text="Código único da sanção")
    tipo_pessoa = models.CharField(
        max_length=1,
        choices=[("F", "Física"), ("J", "Jurídica")],
        blank=True,
        help_text="Tipo de pessoa: F=Física, J=Jurídica"
    )
    cpf_cnpj = models.CharField(max_length=18, db_index=True, blank=True, help_text="CPF ou CNPJ do sancionado")
    nome_sancionado = models.CharField(max_length=500, blank=True, help_text="Nome do sancionado")
    nome_orgao_sancionador = models.CharField(
        max_length=500,
        blank=True,
        help_text="Nome informado pelo órgão sancionador"
    )
    razao_social = models.CharField(max_length=500, blank=True, help_text="Razão Social - Cadastro Receita")
    nome_fantasia = models.CharField(max_length=500, blank=True, help_text="Nome Fantasia - Cadastro Receita")
    numero_processo = models.CharField(max_length=100, blank=True, help_text="Número do processo")
    categoria_sancao = models.CharField(max_length=500, blank=True, help_text="Categoria da sanção")
    
    # Datas
    data_inicio_sancao = models.DateField(null=True, blank=True, db_index=True, help_text="Data início da sanção")
    data_final_sancao = models.DateField(null=True, blank=True, db_index=True, help_text="Data final da sanção")
    data_publicacao = models.DateField(null=True, blank=True, help_text="Data de publicação")
    data_transito_julgado = models.DateField(null=True, blank=True, help_text="Data do trânsito em julgado")
    data_origem_informacao = models.DateField(null=True, blank=True, help_text="Data origem informação")
    
    # Publicação
    publicacao = models.CharField(max_length=500, blank=True, help_text="Publicação")
    detalhamento_meio_publicacao = models.TextField(blank=True, help_text="Detalhamento do meio de publicação")
    
    # Órgão sancionador
    abrangencia_sancao = models.CharField(max_length=500, blank=True, help_text="Abrangência da sanção")
    orgao_sancionador = models.CharField(max_length=500, blank=True, help_text="Órgão sancionador")
    uf_orgao_sancionador = models.CharField(max_length=2, blank=True, help_text="UF do órgão sancionador")
    esfera_orgao_sancionador = models.CharField(max_length=100, blank=True, help_text="Esfera do órgão sancionador")
    
    # Informações adicionais
    fundamentacao_legal = models.TextField(blank=True, help_text="Fundamentação legal")
    origem_informacoes = models.CharField(max_length=500, blank=True, help_text="Origem das informações")
    observacoes = models.TextField(blank=True, help_text="Observações")
    
    # Campos de controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_inicio_sancao", "codigo_sancao"]
        unique_together = ("codigo_sancao",)
        verbose_name = "Empresa Sancionada"
        verbose_name_plural = "Empresas Sancionadas"
        indexes = [
            models.Index(fields=["cpf_cnpj"]),
            models.Index(fields=["nome_sancionado"]),
            models.Index(fields=["data_final_sancao"]),
        ]

    def __str__(self) -> str:
        return f"{self.nome_sancionado or self.cpf_cnpj} - {self.codigo_sancao}"
