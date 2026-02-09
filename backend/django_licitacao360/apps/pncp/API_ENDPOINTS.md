# API PNCP - Endpoints de Compras

Este documento descreve os endpoints públicos da API PNCP para consulta de compras.

## Base URL

```
/api/pncp/
```

## Endpoints Disponíveis

### 1. Compra Detalhada

Retorna os detalhes de uma compra específica incluindo seus itens e resultados.

**Endpoint:** `GET /api/pncp/compras/detalhada/`

**Parâmetros de Query (todos obrigatórios):**
- `codigo_unidade` (string): Código da unidade
- `numero_compra` (string): Número da compra
- `ano_compra` (integer): Ano da compra
- `modalidade` (integer): ID da modalidade

**Resposta de Sucesso (200 OK):**

```json
{
  "sequencial_compra": 123,
  "objeto_compra": "Descrição do objeto da compra",
  "amparo_legal": {
    "id": 1,
    "nome": "Lei 8.666/1993",
    "descricao": "Lei de Licitações"
  },
  "modo_disputa": {
    "id": 1,
    "nome": "Menor Preço",
    "descricao": "Modalidade de menor preço"
  },
  "data_publicacao_pncp": "2024-01-15T10:30:00Z",
  "data_atualizacao": "2024-01-20T14:45:00Z",
  "valor_total_estimado": "100000.00",
  "valor_total_homologado": "95000.00",
  "percentual_desconto": "5.0000",
  "itens": [
    {
      "item_id": "item-123",
      "numero_item": 1,
      "descricao": "Descrição do item",
      "unidade_medida": "UN",
      "valor_unitario_estimado": "1000.00",
      "valor_total_estimado": "10000.00",
      "quantidade": "10.00",
      "percentual_economia": "5.0000",
      "situacao_compra_item_nome": "Homologado",
      "resultados": [
        {
          "resultado_id": "resultado-123",
          "valor_total_homologado": "9500.00",
          "quantidade_homologada": 10,
          "valor_unitario_homologado": "950.00",
          "fornecedor_detalhes": {
            "cnpj_fornecedor": "12.345.678/0001-90",
            "razao_social": "Empresa Exemplo Ltda"
          }
        }
      ]
    }
  ]
}
```

**Resposta de Erro (400 Bad Request):**

```json
{
  "error": "Parâmetro codigo_unidade é obrigatório"
}
```

**Resposta de Erro (404 Not Found):**

```json
{
  "error": "Compra não encontrada com os parâmetros fornecidos"
}
```

---

### 2. Listagem de Compras

Retorna todas as compras de uma unidade em um determinado ano.

**Endpoint:** `GET /api/pncp/compras/listagem/`

**Parâmetros de Query (todos obrigatórios):**
- `codigo_unidade` (string): Código da unidade
- `ano_compra` (integer): Ano da compra

**Resposta de Sucesso (200 OK):**

```json
{
  "count": 2,
  "results": [
    {
      "compra_id": "compra-123",
      "ano_compra": 2024,
      "sequencial_compra": 123,
      "numero_compra": "001/2024",
      "codigo_unidade": "123456",
      "objeto_compra": "Descrição do objeto da compra 1",
      "modalidade": {
        "id": 1,
        "nome": "Pregão",
        "descricao": "Modalidade de pregão"
      },
      "amparo_legal": {
        "id": 1,
        "nome": "Lei 8.666/1993",
        "descricao": "Lei de Licitações"
      },
      "modo_disputa": {
        "id": 1,
        "nome": "Menor Preço",
        "descricao": "Modalidade de menor preço"
      },
      "numero_processo": "12345/2024",
      "data_publicacao_pncp": "2024-01-15T10:30:00Z",
      "data_atualizacao": "2024-01-20T14:45:00Z",
      "valor_total_estimado": "100000.00",
      "valor_total_homologado": "95000.00",
      "percentual_desconto": "5.0000"
    },
    {
      "compra_id": "compra-124",
      "ano_compra": 2024,
      "sequencial_compra": 124,
      "numero_compra": "002/2024",
      "codigo_unidade": "123456",
      "objeto_compra": "Descrição do objeto da compra 2",
      "modalidade": {
        "id": 2,
        "nome": "Tomada de Preços",
        "descricao": "Modalidade de tomada de preços"
      },
      "amparo_legal": {
        "id": 1,
        "nome": "Lei 8.666/1993",
        "descricao": "Lei de Licitações"
      },
      "modo_disputa": {
        "id": 1,
        "nome": "Menor Preço",
        "descricao": "Modalidade de menor preço"
      },
      "numero_processo": "12346/2024",
      "data_publicacao_pncp": "2024-01-16T10:30:00Z",
      "data_atualizacao": "2024-01-21T14:45:00Z",
      "valor_total_estimado": "200000.00",
      "valor_total_homologado": "190000.00",
      "percentual_desconto": "5.0000"
    }
  ]
}
```

**Resposta de Erro (400 Bad Request):**

```json
{
  "error": "Parâmetro codigo_unidade é obrigatório"
}
```

---

### 3. Unidades por Ano

Retorna todos os códigos de unidade que possuem compras em um determinado ano, com informações agregadas.

**Endpoint:** `GET /api/pncp/unidades/por-ano/`

**Parâmetros de Query (obrigatório):**
- `ano_compra` (integer): Ano da compra

**Resposta de Sucesso (200 OK):**

```json
{
  "ano_compra": 2024,
  "count": 2,
  "results": [
    {
      "codigo_unidade": "123456",
      "ano_compra": 2024,
      "quantidade_compras": 5,
      "valor_total_estimado": "500000.00",
      "valor_total_homologado": "475000.00"
    },
    {
      "codigo_unidade": "789012",
      "ano_compra": 2024,
      "quantidade_compras": 3,
      "valor_total_estimado": "300000.00",
      "valor_total_homologado": "285000.00"
    }
  ]
}
```

**Resposta de Erro (400 Bad Request):**

```json
{
  "error": "Parâmetro ano_compra é obrigatório"
}
```

---

### 4. Anos e Unidades para Combobox

Retorna todos os anos disponíveis e, para cada ano, todos os códigos de unidade disponíveis. Ideal para preencher comboboxes em interfaces.

**Endpoint:** `GET /api/pncp/combo/anos-unidades/`

**Parâmetros de Query:** Nenhum (endpoint sem parâmetros)

**Resposta de Sucesso (200 OK):**

```json
{
  "anos": [2024, 2023, 2022],
  "unidades_por_ano": {
    "2024": [
      {
        "codigo_unidade": "123456",
        "sigla_om": "SIGLA1"
      },
      {
        "codigo_unidade": "789012",
        "sigla_om": "SIGLA2"
      },
      {
        "codigo_unidade": "345678",
        "sigla_om": "SIGLA3"
      }
    ],
    "2023": [
      {
        "codigo_unidade": "123456",
        "sigla_om": "SIGLA1"
      },
      {
        "codigo_unidade": "345678",
        "sigla_om": "SIGLA3"
      }
    ],
    "2022": [
      {
        "codigo_unidade": "123456",
        "sigla_om": "SIGLA1"
      },
      {
        "codigo_unidade": "789012",
        "sigla_om": "SIGLA2"
      }
    ]
  }
}
```

**Características:**
- Os anos são retornados em ordem decrescente (mais recentes primeiro)
- Os códigos de unidade são retornados em ordem crescente (alfabética)
- Apenas anos e unidades que possuem compras são incluídos
- Cada unidade inclui `codigo_unidade` e `sigla_om` (obtida do modelo Uasg)
- O campo `sigla_om` pode ser `null` se a unidade não for encontrada na tabela Uasg

---

## Exemplos de Uso

### cURL

#### Endpoint 1 - Compra Detalhada

```bash
curl -X GET "http://localhost:8000/api/pncp/compras/detalhada/?codigo_unidade=123456&numero_compra=001/2024&ano_compra=2024&modalidade=1" \
  -H "Accept: application/json"
```

#### Endpoint 2 - Listagem de Compras

```bash
curl -X GET "http://localhost:8000/api/pncp/compras/listagem/?codigo_unidade=123456&ano_compra=2024" \
  -H "Accept: application/json"
```

#### Endpoint 3 - Unidades por Ano

```bash
curl -X GET "http://localhost:8000/api/pncp/unidades/por-ano/?ano_compra=2024" \
  -H "Accept: application/json"
```

### Python (requests)

#### Endpoint 1 - Compra Detalhada

```python
import requests

url = "http://localhost:8000/api/pncp/compras/detalhada/"
params = {
    "codigo_unidade": "123456",
    "numero_compra": "001/2024",
    "ano_compra": 2024,
    "modalidade": 1
}

response = requests.get(url, params=params)
data = response.json()

if response.status_code == 200:
    print(f"Sequencial: {data['sequencial_compra']}")
    print(f"Objeto: {data['objeto_compra']}")
    print(f"Valor Total Homologado: {data['valor_total_homologado']}")
    print(f"Itens: {len(data['itens'])}")
else:
    print(f"Erro: {data.get('error', 'Erro desconhecido')}")
```

#### Endpoint 2 - Listagem de Compras

```python
import requests

url = "http://localhost:8000/api/pncp/compras/listagem/"
params = {
    "codigo_unidade": "123456",
    "ano_compra": 2024
}

response = requests.get(url, params=params)
data = response.json()

if response.status_code == 200:
    print(f"Total de compras: {data['count']}")
    for compra in data['results']:
        print(f"- {compra['numero_compra']}: {compra['objeto_compra']}")
else:
    print(f"Erro: {data.get('error', 'Erro desconhecido')}")
```

#### Endpoint 3 - Unidades por Ano

```python
import requests

url = "http://localhost:8000/api/pncp/unidades/por-ano/"
params = {
    "ano_compra": 2024
}

response = requests.get(url, params=params)
data = response.json()

if response.status_code == 200:
    print(f"Ano: {data['ano_compra']}")
    print(f"Total de unidades: {data['count']}")
    for unidade in data['results']:
        print(f"- {unidade['codigo_unidade']}: {unidade['quantidade_compras']} compras")
        print(f"  Valor Total Homologado: {unidade['valor_total_homologado']}")
else:
    print(f"Erro: {data.get('error', 'Erro desconhecido')}")
```

#### Endpoint 4 - Anos e Unidades para Combobox

```python
import requests

url = "http://localhost:8000/api/pncp/combo/anos-unidades/"

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    print("Anos disponíveis:", data['anos'])
    print("\nUnidades por ano:")
    for ano, unidades in data['unidades_por_ano'].items():
        print(f"  {ano}: {len(unidades)} unidades")
        for unidade in unidades:
            sigla = unidade.get('sigla_om', 'N/A')
            print(f"    - {unidade['codigo_unidade']} ({sigla})")
else:
    print(f"Erro: {data.get('error', 'Erro desconhecido')}")
```

#### Endpoint 3 - Unidades por Ano

```bash
curl -X GET "http://localhost:8000/api/pncp/unidades/por-ano/?ano_compra=2024" \
  -H "Accept: application/json"
```

### Python (requests)

#### Endpoint 1 - Compra Detalhada

```javascript
const url = new URL('http://localhost:8000/api/pncp/compras/detalhada/');
url.searchParams.append('codigo_unidade', '123456');
url.searchParams.append('numero_compra', '001/2024');
url.searchParams.append('ano_compra', '2024');
url.searchParams.append('modalidade', '1');

fetch(url)
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error('Erro:', data.error);
    } else {
      console.log('Sequencial:', data.sequencial_compra);
      console.log('Objeto:', data.objeto_compra);
      console.log('Valor Total Homologado:', data.valor_total_homologado);
      console.log('Itens:', data.itens.length);
    }
  })
  .catch(error => console.error('Erro na requisição:', error));
```

#### Endpoint 2 - Listagem de Compras

```javascript
const url = new URL('http://localhost:8000/api/pncp/compras/listagem/');
url.searchParams.append('codigo_unidade', '123456');
url.searchParams.append('ano_compra', '2024');

fetch(url)
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error('Erro:', data.error);
    } else {
      console.log('Total de compras:', data.count);
      data.results.forEach(compra => {
        console.log(`- ${compra.numero_compra}: ${compra.objeto_compra}`);
      });
    }
  })
  .catch(error => console.error('Erro na requisição:', error));
```

#### Endpoint 3 - Unidades por Ano

```javascript
const url = new URL('http://localhost:8000/api/pncp/unidades/por-ano/');
url.searchParams.append('ano_compra', '2024');

fetch(url)
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error('Erro:', data.error);
    } else {
      console.log('Ano:', data.ano_compra);
      console.log('Total de unidades:', data.count);
      data.results.forEach(unidade => {
        console.log(`- ${unidade.codigo_unidade}: ${unidade.quantidade_compras} compras`);
        console.log(`  Valor Total Homologado: ${unidade.valor_total_homologado}`);
      });
    }
  })
  .catch(error => console.error('Erro na requisição:', error));
```

#### Endpoint 4 - Anos e Unidades para Combobox

```javascript
fetch('http://localhost:8000/api/pncp/combo/anos-unidades/')
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error('Erro:', data.error);
    } else {
      console.log('Anos disponíveis:', data.anos);
      console.log('\nUnidades por ano:');
      Object.entries(data.unidades_por_ano).forEach(([ano, unidades]) => {
        console.log(`  ${ano}: ${unidades.length} unidades`);
        unidades.forEach(unidade => {
          const sigla = unidade.sigla_om || 'N/A';
          console.log(`    - ${unidade.codigo_unidade} (${sigla})`);
        });
      });
      
      // Exemplo de uso para preencher combobox
      // Preencher combobox de anos
      const anoSelect = document.getElementById('ano-select');
      data.anos.forEach(ano => {
        const option = document.createElement('option');
        option.value = ano;
        option.textContent = ano;
        anoSelect.appendChild(option);
      });
      
      // Preencher combobox de unidades quando ano for selecionado
      const unidadeSelect = document.getElementById('unidade-select');
      anoSelect.addEventListener('change', (e) => {
        const anoSelecionado = e.target.value;
        unidadeSelect.innerHTML = ''; // Limpar opções anteriores
        data.unidades_por_ano[anoSelecionado].forEach(unidade => {
          const option = document.createElement('option');
          option.value = unidade.codigo_unidade;
          const displayText = unidade.sigla_om 
            ? `${unidade.codigo_unidade} - ${unidade.sigla_om}`
            : unidade.codigo_unidade;
          option.textContent = displayText;
          unidadeSelect.appendChild(option);
        });
      });
    }
  })
  .catch(error => console.error('Erro na requisição:', error));
```

### Postman

#### Endpoint 1 - Compra Detalhada

1. Método: `GET`
2. URL: `http://localhost:8000/api/pncp/compras/detalhada/`
3. Params:
   - `codigo_unidade`: `123456`
   - `numero_compra`: `001/2024`
   - `ano_compra`: `2024`
   - `modalidade`: `1`

#### Endpoint 2 - Listagem de Compras

1. Método: `GET`
2. URL: `http://localhost:8000/api/pncp/compras/listagem/`
3. Params:
   - `codigo_unidade`: `123456`
   - `ano_compra`: `2024`

#### Endpoint 3 - Unidades por Ano

1. Método: `GET`
2. URL: `http://localhost:8000/api/pncp/unidades/por-ano/`
3. Params:
   - `ano_compra`: `2024`

#### Endpoint 4 - Anos e Unidades para Combobox

1. Método: `GET`
2. URL: `http://localhost:8000/api/pncp/combo/anos-unidades/`
3. Params: Nenhum

---

## Notas Importantes

1. **API Pública**: Todos os endpoints são públicos e não requerem autenticação.

2. **Endpoint de Combobox**: O endpoint 4 (`/combo/anos-unidades/`) é otimizado para uso em interfaces, retornando uma estrutura hierárquica que facilita o preenchimento de comboboxes dependentes (ano → unidade).

2. **Parâmetros Obrigatórios**: Todos os parâmetros especificados são obrigatórios. A ausência de qualquer parâmetro resultará em erro 400.

3. **Tipos de Dados**:
   - `codigo_unidade` e `numero_compra` são strings
   - `ano_compra` e `modalidade` são números inteiros

4. **Ordenação**: 
   - O endpoint de listagem retorna as compras ordenadas por `sequencial_compra` em ordem decrescente (mais recentes primeiro).
   - O endpoint de unidades por ano retorna as unidades ordenadas por `codigo_unidade` em ordem crescente.

5. **Relacionamentos**: 
   - O endpoint de compra detalhada inclui automaticamente os itens da compra e seus resultados (fornecedores).
   - Os itens são retornados com todos os seus resultados associados.

6. **Valores Nulos**: Alguns campos podem retornar `null` se não estiverem disponíveis no banco de dados (ex: `valor_total_homologado`, `percentual_desconto`).

7. **Agregações**: 
   - O endpoint de unidades por ano retorna informações agregadas (quantidade de compras, valores totais) para cada unidade no ano especificado.

8. **Combobox**: 
   - O endpoint de anos e unidades retorna dados prontos para uso em comboboxes, com anos ordenados decrescentemente e unidades ordenadas alfabeticamente.
   - A estrutura `unidades_por_ano` usa strings como chaves (anos) para facilitar o acesso via JavaScript.
   - Cada unidade inclui `codigo_unidade` e `sigla_om` (obtida do modelo Uasg), permitindo exibir informações mais completas nos comboboxes.

---

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `400 Bad Request`: Parâmetros inválidos ou ausentes
- `404 Not Found`: Compra não encontrada (apenas endpoint 1)
- `500 Internal Server Error`: Erro interno do servidor
