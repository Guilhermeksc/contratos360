# Endpoints PNCP - Documentação da API

Esta documentação descreve os endpoints disponíveis para acessar dados do PNCP, equivalentes ao script Python original.

## 📋 Endpoints Disponíveis

### Base URL
```
/api/pncp/
```

---

## 1. Compras por Código de Unidade

Retorna todas as compras filtradas por código de unidade.

**Endpoint:**
```
GET /api/pncp/compras/por-unidade/{codigo_unidade}/
```

**Parâmetros:**
- `codigo_unidade` (path): Código da unidade (ex: `765701`)

**Exemplo:**
```bash
# Via navegador ou curl (sem autenticação)
GET http://localhost:8080/api/pncp/compras/por-unidade/765701/
```

**Resposta:**
```json
[
  {
    "compra_id": "2023-8112",
    "ano_compra": 2023,
    "sequencial_compra": 8112,
    "numero_compra": "001/2023",
    "codigo_unidade": "765701",
    "objeto_compra": "Aquisição de...",
    "modalidade_nome": "Inexigibilidade",
    "link_pncp": "https://pncp.gov.br/app/editais/00394502000144/2023/8112",
    "itens": [...],
    ...
  }
]
```

---

## 2. Itens com Resultado Merge

Retorna o merge de itens de compra com seus resultados (fornecedores homologados).

**Endpoint:**
```
GET /api/pncp/compras/itens-resultado-merge/{codigo_unidade}/
```

**Parâmetros:**
- `codigo_unidade` (path): Código da unidade (ex: `765701`)

**Exemplo:**
```bash
GET http://localhost:8080/api/pncp/compras/itens-resultado-merge/765701/
```

**Resposta:**
```json
[
  {
    "ano_compra": 2023,
    "sequencial_compra": 8112,
    "numero_item": 1,
    "descricao": "Item descrição...",
    "unidade_medida": "UN",
    "valor_unitario_estimado": "100.00",
    "valor_total_estimado": "1000.00",
    "quantidade": "10.00",
    "situacao_compra_item_nome": "Homologado",
    "cnpj_fornecedor": "12345678000190",
    "valor_total_homologado": "950.00",
    "valor_unitario_homologado": "95.00",
    "quantidade_homologada": 10,
    "percentual_desconto": 5.0,
    "link_pncp": "https://pncp.gov.br/app/editais/00394502000144/2023/8112",
    "razao_social": "Fornecedor LTDA"
  }
]
```

---

## 3. Modalidades Agregadas

Retorna estatísticas agregadas por modalidade de compra.

**Endpoint:**
```
GET /api/pncp/compras/modalidades-agregadas/{codigo_unidade}/
```

**Parâmetros:**
- `codigo_unidade` (path): Código da unidade (ex: `765701`)

**Exemplo:**
```bash
GET http://localhost:8080/api/pncp/compras/modalidades-agregadas/765701/
```

**Resposta:**
```json
[
  {
    "ano_compra": 2023,
    "modalidade_nome": "Inexigibilidade",
    "quantidade_compras": 15,
    "valor_total_homologado": "150000.00"
  },
  {
    "ano_compra": 2023,
    "modalidade_nome": "Pregão Eletrônico",
    "quantidade_compras": 8,
    "valor_total_homologado": "80000.00"
  }
]
```

---

## 4. Fornecedores Agregados

Retorna fornecedores com valores totais homologados agregados.

**Endpoint:**
```
GET /api/pncp/compras/fornecedores-agregados/{codigo_unidade}/
```

**Parâmetros:**
- `codigo_unidade` (path): Código da unidade (ex: `765701`)

**Exemplo:**
```bash
GET http://localhost:8080/api/pncp/compras/fornecedores-agregados/765701/
```

**Resposta:**
```json
[
  {
    "cnpj_fornecedor": "12345678000190",
    "razao_social": "Fornecedor LTDA",
    "valor_total_homologado": "50000.00"
  },
  {
    "cnpj_fornecedor": "98765432000110",
    "razao_social": "Outro Fornecedor ME",
    "valor_total_homologado": "30000.00"
  }
]
```

---

## 5. Itens por Modalidade

Retorna itens filtrados por modalidade específica.

**Endpoint:**
```
GET /api/pncp/compras/itens-por-modalidade/{codigo_unidade}/
```

**Parâmetros:**
- `codigo_unidade` (path): Código da unidade (ex: `765701`)
- `modalidade_nome` (query, opcional): Nome da modalidade para filtrar

**Exemplo:**
```bash
# Todos os itens
GET http://localhost:8080/api/pncp/compras/itens-por-modalidade/765701/

# Filtrar por modalidade específica
GET http://localhost:8080/api/pncp/compras/itens-por-modalidade/765701/?modalidade_nome=Inexigibilidade
```

**Resposta:**
```json
[
  {
    "ano_compra": 2023,
    "sequencial_compra": 8112,
    "numero_item": 1,
    "cnpj_fornecedor": "12345678000190",
    "razao_social": "Fornecedor LTDA",
    "descricao": "Item descrição...",
    "quantidade": "10.00",
    "valor_total_estimado": "1000.00",
    "valor_total_homologado": "950.00",
    "percentual_desconto": 5.0
  }
]
```

---

## 6. Exportação XLSX

Gera e faz download de arquivo XLSX equivalente ao script Python original.

**Endpoint:**
```
GET /api/pncp/compras/export-xlsx/{codigo_unidade}/
```

**Parâmetros:**
- `codigo_unidade` (path): Código da unidade (ex: `765701`)

**Exemplo:**
```bash
GET /api/pncp/compras/export-xlsx/765701/
```

**Resposta:**
- Arquivo XLSX para download com nome `compras_{codigo_unidade}.xlsx`

**Estrutura do XLSX:**

O arquivo contém as seguintes abas:

1. **compras**: Todas as compras da unidade
2. **itens_resultado_merge**: Merge de itens com resultados
3. **modalidades**: Estatísticas agregadas por modalidade
4. **fornecedores**: Fornecedores com valores agregados
5. **inexigibilidade**: Itens da modalidade Inexigibilidade
6. **{modalidade}**: Uma aba para cada modalidade única (exceto Inexigibilidade)

**Exemplo de uso:**
```bash
# Via curl (sem autenticação)
curl -O -J "http://localhost:8080/api/pncp/compras/export-xlsx/765701/"

# Via navegador
http://localhost:8080/api/pncp/compras/export-xlsx/765701/
```

---

## 📊 Endpoints Padrão do DRF

Além dos endpoints customizados acima, os seguintes endpoints padrão do Django REST Framework estão disponíveis:

### Fornecedores
- `GET /api/pncp/fornecedores/` - Lista todos os fornecedores
- `GET /api/pncp/fornecedores/{id}/` - Detalhes de um fornecedor
- `POST /api/pncp/fornecedores/` - Criar fornecedor
- `PUT /api/pncp/fornecedores/{id}/` - Atualizar fornecedor
- `DELETE /api/pncp/fornecedores/{id}/` - Deletar fornecedor

### Compras
- `GET /api/pncp/compras/` - Lista todas as compras
- `GET /api/pncp/compras/{id}/` - Detalhes de uma compra
- Filtros: `?codigo_unidade=765701&ano_compra=2023&modalidade_nome=Inexigibilidade`
- Busca: `?search=objeto`

### Itens de Compra
- `GET /api/pncp/itens/` - Lista todos os itens
- `GET /api/pncp/itens/{id}/` - Detalhes de um item
- Filtros: `?compra={compra_id}&tem_resultado=true`

### Resultados de Itens
- `GET /api/pncp/resultados/` - Lista todos os resultados
- `GET /api/pncp/resultados/{id}/` - Detalhes de um resultado
- Filtros: `?item_compra={item_id}&fornecedor={cnpj}`

---

## 🔍 Filtros e Busca

### Filtros Disponíveis

**Compras:**
- `codigo_unidade`: Filtra por código da unidade
- `ano_compra`: Filtra por ano
- `modalidade_nome`: Filtra por modalidade

**Itens:**
- `compra`: Filtra por ID da compra
- `tem_resultado`: Filtra itens com/sem resultado (true/false)
- `situacao_compra_item_nome`: Filtra por situação

**Resultados:**
- `item_compra`: Filtra por ID do item
- `fornecedor`: Filtra por CNPJ do fornecedor
- `status`: Filtra por status

### Busca (Search)

**Compras:**
- Busca em: `numero_compra`, `objeto_compra`, `numero_processo`

**Fornecedores:**
- Busca em: `cnpj_fornecedor`, `razao_social`

**Itens:**
- Busca em: `descricao`

**Resultados:**
- Busca em: `marca`, `modelo`

**Exemplo:**
```bash
GET /api/pncp/compras/?search=aquisição
GET /api/pncp/fornecedores/?search=LTDA
```

---

## 📝 Exemplos de Uso Completo

### 1. Obter todas as compras de uma unidade
```bash
curl http://localhost:8080/api/pncp/compras/por-unidade/765701/
```

### 2. Obter itens com resultados
```bash
curl http://localhost:8080/api/pncp/compras/itens-resultado-merge/765701/
```

### 3. Obter estatísticas por modalidade
```bash
curl http://localhost:8080/api/pncp/compras/modalidades-agregadas/765701/
```

### 4. Obter fornecedores agregados
```bash
curl http://localhost:8080/api/pncp/compras/fornecedores-agregados/765701/
```

### 5. Obter itens de uma modalidade específica
```bash
curl "http://localhost:8080/api/pncp/compras/itens-por-modalidade/765701/?modalidade_nome=Inexigibilidade"
```

### 6. Exportar para XLSX
```bash
curl -O -J "http://localhost:8080/api/pncp/compras/export-xlsx/765701/"
```

---

## ⚠️ Notas Importantes

1. **Percentual de Desconto**: Calculado como `((valor_total_estimado - valor_total_homologado) / valor_total_estimado) * 100`

2. **Link PNCP**: Gerado automaticamente no formato:
   `https://pncp.gov.br/app/editais/00394502000144/{ano_compra}/{sequencial_compra}`

3. **Valores Null**: Alguns campos podem ser `null` quando não há resultado homologado para o item.

4. **Formato de Datas**: Datas são retornadas no formato ISO 8601 com timezone.

5. **Formato de Valores Decimais**: Valores monetários são retornados como strings para preservar precisão.

---

## 🔐 Autenticação

**Todos os endpoints do PNCP são públicos** e não requerem autenticação. Eles estão configurados com `permission_classes = [AllowAny]`, permitindo acesso sem necessidade de token JWT ou credenciais.

---

## 📞 Suporte

Para problemas ou dúvidas sobre os endpoints, consulte:
- Logs do servidor Django
- Documentação do Django REST Framework
- Código-fonte em `apps/pncp/views.py` e `apps/pncp/serializers.py`
