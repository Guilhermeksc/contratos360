# Comandos de Migração PNCP - Guia de Uso

Este diretório contém comandos Django para migrar dados do arquivo SQLite `pncp.db` para o banco de dados PostgreSQL.

## 📋 Comandos Disponíveis

### 1. `load_fornecedores` - Carrega Fornecedores
Migra a tabela `fornecedores` do SQLite para o modelo `Fornecedor` no PostgreSQL.

**Dependências:** Nenhuma (pode ser executado primeiro)

**Uso:**
```bash
# Execução normal
docker compose exec backend python manage.py load_fornecedores

# Validação sem salvar (dry-run)
docker compose exec backend python manage.py load_fornecedores --dry-run

# Com caminho customizado
docker compose exec backend python manage.py load_fornecedores --db-path /caminho/para/pncp.db

# Com tamanho de lote customizado
docker compose exec backend python manage.py load_fornecedores --batch-size 500
```

---

### 2. `load_compras` - Carrega Compras
Migra a tabela `compras` do SQLite para o modelo `Compra` no PostgreSQL.

**Dependências:** Nenhuma (pode ser executado após fornecedores ou antes)

**Uso:**
```bash
# Execução normal
docker compose exec backend python manage.py load_compras

# Validação sem salvar (dry-run)
docker compose exec backend python manage.py load_compras --dry-run

# Com caminho customizado
docker compose exec backend python manage.py load_compras --db-path /caminho/para/pncp.db

# Com tamanho de lote customizado
docker compose exec backend python manage.py load_compras --batch-size 500
```

---

### 3. `load_itens_compra` - Carrega Itens de Compra
Migra a tabela `itens_compra` do SQLite para o modelo `ItemCompra` no PostgreSQL.

**Dependências:** Requer que `Compra` já tenha sido migrado

**Uso:**
```bash
# Execução normal
docker compose exec backend python manage.py load_itens_compra

# Validação sem salvar (dry-run)
docker compose exec backend python manage.py load_itens_compra --dry-run

# Com caminho customizado
docker compose exec backend python manage.py load_itens_compra --db-path /caminho/para/pncp.db

# Com tamanho de lote customizado
docker compose exec backend python manage.py load_itens_compra --batch-size 500
```

**Nota:** Itens cuja compra não existir no PostgreSQL serão pulados (será exibido um aviso).

---

### 4. `load_resultados_item` - Carrega Resultados de Itens
Migra a tabela `resultados_item` do SQLite para o modelo `ResultadoItem` no PostgreSQL.

**Dependências:** Requer que `ItemCompra` e `Fornecedor` já tenham sido migrados

**Uso:**
```bash
# Execução normal
docker compose exec backend python manage.py load_resultados_item

# Validação sem salvar (dry-run)
docker compose exec backend python manage.py load_resultados_item --dry-run

# Com caminho customizado
docker compose exec backend python manage.py load_resultados_item --db-path /caminho/para/pncp.db

# Com tamanho de lote customizado
docker compose exec backend python manage.py load_resultados_item --batch-size 500
```

**Nota:** Resultados cujo item de compra ou fornecedor não existirem no PostgreSQL serão pulados (será exibido um aviso).

---

## 🚀 Ordem Recomendada de Execução

Para garantir a integridade referencial, execute os comandos na seguinte ordem:

```bash
# 1. Primeiro: Fornecedores (não depende de nada)
docker compose exec backend python manage.py load_fornecedores

# 2. Segundo: Compras (não depende de nada)
docker compose exec backend python manage.py load_compras

# 3. Terceiro: Itens de Compra (depende de Compras)
docker compose exec backend python manage.py load_itens_compra

# 4. Por último: Resultados de Itens (depende de Itens de Compra e Fornecedores)
docker compose exec backend python manage.py load_resultados_item
```

---

## 📝 Opções Disponíveis

Todos os comandos suportam as seguintes opções:

### `--db-path` (opcional)
Caminho para o arquivo SQLite. Se não fornecido, usa o caminho padrão:
- **Padrão:** `apps/pncp/fixtures/pncp.db`

**Exemplo:**
```bash
python manage.py load_fornecedores --db-path /caminho/customizado/pncp.db
```

### `--dry-run` (opcional)
Executa o comando sem salvar dados no banco. Útil para validar antes da migração real.

**Exemplo:**
```bash
python manage.py load_fornecedores --dry-run
```

### `--batch-size` (opcional)
Tamanho do lote para inserção em batch. Valores menores usam menos memória, mas são mais lentos.

- **Padrão:** `1000`
- **Recomendado:** Entre `500` e `2000` dependendo da memória disponível

**Exemplo:**
```bash
python manage.py load_fornecedores --batch-size 500
```

---

## 🔍 Exemplo Completo de Migração

### Passo 1: Validação (Dry-Run)
Execute todos os comandos em modo dry-run para validar:

```bash
docker compose exec backend python manage.py load_fornecedores --dry-run
docker compose exec backend python manage.py load_compras --dry-run
docker compose exec backend python manage.py load_itens_compra --dry-run
docker compose exec backend python manage.py load_resultados_item --dry-run
```

### Passo 2: Migração Real
Após validar, execute a migração real:

```bash
# 1. Fornecedores
docker compose exec backend python manage.py load_fornecedores

# 2. Compras
docker compose exec backend python manage.py load_compras

# 3. Itens de Compra
docker compose exec backend python manage.py load_itens_compra

# 4. Resultados de Itens
docker compose exec backend python manage.py load_resultados_item
```

---

## ⚠️ Tratamento de Erros

### Campos Truncados
Os comandos automaticamente truncam valores que excedem os limites dos campos:
- **CNPJ:** Máximo 20 caracteres
- **Razão Social:** Máximo 255 caracteres
- **Compra ID:** Máximo 100 caracteres
- **Número de Compra:** Máximo 50 caracteres
- **Modalidade:** Máximo 100 caracteres
- E outros campos conforme definido nos modelos

### Valores Numéricos
- Valores decimais são validados e limitados conforme `max_digits` e `decimal_places`
- Percentuais (`percentual_desconto`, `percentual_economia`) são limitados a 999.9999

### Datas
- Datas são convertidas para timezone-aware automaticamente
- Formatos suportados: `YYYY-MM-DD`, `YYYY-MM-DD HH:MM:SS`, `DD/MM/YYYY`, `DD/MM/YYYY HH:MM:SS`

### Registros Dependentes Não Encontrados
- Itens de compra cuja compra não existir serão pulados
- Resultados cujo item ou fornecedor não existirem serão pulados
- Avisos serão exibidos informando quantos registros foram pulados

---

## 📊 Estatísticas Esperadas

Com base no arquivo `pncp.db` fornecido, espera-se migrar aproximadamente:

- **Fornecedores:** ~17.005 registros
- **Compras:** ~56.259 registros
- **Itens de Compra:** ~346.846 registros
- **Resultados de Itens:** ~264.446 registros

---

## 🐛 Troubleshooting

### Erro: "Arquivo SQLite não encontrado"
**Solução:** Verifique se o arquivo `pncp.db` existe no caminho especificado ou use `--db-path` para fornecer o caminho correto.

### Erro: "value too long for type character varying"
**Solução:** Os comandos já fazem truncamento automático. Se o erro persistir, verifique se há algum campo não tratado.

### Erro: "numeric field overflow"
**Solução:** Os comandos já validam e limitam valores numéricos. Se o erro persistir, verifique os dados no SQLite.

### Erro: "Compra não encontrada" ou "Fornecedor não encontrado"
**Solução:** Execute os comandos na ordem correta:
1. `load_fornecedores`
2. `load_compras`
3. `load_itens_compra`
4. `load_resultados_item`

### Performance Lenta
**Solução:** Ajuste o `--batch-size`:
- Valores menores (500): Menos memória, mais lento
- Valores maiores (2000): Mais memória, mais rápido

---

## 📚 Comando Original

O comando original `load_pncp_from_sqlite` ainda está disponível e executa todos os passos em sequência. Os comandos separados oferecem mais controle e flexibilidade.

**Uso do comando original:**
```bash
docker compose exec backend python manage.py load_pncp_from_sqlite
docker compose exec backend python manage.py load_pncp_from_sqlite --dry-run
```

---

## 🔄 Reexecução

Todos os comandos usam `update_or_create`, então podem ser executados múltiplas vezes sem criar duplicatas. Os registros existentes serão atualizados se necessário.

---

## 📞 Suporte

Em caso de problemas ou dúvidas, verifique:
1. Os logs do comando para identificar erros específicos
2. A integridade do arquivo SQLite
3. A conexão com o banco de dados PostgreSQL
4. As dependências entre os modelos (ordem de execução)
