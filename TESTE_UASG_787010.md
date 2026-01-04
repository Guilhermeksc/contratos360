# Teste de Integração - UASG 787010

Este documento explica como testar a sincronização da UASG 787010 e verificar se todos os campos estão sendo salvos corretamente, especialmente o campo `valor_global`.

## 🚀 Métodos de Teste

### Método 1: Script Automatizado (Recomendado)

Execute o script que automatiza todo o processo:

```bash
./test_uasg_787010.sh
```

Este script:
1. Verifica se os containers estão rodando
2. Executa o teste de integração
3. Mostra estatísticas dos contratos salvos
4. Identifica problemas com `valor_global`

### Método 2: Comando de Management

Use o comando de management customizado:

```bash
docker compose exec backend python manage.py test_uasg --uasg 787010 --limit 10
```

**Parâmetros:**
- `--uasg`: Código da UASG (obrigatório)
- `--limit`: Número máximo de contratos para verificar (padrão: 10)

**Exemplo:**
```bash
docker compose exec backend python manage.py test_uasg --uasg 787010 --limit 20
```

### Método 3: Teste Unitário Completo

Execute todos os testes de integração:

```bash
docker compose exec backend python manage.py test gestao_contratos.tests_integration --verbosity=2
```

Ou apenas o teste específico da UASG 787010:

```bash
docker compose exec backend python manage.py test gestao_contratos.tests_integration.ComprasNetIntegrationTest.test_sync_uasg_787010_and_verify_all_fields --verbosity=2
```

### Método 4: Sincronização Manual + Verificação

1. **Sincronizar a UASG:**
```bash
docker compose exec backend python manage.py sync_comprasnet --uasg 787010
```

2. **Verificar no shell do Django:**
```bash
docker compose exec backend python manage.py shell
```

No shell:
```python
from gestao_contratos.models import Contrato, Uasg
from decimal import Decimal

uasg_code = '787010'
contratos = Contrato.objects.filter(uasg__uasg_code=uasg_code)

print(f"Total de contratos: {contratos.count()}")

# Contratos com valor_global
com_valor = contratos.exclude(valor_global__isnull=True).count()
sem_valor = contratos.filter(valor_global__isnull=True).count()

print(f"Com valor_global: {com_valor}")
print(f"Sem valor_global: {sem_valor}")

# Exemplos
print("\nExemplos COM valor_global:")
for c in contratos.exclude(valor_global__isnull=True)[:5]:
    print(f"  {c.numero or c.id}: R$ {c.valor_global:,.2f}")

print("\nExemplos SEM valor_global:")
for c in contratos.filter(valor_global__isnull=True)[:5]:
    raw_valor = c.raw_json.get('valor_global') if c.raw_json else None
    print(f"  {c.numero or c.id}: raw_json.valor_global = {raw_valor}")
```

## 📊 O que os testes verificam

### Campos Verificados:
- ✅ `id` - ID do contrato
- ✅ `uasg` - Relação com UASG
- ✅ `numero` - Número do contrato
- ✅ `licitacao_numero` - Número da licitação
- ✅ `processo` - Processo administrativo
- ✅ `fornecedor_nome` - Nome do fornecedor
- ✅ `fornecedor_cnpj` - CNPJ do fornecedor
- ✅ `objeto` - Objeto do contrato
- ✅ **`valor_global`** - Valor monetário (campo crítico!)
- ✅ `vigencia_inicio` - Data de início
- ✅ `vigencia_fim` - Data de fim
- ✅ `tipo` - Tipo do contrato
- ✅ `modalidade` - Modalidade de licitação
- ✅ `contratante_orgao_unidade_gestora_codigo` - Código UG
- ✅ `contratante_orgao_unidade_gestora_nome_resumido` - Nome UG
- ✅ `raw_json` - JSON completo da API

### Verificações Especiais para `valor_global`:

1. **Tipo de dado:** Deve ser `Decimal`, não `float` ou `string`
2. **Valor não nulo:** Verifica se foi salvo (não é `None`)
3. **Valor positivo:** Deve ser >= 0
4. **Formato correto:** Verifica se valores com vírgula/ponto foram parseados corretamente
5. **Comparação:** Compara valor parseado com valor salvo no banco

## 🔍 Troubleshooting

### Problema: `valor_global` não está sendo salvo

**Possíveis causas:**

1. **Formato do valor na API:** A API pode retornar valores em formatos diferentes
   - Solução: Verifique o `raw_json` do contrato para ver o formato original

2. **Erro no parsing:** O método `_parse_decimal` pode não estar tratando algum formato
   - Solução: Verifique os logs e o valor no `raw_json`

3. **Validação do modelo:** O `MinValueValidator` pode estar rejeitando valores
   - Solução: Verifique se há valores negativos na API

### Como debugar:

1. **Ver o valor original da API:**
```python
contrato = Contrato.objects.get(id='SEU_ID')
print(contrato.raw_json.get('valor_global'))
```

2. **Testar o parsing manualmente:**
```python
from gestao_contratos.services.ingestion import ComprasNetIngestionService

service = ComprasNetIngestionService()
valor_original = "1.000.000,50"  # Exemplo
valor_parseado = service._parse_decimal(valor_original)
print(f"Original: {valor_original}")
print(f"Parseado: {valor_parseado}")
```

3. **Verificar logs do Django:**
```bash
docker compose logs backend --tail 100 | grep -i "valor\|decimal\|erro"
```

## 📝 Formato Esperado

O método `_parse_decimal` suporta os seguintes formatos:

- ✅ `"1.000.000,50"` → `Decimal('1000000.50')` (formato brasileiro)
- ✅ `"500000,75"` → `Decimal('500000.75')` (vírgula como decimal)
- ✅ `"1000000.25"` → `Decimal('1000000.25')` (ponto como decimal)
- ✅ `750000.50` → `Decimal('750000.50')` (número float)
- ✅ `None` ou `""` → `None` (valor vazio)

## ✅ Resultado Esperado

Após executar os testes, você deve ver:

- ✅ Todos ou a maioria dos contratos com `valor_global` salvo
- ✅ Valores em formato `Decimal` correto
- ✅ Valores correspondendo ao formato original da API
- ✅ Taxa de sucesso > 50% para `valor_global`

Se encontrar problemas, os testes irão:
- Listar contratos sem `valor_global`
- Mostrar o valor original no `raw_json`
- Indicar possíveis causas do problema


