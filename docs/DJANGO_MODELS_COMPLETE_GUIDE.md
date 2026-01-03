# Guia Completo de Modelagem Django - Migração PyQt6 → Django + PostgreSQL

Este documento fornece uma análise minuciosa da estrutura de dados do aplicativo PyQt6 (SQLite + JSON) para orientar a criação dos models Django/PostgreSQL. A análise foi baseada nos arquivos:

- `Contratos/model/models.py` (SQLAlchemy models)
- `Contratos/model/offline_db_model.py` (criação de tabelas SQLite)
- `Contratos/model/uasg_model.py` (lógica de negócio)
- `atas/model/atas_model.py` (models de atas)
- Arquivos JSON em `jsons/` (dados híbridos)

---

## 1. Arquitetura de Persistência Atual

### 1.1. Estrutura Híbrida SQLite + JSON

O sistema atual utiliza uma arquitetura híbrida:

**SQLite (`gerenciador_uasg.db`):**
- Tabelas principais: `uasgs`, `contratos`
- Tabelas de status: `status_contratos`, `registros_status`, `registro_mensagem`, `links_contratos`, `fiscalizacao`
- Tabelas offline (cache de APIs): `historico`, `empenhos`, `itens`, `arquivos`

**SQLite (`atas_controle.db`):**
- Tabelas principais: `atas`
- Tabelas de status: `status_atas`, `registros_atas`, `links_ata`, `fiscalizacao_atas`

**Arquivos JSON (`jsons/`):**
- `GERAL.json`: Exportação/importação de status de contratos
- `contratos_manuais.json`: Contratos criados manualmente
- `atas_principais-submend.json`: Dados principais de atas
- `atas_complementares-submend.json`: Status e registros de atas

### 1.2. Observações Importantes

1. **Campo `manual` em `contratos`**: Presente no ORM SQLAlchemy mas **não criado** pela função `_create_tables()` do `OfflineDBController`. Deve ser incluído no schema Django.

2. **Campo `termo_aditivo_edit` em `status_contratos`**: Presente no ORM mas **ausente** na criação SQL. Deve ser incluído.

3. **Tabela `fiscalizacao`**: Definida no ORM mas **não criada** por `_create_tables()`. Deve ser criada no Django.

4. **Índices**: O SQLite cria índices explícitos (`idx_*_contrato_id`) que devem ser replicados no PostgreSQL via `db_index=True` ou `Meta.indexes`.

---

## 2. Models Django - Domínio de Contratos

### 2.1. Uasg

**Tabela SQLite:** `uasgs`

```python
class Uasg(models.Model):
    uasg_code = models.CharField(max_length=10, primary_key=True, db_index=True)
    nome_resumido = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'uasgs'
        verbose_name = 'UASG'
        verbose_name_plural = 'UASGs'
        ordering = ['uasg_code']
```

**Observações:**
- Chave primária textual (código da UASG)
- Relacionamento 1:N com `Contrato` (cascade via Django)

---

### 2.2. Contrato

**Tabela SQLite:** `contratos`

```python
class Contrato(models.Model):
    id = models.CharField(max_length=255, primary_key=True, db_index=True)
    uasg = models.ForeignKey(
        'Uasg',
        on_delete=models.CASCADE,
        related_name='contratos',
        db_column='uasg_code',
        to_field='uasg_code'
    )
    
    # Identificadores administrativos
    numero = models.CharField(max_length=100, blank=True, null=True)
    licitacao_numero = models.CharField(max_length=100, blank=True, null=True)
    processo = models.CharField(max_length=100, blank=True, null=True)
    
    # Dados do fornecedor
    fornecedor_nome = models.CharField(max_length=255, blank=True, null=True)
    fornecedor_cnpj = models.CharField(max_length=20, blank=True, null=True)
    
    # Objeto e valores
    objeto = models.TextField(blank=True, null=True)
    valor_global = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Valor monetário do contrato"
    )
    
    # Vigência
    vigencia_inicio = models.DateField(blank=True, null=True)
    vigencia_fim = models.DateField(blank=True, null=True)
    
    # Classificações
    tipo = models.CharField(max_length=100, blank=True, null=True)
    modalidade = models.CharField(max_length=100, blank=True, null=True)
    
    # Dados do contratante
    contratante_orgao_unidade_gestora_codigo = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_column='contratante_orgao_unidade_gestora_codigo'
    )
    contratante_orgao_unidade_gestora_nome_resumido = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_column='contratante_orgao_unidade_gestora_nome_resumido'
    )
    
    # Flag manual (presente no ORM mas não criado no SQLite)
    manual = models.BooleanField(
        default=False,
        help_text="True se criado manualmente, False se importado da API"
    )
    
    # Snapshot do payload completo
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload completo do contrato da API ComprasNet"
    )
    
    # Campos de auditoria (novos no Django)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contratos'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        indexes = [
            models.Index(fields=['uasg', 'vigencia_fim']),
            models.Index(fields=['manual']),
            models.Index(fields=['vigencia_fim']),
        ]
        ordering = ['-vigencia_fim', 'numero']
```

**Observações:**
- `id` é string (vem da API pública)
- `valor_global` convertido de TEXT para `DecimalField`
- `vigencia_inicio` e `vigencia_fim` convertidos de TEXT para `DateField`
- Campo `manual` incluído (estava faltando no SQLite)
- `raw_json` convertido de TEXT para `JSONField` (PostgreSQL nativo)

---

### 2.3. StatusContrato

**Tabela SQLite:** `status_contratos`

```python
class StatusContrato(models.Model):
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='status',
        primary_key=True,
        db_column='contrato_id'
    )
    uasg_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Redundância para filtros rápidos"
    )
    status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='SEÇÃO CONTRATOS',
        help_text="Ex: ALERTA PRAZO, PORTARIA, PRORROGADO"
    )
    objeto_editado = models.TextField(
        blank=True,
        null=True,
        help_text="Objeto ajustado para exibição"
    )
    portaria_edit = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Valor exibido em interface"
    )
    termo_aditivo_edit = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Termo aditivo editado (presente no ORM mas ausente no SQLite)"
    )
    radio_options_json = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON com flags: Pode Renovar?, Custeio?, Natureza Continuada?, etc."
    )
    data_registro = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Timestamp textual no formato DD/MM/AAAA HH:MM:SS"
    )
    
    class Meta:
        db_table = 'status_contratos'
        verbose_name = 'Status do Contrato'
        verbose_name_plural = 'Status dos Contratos'
```

**Observações:**
- Relacionamento 1:1 com `Contrato`
- Campo `termo_aditivo_edit` incluído (estava faltando no SQLite)
- `radio_options_json` convertido de TEXT para `JSONField`
- `data_registro` mantido como string (formato específico do sistema)

---

### 2.4. RegistroStatus

**Tabela SQLite:** `registros_status`

```python
class RegistroStatus(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='registros_status',
        db_column='contrato_id',
        db_index=True
    )
    uasg_code = models.CharField(max_length=10, blank=True, null=True)
    texto = models.TextField(
        unique=True,
        help_text="Linha formatada: 'DD/MM/AAAA - mensagem - STATUS'"
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
```

**Observações:**
- `texto` tem `unique=True` no SQLite
- Índice em `contrato_id` replicado

---

### 2.5. RegistroMensagem

**Tabela SQLite:** `registro_mensagem`

```python
class RegistroMensagem(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='registros_mensagem',
        db_column='contrato_id',
        db_index=True
    )
    texto = models.TextField(
        unique=True,
        help_text="Mensagens soltas ligadas ao contrato"
    )
    
    class Meta:
        db_table = 'registro_mensagem'
        verbose_name = 'Registro de Mensagem'
        verbose_name_plural = 'Registros de Mensagem'
        indexes = [
            models.Index(fields=['contrato']),
        ]
```

**Observações:**
- `texto` tem `unique=True` no SQLite (opcional no código, mas aplicado)

---

### 2.6. LinksContrato

**Tabela SQLite:** `links_contratos`

```python
class LinksContrato(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='links',
        db_column='contrato_id',
        unique=True
    )
    link_contrato = models.URLField(max_length=500, blank=True, null=True)
    link_ta = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link do Termo Aditivo"
    )
    link_portaria = models.URLField(max_length=500, blank=True, null=True)
    link_pncp_espc = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link PNCP específico"
    )
    link_portal_marinha = models.URLField(max_length=500, blank=True, null=True)
    
    class Meta:
        db_table = 'links_contratos'
        verbose_name = 'Links do Contrato'
        verbose_name_plural = 'Links dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
```

**Observações:**
- Relacionamento 1:1 com `Contrato`
- Campos convertidos para `URLField` (validação automática)

---

### 2.7. FiscalizacaoContrato

**Tabela SQLite:** `fiscalizacao` (definida no ORM mas não criada no SQLite)

```python
class FiscalizacaoContrato(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='fiscalizacao',
        db_column='contrato_id',
        unique=True,
        db_index=True
    )
    
    # Responsáveis e substitutos
    gestor = models.CharField(max_length=255, blank=True, null=True)
    gestor_substituto = models.CharField(max_length=255, blank=True, null=True)
    fiscal_tecnico = models.CharField(max_length=255, blank=True, null=True)
    fiscal_tec_substituto = models.CharField(max_length=255, blank=True, null=True)
    fiscal_administrativo = models.CharField(max_length=255, blank=True, null=True)
    fiscal_admin_substituto = models.CharField(max_length=255, blank=True, null=True)
    
    observacoes = models.TextField(blank=True, null=True)
    
    # Timestamps (convertidos de string para DateTimeField)
    data_criacao = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Data de criação do registro"
    )
    data_atualizacao = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Última atualização"
    )
    
    class Meta:
        db_table = 'fiscalizacao'
        verbose_name = 'Fiscalização do Contrato'
        verbose_name_plural = 'Fiscalizações dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
```

**Observações:**
- Tabela não criada no SQLite atual, mas definida no ORM
- `data_criacao` e `data_atualizacao` convertidos de string para `DateTimeField`

---

## 3. Models Django - Dados Offline (Cache de APIs)

### 3.1. HistoricoContrato

**Tabela SQLite:** `historico`

```python
class HistoricoContrato(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='historicos',
        db_column='contrato_id',
        db_index=True
    )
    
    # Dados do histórico
    receita_despesa = models.CharField(max_length=50, blank=True, null=True)
    numero = models.CharField(max_length=100, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    ug = models.CharField(max_length=20, blank=True, null=True)
    gestao = models.CharField(max_length=50, blank=True, null=True)
    fornecedor_cnpj = models.CharField(max_length=20, blank=True, null=True)
    fornecedor_nome = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    processo = models.CharField(max_length=100, blank=True, null=True)
    objeto = models.TextField(blank=True, null=True)
    modalidade = models.CharField(max_length=100, blank=True, null=True)
    licitacao_numero = models.CharField(max_length=100, blank=True, null=True)
    
    # Datas (convertidas de string para DateField)
    data_assinatura = models.DateField(blank=True, null=True)
    data_publicacao = models.DateField(blank=True, null=True)
    vigencia_inicio = models.DateField(blank=True, null=True)
    vigencia_fim = models.DateField(blank=True, null=True)
    
    # Valor (convertido de string para DecimalField)
    valor_global = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Snapshot do payload
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de histórico"
    )
    
    class Meta:
        db_table = 'historico'
        verbose_name = 'Histórico do Contrato'
        verbose_name_plural = 'Históricos dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
```

---

### 3.2. Empenho

**Tabela SQLite:** `empenhos`

```python
class Empenho(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='empenhos',
        db_column='contrato_id',
        db_index=True
    )
    
    unidade_gestora = models.CharField(max_length=50, blank=True, null=True)
    gestao = models.CharField(max_length=50, blank=True, null=True)
    numero = models.CharField(max_length=100, blank=True, null=True)
    data_emissao = models.DateField(blank=True, null=True)
    credor_cnpj = models.CharField(max_length=20, blank=True, null=True)
    credor_nome = models.CharField(max_length=255, blank=True, null=True)
    
    # Valores monetários (convertidos de string para DecimalField)
    empenhado = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True
    )
    liquidado = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True
    )
    pago = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    informacao_complementar = models.TextField(blank=True, null=True)
    
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de empenhos"
    )
    
    class Meta:
        db_table = 'empenhos'
        verbose_name = 'Empenho'
        verbose_name_plural = 'Empenhos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
```

---

### 3.3. ItemContrato

**Tabela SQLite:** `itens`

```python
class ItemContrato(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='itens',
        db_column='contrato_id',
        db_index=True
    )
    
    # Classificadores
    tipo_id = models.CharField(max_length=50, blank=True, null=True)
    tipo_material = models.CharField(max_length=100, blank=True, null=True)
    grupo_id = models.CharField(max_length=50, blank=True, null=True)
    catmatseritem_id = models.CharField(max_length=50, blank=True, null=True)
    
    descricao_complementar = models.TextField(blank=True, null=True)
    
    # Quantidades e valores (convertidos de string para DecimalField)
    quantidade = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True
    )
    valorunitario = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True
    )
    valortotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    numero_item_compra = models.CharField(max_length=100, blank=True, null=True)
    
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de itens"
    )
    
    class Meta:
        db_table = 'itens'
        verbose_name = 'Item do Contrato'
        verbose_name_plural = 'Itens dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
```

---

### 3.4. ArquivoContrato

**Tabela SQLite:** `arquivos`

```python
class ArquivoContrato(models.Model):
    id = models.AutoField(primary_key=True)
    contrato = models.ForeignKey(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='arquivos',
        db_column='contrato_id',
        db_index=True
    )
    
    tipo = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    path_arquivo = models.CharField(max_length=500, blank=True, null=True)
    origem = models.CharField(max_length=100, blank=True, null=True)
    link_sei = models.URLField(max_length=500, blank=True, null=True)
    
    raw_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Payload integral da API de arquivos"
    )
    
    class Meta:
        db_table = 'arquivos'
        verbose_name = 'Arquivo do Contrato'
        verbose_name_plural = 'Arquivos dos Contratos'
        indexes = [
            models.Index(fields=['contrato']),
        ]
```

---

## 4. Models Django - Domínio de Atas

### 4.1. Ata

**Tabela SQLite:** `atas`

```python
class Ata(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    
    setor = models.CharField(max_length=100, blank=True, null=True)
    modalidade = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=50, blank=True, null=True)
    ano = models.CharField(max_length=4, blank=True, null=True)
    empresa = models.CharField(max_length=255, blank=True, null=True)
    
    contrato_ata_parecer = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Identificador único da ata (ex: 87000/24-088/00)"
    )
    
    objeto = models.TextField(blank=True, null=True)
    celebracao = models.DateField(blank=True, null=True)
    termino = models.DateField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    termo_aditivo = models.CharField(max_length=255, blank=True, null=True)
    portaria_fiscalizacao = models.CharField(max_length=255, blank=True, null=True)
    nup = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Número único de processo"
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'atas'
        verbose_name = 'Ata'
        verbose_name_plural = 'Atas'
        indexes = [
            models.Index(fields=['contrato_ata_parecer']),
            models.Index(fields=['termino']),
        ]
        ordering = ['-termino', 'contrato_ata_parecer']
```

---

### 4.2. StatusAta

**Tabela SQLite:** `status_atas`

```python
class StatusAta(models.Model):
    ata = models.OneToOneField(
        'Ata',
        on_delete=models.CASCADE,
        related_name='status_info',
        primary_key=True,
        db_column='ata_parecer',
        to_field='contrato_ata_parecer'
    )
    status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='SEÇÃO ATAS',
        help_text="Ex: ALERTA PRAZO, PORTARIA, PUBLICADO"
    )
    
    class Meta:
        db_table = 'status_atas'
        verbose_name = 'Status da Ata'
        verbose_name_plural = 'Status das Atas'
```

---

### 4.3. RegistroAta

**Tabela SQLite:** `registros_atas`

```python
class RegistroAta(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    ata = models.ForeignKey(
        'Ata',
        on_delete=models.CASCADE,
        related_name='registros',
        db_column='ata_parecer',
        to_field='contrato_ata_parecer'
    )
    texto = models.TextField(
        help_text="Registro cronológico da ata (formato: [DD/MM/AAAA] - mensagem)"
    )
    
    class Meta:
        db_table = 'registros_atas'
        verbose_name = 'Registro de Ata'
        verbose_name_plural = 'Registros de Atas'
        indexes = [
            models.Index(fields=['ata']),
        ]
```

---

### 4.4. LinksAta

**Tabela SQLite:** `links_ata`

```python
class LinksAta(models.Model):
    id = models.AutoField(primary_key=True)
    ata = models.OneToOneField(
        'Ata',
        on_delete=models.CASCADE,
        related_name='links',
        db_column='ata_parecer',
        to_field='contrato_ata_parecer',
        unique=True
    )
    serie_ata_link = models.URLField(max_length=500, blank=True, null=True)
    portaria_link = models.URLField(max_length=500, blank=True, null=True)
    ta_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link do Termo Aditivo"
    )
    portal_licitacoes_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Link do Portal de Licitações"
    )
    
    class Meta:
        db_table = 'links_ata'
        verbose_name = 'Links da Ata'
        verbose_name_plural = 'Links das Atas'
```

---

### 4.5. FiscalizacaoAta

**Tabela SQLite:** `fiscalizacao_atas`

```python
class FiscalizacaoAta(models.Model):
    id = models.AutoField(primary_key=True)
    ata = models.OneToOneField(
        'Ata',
        on_delete=models.CASCADE,
        related_name='fiscalizacao_info',
        db_column='ata_parecer',
        to_field='contrato_ata_parecer',
        unique=True,
        db_index=True
    )
    
    gestor = models.CharField(max_length=255, blank=True, null=True)
    gestor_substituto = models.CharField(max_length=255, blank=True, null=True)
    fiscal_tecnico = models.CharField(max_length=255, blank=True, null=True)
    fiscal_tec_substituto = models.CharField(max_length=255, blank=True, null=True)
    fiscal_administrativo = models.CharField(max_length=255, blank=True, null=True)
    fiscal_admin_substituto = models.CharField(max_length=255, blank=True, null=True)
    
    observacoes = models.TextField(blank=True, null=True)
    
    # Timestamps (convertidos de string para DateTimeField)
    data_criacao = models.DateTimeField(blank=True, null=True)
    data_atualizacao = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'fiscalizacao_atas'
        verbose_name = 'Fiscalização da Ata'
        verbose_name_plural = 'Fiscalizações das Atas'
        indexes = [
            models.Index(fields=['ata']),
        ]
```

---

## 5. Migração de Dados JSON para PostgreSQL

### 5.1. Contratos Manuais (`jsons/contratos_manuais.json`)

**Estrutura atual:**
- Lista de objetos com estrutura similar à API pública
- Campo `manual: true`
- Campos adicionais: `sigla_om_resp`, `orgao_responsavel`, `portaria`, `portaria_edit`
- `raw_json` simplificado

**Estratégia de migração:**
1. Criar script de migração que lê `contratos_manuais.json`
2. Para cada contrato:
   - Criar/atualizar registro em `Contrato` com `manual=True`
   - Salvar campos adicionais em `StatusContrato` ou criar tabela auxiliar `DadosManuaisContrato`
3. Manter compatibilidade: IDs manuais começam com `MANUAL-{uasg}-{numero}`

**Model sugerido para dados manuais:**

```python
class DadosManuaisContrato(models.Model):
    contrato = models.OneToOneField(
        'Contrato',
        on_delete=models.CASCADE,
        related_name='dados_manuais',
        primary_key=True
    )
    sigla_om_resp = models.CharField(max_length=50, blank=True, null=True)
    orgao_responsavel = models.CharField(max_length=255, blank=True, null=True)
    portaria = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contratos_manuais_criados'
    )
    
    class Meta:
        db_table = 'dados_manuais_contrato'
```

---

### 5.2. Status de Contratos (`jsons/GERAL.json`)

**Estrutura atual:**
- Lista de objetos com `contrato_id`, `uasg_code`, `status`, `objeto_editado`, `portaria_edit`, `termo_aditivo_edit`, `radio_options_json`, `data_registro`, `registros`, `registros_mensagem`, links e fiscalização

**Estratégia de migração:**
1. Script que lê `GERAL.json`
2. Para cada entrada:
   - Criar/atualizar `StatusContrato`
   - Criar/atualizar `LinksContrato`
   - Criar/atualizar `FiscalizacaoContrato`
   - Criar registros em `RegistroStatus` e `RegistroMensagem`
3. Validar `data_registro` antes de atualizar (lógica existente no código)

---

### 5.3. Atas (`jsons/atas_principais-submend.json` e `atas_complementares-submend.json`)

**Estrutura atual:**
- `atas_principais-submend.json`: Lista de atas principais
- `atas_complementares-submend.json`: Objeto com `status_atas`, `registros_atas`, `links_ata`, `fiscalizacao_atas`

**Estratégia de migração:**
1. Script que lê ambos os arquivos
2. Importar atas principais primeiro
3. Importar dados complementares (status, registros, links, fiscalização)
4. Validar `ata_parecer` antes de criar relacionamentos

---

## 6. Índices e Performance

### 6.1. Índices Obrigatórios (replicados do SQLite)

```python
# Em cada model relacionado a Contrato:
indexes = [
    models.Index(fields=['contrato']),
]

# Em Contrato:
indexes = [
    models.Index(fields=['uasg', 'vigencia_fim']),
    models.Index(fields=['manual']),
    models.Index(fields=['vigencia_fim']),
]

# Em Ata:
indexes = [
    models.Index(fields=['contrato_ata_parecer']),
    models.Index(fields=['termino']),
]
```

### 6.2. Índices Adicionais Recomendados

```python
# Para buscas por fornecedor:
indexes = [
    models.Index(fields=['fornecedor_cnpj']),
]

# Para buscas por processo:
indexes = [
    models.Index(fields=['processo']),
]

# Para ordenação por data:
indexes = [
    models.Index(fields=['-vigencia_fim', 'numero']),
]
```

---

## 7. Constraints e Validações

### 7.1. UniqueConstraints

```python
# Em RegistroStatus:
constraints = [
    models.UniqueConstraint(
        fields=['contrato', 'texto'],
        name='unique_registro_status_contrato_texto'
    )
]

# Em LinksContrato e FiscalizacaoContrato:
# Já garantido pelo OneToOneField com unique=True
```

### 7.2. Validações de Negócio

```python
# Em Contrato:
def clean(self):
    if self.vigencia_fim and self.vigencia_inicio:
        if self.vigencia_fim < self.vigencia_inicio:
            raise ValidationError("Data de fim não pode ser anterior à data de início")
    
    if self.manual and not self.numero:
        raise ValidationError("Contratos manuais devem ter número")
```

---

## 8. Relacionamentos e Cascade

### 8.1. Estratégia de Cascade

- **Uasg → Contrato**: `CASCADE` (deletar UASG deleta contratos)
- **Contrato → Status/Links/Fiscalizacao**: `CASCADE` (deletar contrato deleta dados relacionados)
- **Contrato → Historico/Empenhos/Itens/Arquivos**: `CASCADE` (dados offline)
- **Contrato → RegistroStatus/RegistroMensagem**: `CASCADE` (registros históricos)

### 8.2. Proteção de Dados Críticos

```python
# Uasg não deve ser deletada se houver contratos ativos
class Uasg(models.Model):
    # ...
    def delete(self, *args, **kwargs):
        if self.contratos.filter(vigencia_fim__gte=timezone.now().date()).exists():
            raise ProtectedError(
                "Não é possível deletar UASG com contratos ativos",
                self.contratos.filter(vigencia_fim__gte=timezone.now().date())
            )
        super().delete(*args, **kwargs)
```

---

## 9. Campos de Auditoria

Todos os models principais devem incluir:

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    related_name='%(class)s_criados'
)
updated_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    related_name='%(class)s_atualizados'
)
```

---

## 10. Considerações Finais

1. **Compatibilidade com dados existentes**: Manter IDs como string para compatibilidade com dados SQLite
2. **Migração incremental**: Criar scripts de migração que possam ser executados em etapas
3. **Validação de dados**: Validar formato de datas e valores monetários durante migração
4. **Backup**: Fazer backup completo do SQLite antes de migrar
5. **Testes**: Criar testes unitários para validar integridade dos dados migrados
6. **Documentação**: Documentar todas as transformações de dados (TEXT → DateField, TEXT → DecimalField, etc.)

---

## 11. Estrutura de Apps Django Sugerida

```
django_licitacao360/
├── apps/
│   ├── gestao_contratos/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── uasg.py
│   │   │   ├── contrato.py
│   │   │   ├── status.py
│   │   │   ├── links.py
│   │   │   ├── fiscalizacao.py
│   │   │   ├── historico.py
│   │   │   ├── empenho.py
│   │   │   ├── item.py
│   │   │   └── arquivo.py
│   │   ├── models/
│   │   │   └── ata.py (ou criar app separado gestao_atas)
│   │   ├── migrations/
│   │   ├── serializers/
│   │   ├── views/
│   │   ├── services/
│   │   │   └── ingestion.py (migração do OfflineDBController)
│   │   └── management/
│   │       └── commands/
│   │           ├── migrate_from_sqlite.py
│   │           └── sync_comprasnet.py
```

---

Este guia deve ser usado como referência completa para criar os models Django que replicam fielmente a estrutura do SQLite, incluindo todas as melhorias e correções identificadas na análise.

