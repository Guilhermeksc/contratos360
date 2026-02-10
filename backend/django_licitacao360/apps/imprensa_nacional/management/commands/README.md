# Comandos de Management - Imprensa Nacional (INLABS)

Este documento descreve todos os comandos de management disponíveis para o app `imprensa_nacional`, que gerencia a importação e processamento de artigos do INLABS (Imprensa Nacional).

## Índice

- [Comandos Disponíveis](#comandos-disponíveis)
  - [import_inlabs](#import_inlabs)
  - [import_inlabs_batch](#import_inlabs_batch)
  - [load_inlabs_data](#load_inlabs_data)
  - [export_inlabs_to_sqlite](#export_inlabs_to_sqlite)
  - [sync_celery_beat](#sync_celery_beat)
- [Fluxos de Uso](#fluxos-de-uso)
- [Troubleshooting](#troubleshooting)

---

## Comandos Disponíveis

### import_inlabs

**Descrição:** Baixa e salva artigos do INLABS para uma data específica ou a data atual.

**Uso:**
```bash
python manage.py import_inlabs [--date YYYY-MM-DD]
```

**Parâmetros:**
- `--date` (opcional): Data no formato `YYYY-MM-DD` da edição do INLABS a importar. Se omitido, usa a data atual.

**Exemplos:**
```bash
# Importar artigos da data atual
python manage.py import_inlabs

# Importar artigos de uma data específica
python manage.py import_inlabs --date 2025-02-08
```

**Comportamento:**
- Baixa o arquivo ZIP do INLABS para a data especificada
- Extrai e processa os XMLs dos artigos
- Filtra artigos relacionados ao "Comando da Marinha"
- Salva os artigos no banco de dados PostgreSQL
- Retorna estatísticas sobre a importação

**Saída esperada:**
```
Iniciando importação do INLABS para 2025-02-08...
Importação concluída: arquivo=S03022025.zip artigos=150
```

---

### import_inlabs_batch

**Descrição:** Importa artigos do INLABS para um intervalo de datas ou uma lista específica de datas.

**Uso:**
```bash
python manage.py import_inlabs_batch --start-date YYYY-MM-DD [opções]
```

**Parâmetros:**
- `--start-date` (obrigatório): Data inicial do intervalo no formato `YYYY-MM-DD`
- `--end-date` (opcional): Data final do intervalo. Se omitido, usa a data atual
- `--dates` (opcional): Lista específica de datas para importar (sobrescreve start-date e end-date)
- `--skip-existing`: Pula datas que já possuem artigos no banco de dados
- `--delay`: Delay em segundos entre cada importação (padrão: 2)
- `--continue-on-error`: Continua importação mesmo quando ocorre erro em uma data

**Exemplos:**
```bash
# Importar intervalo de datas
docker compose exec backend python manage.py import_inlabs_batch --start-date 2026-02-02 --end-date 2026-02-06

# Importar até a data atual
python manage.py import_inlabs_batch --start-date 2025-01-01

# Importar lista específica de datas
docker compose exec backend python manage.py import_inlabs_batch --dates 2026-02-02 2026-02-03 2026-02-04 2026-02-05 2026-02-06 2026-02-09

# Pular datas que já têm artigos
python manage.py import_inlabs_batch --start-date 2025-01-01 --skip-existing

# Continuar mesmo com erros
python manage.py import_inlabs_batch --start-date 2025-01-01 --continue-on-error

# Ajustar delay entre importações
python manage.py import_inlabs_batch --start-date 2025-01-01 --delay 5
```

**Comportamento:**
- Processa cada data sequencialmente
- Mostra progresso em tempo real (`[1/30] Processando 2025-01-01...`)
- Aplica delay entre importações para evitar sobrecarga
- Gera relatório final com estatísticas

**Saída esperada:**
```
Iniciando importação em lote: 30 datas
Intervalo: 2025-01-01 até 2025-01-30

[1/30] Processando 2025-01-01...
✅ 2025-01-01: 150 artigos salvos

...

============================================================
RESUMO DA IMPORTAÇÃO EM LOTE
============================================================
Total de datas processadas: 30
✅ Sucessos: 28
⚠  Puladas (arquivo não disponível): 2
❌ Erros: 0
📊 Total de artigos salvos: 4200
```

---

### load_inlabs_data

**Descrição:** Carrega dados do arquivo SQLite (`inlabs_articles.db`) para o banco de dados PostgreSQL.

**Uso:**
```bash
python manage.py load_inlabs_data [opções]
```

**Parâmetros:**
- `--db-path` (opcional): Caminho para o arquivo SQLite. Padrão: `apps/imprensa_nacional/fixtures/inlabs_articles.db`
- `--dry-run`: Executa sem salvar no banco (apenas valida)
- `--batch-size`: Tamanho do lote para inserção em batch (padrão: 1000)
- `--table`: Tabela específica para carregar (`all`, `articles`, `avisos`, `credenciamentos`). Padrão: `all`

**Exemplos:**
```bash
# Carregar todas as tabelas
docker compose exec backend python manage.py load_inlabs_data

# Carregar apenas artigos
docker compose exec backend python manage.py load_inlabs_data --table articles

# Carregar apenas avisos de licitação
docker compose exec backend python manage.py load_inlabs_data --table avisos

# Carregar apenas credenciamentos
docker compose exec backend python manage.py load_inlabs_data --table credenciamentos

# Modo dry-run (validação sem salvar)
docker compose exec backend python manage.py load_inlabs_data --dry-run

# Especificar caminho customizado
docker compose exec backend python manage.py load_inlabs_data --db-path /caminho/para/inlabs_articles.db

# Ajustar tamanho do lote
docker compose exec backend python manage.py load_inlabs_data --batch-size 500
```

**Comportamento:**
- Conecta ao arquivo SQLite especificado
- Carrega dados das tabelas: `inlabs_articles`, `aviso_licitacao`, `credenciamento`
- Processa em lotes para melhor performance
- Usa `update_or_create` para evitar duplicatas
- Trunca campos automaticamente se excederem o tamanho máximo
- Executa dentro de uma transação para garantir consistência

**Saída esperada:**
```
Conectando ao SQLite: /path/to/inlabs_articles.db
Migrando artigos INLABS...
  ✓ Migrados 89674 artigos
Migrando avisos de licitação...
  ✓ Migrados 12548 avisos de licitação
Migrando credenciamentos...
  ✓ Migrados 2403 credenciamentos

✅ Migração concluída com sucesso!
  Artigos: 89674
  Avisos de Licitação: 12548
  Credenciamentos: 2403
```

**Nota:** Este comando é útil para migrar dados de um banco SQLite existente (gerado pelo script `zip_xml_to_sqlite.py`) para o PostgreSQL.

---

### export_inlabs_to_sqlite

**Descrição:** Exporta todos os dados do modelo `InlabsArticle` para um arquivo SQLite.

**Uso:**
```bash
python manage.py export_inlabs_to_sqlite [opções]
```

**Parâmetros:**
- `--output`: Caminho do arquivo SQLite de saída (padrão: `inlabs_articles.db`)
- `--overwrite`: Sobrescreve o arquivo SQLite se ele já existir

**Exemplos:**
```bash
# Exportar para arquivo padrão
python manage.py export_inlabs_to_sqlite

# Exportar para caminho específico
python manage.py export_inlabs_to_sqlite --output /backup/inlabs_backup.db

# Sobrescrever arquivo existente
python manage.py export_inlabs_to_sqlite --output backup.db --overwrite
```

**Comportamento:**
- Cria arquivo SQLite com a estrutura da tabela `inlabs_articles`
- Exporta todos os registros do modelo `InlabsArticle`
- Processa em lotes de 1000 registros
- Cria índices para melhorar performance de consultas
- Preserva todos os campos, incluindo campos de texto longo

**Saída esperada:**
```
Criando estrutura da tabela...
Buscando artigos do banco de dados...
Encontrados 89674 artigos. Exportando...
  Exportados 1000/89674 artigos...
  Exportados 2000/89674 artigos...
...
Criando índices...

✅ Exportação concluída com sucesso!
   Arquivo: /path/to/inlabs_articles.db
   Total de artigos exportados: 89674
```

**Nota:** Este comando é útil para fazer backup dos dados ou migrar para outro ambiente.

---

### sync_celery_beat

**Descrição:** Sincroniza tarefas periódicas do `CELERY_BEAT_SCHEDULE` para o banco de dados.

**Uso:**
```bash
python manage.py sync_celery_beat
```

**Parâmetros:** Nenhum

**Exemplos:**
```bash
python manage.py sync_celery_beat
```

**Comportamento:**
- Lê as tarefas definidas em `CELERY_BEAT_SCHEDULE` no `settings.py`
- Cria tarefas periódicas no banco de dados (usando `django_celery_beat`)
- Atualiza tarefas existentes se houver mudanças
- Desabilita tarefas INLABS que não estão mais no schedule
- Configura crontab schedules automaticamente

**Saída esperada:**
```
✅ Tarefa criada: coletar_inlabs_diario
✅ Tarefa atualizada: coletar_inlabs_diario
⚠️  Tarefa desabilitada: coletar_inlabs_antiga
```

**Nota:** Este comando deve ser executado sempre que houver alterações no `CELERY_BEAT_SCHEDULE` para sincronizar as tarefas com o banco de dados.

---

## Fluxos de Uso

### Fluxo 1: Importação Inicial de Dados Históricos

Para importar um grande volume de dados históricos:

```bash
# 1. Importar intervalo de datas (com skip-existing para evitar duplicatas)
python manage.py import_inlabs_batch \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --skip-existing \
  --delay 2 \
  --continue-on-error

# 2. Verificar estatísticas no resumo final
```

### Fluxo 2: Migração de SQLite para PostgreSQL

Para migrar dados de um arquivo SQLite existente:

```bash
# 1. Validar dados (dry-run)
python manage.py load_inlabs_data --dry-run

# 2. Carregar dados reais
python manage.py load_inlabs_data --batch-size 1000

# 3. Verificar estatísticas
```

### Fluxo 3: Backup e Restauração

Para fazer backup e restaurar dados:

```bash
# 1. Exportar dados para SQLite
python manage.py export_inlabs_to_sqlite --output backup_$(date +%Y%m%d).db

# 2. (Em caso de necessidade) Restaurar do backup
python manage.py load_inlabs_data --db-path backup_20250208.db
```

### Fluxo 4: Importação Diária Automatizada

Para configurar importação automática:

```bash
# 1. Sincronizar tarefas do Celery Beat
python manage.py sync_celery_beat

# 2. (Opcional) Testar importação manual
python manage.py import_inlabs --date $(date +%Y-%m-%d)
```

---

## Troubleshooting

### Erro: "Arquivo SQLite não encontrado"

**Problema:** O comando `load_inlabs_data` não encontra o arquivo SQLite.

**Solução:**
```bash
# Verificar se o arquivo existe
ls -la apps/imprensa_nacional/fixtures/inlabs_articles.db

# Ou especificar caminho customizado
python manage.py load_inlabs_data --db-path /caminho/completo/para/arquivo.db
```

### Erro: "Data inválida"

**Problema:** Formato de data incorreto nos comandos de importação.

**Solução:** Use sempre o formato `YYYY-MM-DD`:
```bash
# ✅ Correto
python manage.py import_inlabs --date 2025-02-08

# ❌ Incorreto
python manage.py import_inlabs --date 08/02/2025
```

### Erro: "Arquivo já existe" no export

**Problema:** Tentativa de exportar para um arquivo que já existe.

**Solução:**
```bash
# Usar --overwrite para sobrescrever
python manage.py export_inlabs_to_sqlite --output arquivo.db --overwrite

# Ou usar um nome diferente
python manage.py export_inlabs_to_sqlite --output arquivo_novo.db
```

### Performance: Importação muito lenta

**Problema:** Importação em lote está demorando muito.

**Soluções:**
- Aumentar o `--batch-size` (padrão: 1000)
- Reduzir o `--delay` entre importações
- Usar `--skip-existing` para pular datas já processadas

```bash
docker compose exec backend python manage.py import_inlabs_batch \
  --start-date 2025-01-01 \
  --batch-size 2000 \
  --delay 1 \
  --skip-existing
```

### Erro: "Unique constraint violation"

**Problema:** Tentativa de inserir registros duplicados.

**Solução:** Os comandos usam `update_or_create` automaticamente, mas se o erro persistir:
- Verificar se há conflitos na constraint `unique_together` do modelo
- Usar `--skip-existing` no `import_inlabs_batch`
- Limpar dados duplicados manualmente antes de importar

---

## Estrutura de Dados

Os comandos trabalham com as seguintes tabelas:

### inlabs_articles
- Armazena artigos do INLABS filtrados pelo Comando da Marinha
- Constraint única: `(article_id, pub_date, materia_id)`

### aviso_licitacao
- Armazena avisos de licitação extraídos dos artigos
- Relacionado a `inlabs_articles` via `article_id` (unique)

### credenciamento
- Armazena credenciamentos extraídos dos artigos
- Relacionado a `inlabs_articles` via `article_id` (unique)

---

## Notas Importantes

1. **Transações:** O comando `load_inlabs_data` executa dentro de uma transação atômica. Se houver erro, todas as alterações são revertidas.

2. **Validação:** Sempre use `--dry-run` antes de executar operações em produção para validar os dados.

3. **Performance:** Para grandes volumes de dados, ajuste o `--batch-size` conforme a capacidade do servidor.

4. **Backup:** Sempre faça backup antes de executar comandos que modificam dados em produção.

5. **Celery Beat:** Execute `sync_celery_beat` sempre que houver alterações no `CELERY_BEAT_SCHEDULE`.

---

## Suporte

Para mais informações sobre o app Imprensa Nacional, consulte:
- Documentação do app: `apps/imprensa_nacional/ATUALIZACAO_DADOS_IMPRENSA_NACIONAL.md`
- Modelos: `apps/imprensa_nacional/models.py`
- Serviços: `apps/imprensa_nacional/services/inlabs_downloader.py`
