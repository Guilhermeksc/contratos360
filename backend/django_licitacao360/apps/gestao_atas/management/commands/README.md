# Comandos de Management - Gestão de Atas

Este documento descreve os comandos de management disponíveis para o app `gestao_atas`, que gerencia a importação e processamento de atas de registro de preço.

## Comandos Disponíveis

### load_atas

**Descrição:** Carrega dados do arquivo SQLite (`atas.db`) para o banco de dados PostgreSQL.

**Uso:**
```bash
python manage.py load_atas [opções]
```

**Parâmetros:**
- `--db-path` (opcional): Caminho para o arquivo SQLite. Padrão: `apps/gestao_atas/fixtures/atas.db`
- `--dry-run`: Executa sem salvar no banco (apenas valida)
- `--batch-size`: Tamanho do lote para inserção em batch (padrão: 1000)

**Exemplos:**
```bash
# Carregar todas as atas
docker compose exec backend python manage.py load_atas

# Validação sem salvar (dry-run)
docker compose exec backend python manage.py load_atas --dry-run

# Especificar caminho customizado
docker compose exec backend python manage.py load_atas --db-path /caminho/para/atas.db

# Ajustar tamanho do lote
docker compose exec backend python manage.py load_atas --batch-size 500
```

**Comportamento:**
- Conecta ao arquivo SQLite especificado
- Carrega dados da tabela `ata`
- Processa em lotes para melhor performance
- Usa `update_or_create` para evitar duplicatas
- Trunca campos automaticamente se excederem o tamanho máximo
- Executa dentro de uma transação para garantir consistência

**Saída esperada:**
```
Conectando ao SQLite: /path/to/atas.db
Migrando atas...
  ✓ Migradas 15289 atas

✅ Migração concluída com sucesso!
  Atas: 15289
```

**Nota:** Este comando é útil para migrar dados de um banco SQLite existente para o PostgreSQL.

---

## Estrutura de Dados

O comando trabalha com a seguinte tabela:

### ata
- Armazena atas de registro de preço
- Chave primária: `numeroControlePNCPAta`
- Campos principais:
  - Identificação: `numeroControlePNCPAta`, `numeroAtaRegistroPreco`, `anoAta`
  - Órgão: `cnpjOrgao`, `nomeOrgao`, `codigoUnidadeOrgao`, `nomeUnidadeOrgao`
  - Vigência: `vigenciaInicio`, `vigenciaFim`, `cancelado`, `dataCancelamento`
  - Contratação: `objetoContratacao`, `dataAssinatura`
  - Controle: `dataPublicacaoPncp`, `dataInclusao`, `dataAtualizacao`

---

## Notas Importantes

1. **Transações:** O comando executa dentro de uma transação atômica. Se houver erro, todas as alterações são revertidas.

2. **Validação:** Sempre use `--dry-run` antes de executar operações em produção para validar os dados.

3. **Performance:** Para grandes volumes de dados, ajuste o `--batch-size` conforme a capacidade do servidor.

4. **Backup:** Sempre faça backup antes de executar comandos que modificam dados em produção.

5. **Duplicatas:** O comando usa `update_or_create` baseado em `numeroControlePNCPAta`, então execuções repetidas atualizarão registros existentes.

---

## Troubleshooting

### Erro: "Arquivo SQLite não encontrado"

**Problema:** O comando `load_atas` não encontra o arquivo SQLite.

**Solução:**
```bash
# Verificar se o arquivo existe
ls -la apps/gestao_atas/fixtures/atas.db

# Ou especificar caminho customizado
python manage.py load_atas --db-path /caminho/completo/para/arquivo.db
```

### Erro: "Unique constraint violation"

**Problema:** Tentativa de inserir registros duplicados.

**Solução:** O comando usa `update_or_create` automaticamente, mas se o erro persistir:
- Verificar se há conflitos na constraint `unique_together` do modelo
- Limpar dados duplicados manualmente antes de importar

### Performance: Importação muito lenta

**Problema:** Importação está demorando muito.

**Soluções:**
- Aumentar o `--batch-size` (padrão: 1000)
- Verificar índices no banco de dados PostgreSQL

```bash
docker compose exec backend python manage.py load_atas --batch-size 2000
```

---

## Suporte

Para mais informações sobre o app Gestão de Atas, consulte:
- Modelos: `apps/gestao_atas/models.py`
- Views: `apps/gestao_atas/views.py`
- Serializers: `apps/gestao_atas/serializers.py`
