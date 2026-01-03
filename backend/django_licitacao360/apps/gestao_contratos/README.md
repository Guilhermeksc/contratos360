# App de Gestão de Contratos

Este app Django gerencia contratos administrativos, UASGs e dados relacionados.

## Estrutura

```
gestao_contratos/
├── models/              # Models Django
│   ├── uasg.py
│   ├── contrato.py
│   ├── status.py
│   ├── links.py
│   ├── fiscalizacao.py
│   ├── historico.py
│   ├── empenho.py
│   ├── item.py
│   ├── arquivo.py
│   └── dados_manuais.py
├── serializers/         # Serializers DRF
├── views/               # ViewSets e Views
├── services/            # Serviços de negócio
│   └── ingestion.py     # Ingestão da API ComprasNet
├── management/          # Management commands
│   └── commands/
│       ├── sync_comprasnet.py
│       └── migrate_from_sqlite.py
└── urls.py              # Rotas da API
```

## Models

### Principais
- **Uasg**: Unidade Administrativa com Suporte Gerencial
- **Contrato**: Contratos administrativos
- **StatusContrato**: Status e informações editadas de contratos
- **RegistroStatus**: Registros cronológicos de status
- **RegistroMensagem**: Mensagens relacionadas a contratos
- **LinksContrato**: Links relacionados a contratos
- **FiscalizacaoContrato**: Dados de fiscalização

### Dados Offline (Cache de APIs)
- **HistoricoContrato**: Histórico de contratos
- **Empenho**: Empenhos relacionados
- **ItemContrato**: Itens dos contratos
- **ArquivoContrato**: Arquivos relacionados

### Auxiliares
- **DadosManuaisContrato**: Dados adicionais para contratos manuais

## Endpoints da API

### UASGs
- `GET /api/contratos/uasgs/` - Lista UASGs
- `GET /api/contratos/uasgs/{code}/` - Detalhes de uma UASG

### Contratos
- `GET /api/contratos/contratos/` - Lista contratos
- `POST /api/contratos/contratos/` - Cria contrato
- `GET /api/contratos/contratos/{id}/` - Detalhes de um contrato
- `PUT /api/contratos/contratos/{id}/` - Atualiza contrato
- `DELETE /api/contratos/contratos/{id}/` - Deleta contrato
- `GET /api/contratos/contratos/{id}/detalhes/` - Detalhes completos (com dados relacionados)
- `GET /api/contratos/contratos/vencidos/` - Contratos vencidos
- `GET /api/contratos/contratos/proximos_vencer/` - Contratos próximos a vencer (30 dias)
- `GET /api/contratos/contratos/ativos/` - Contratos ativos

### Status
- `GET /api/contratos/status/` - Lista status
- `POST /api/contratos/status/` - Cria status
- `GET /api/contratos/registros-status/` - Lista registros de status
- `GET /api/contratos/registros-mensagem/` - Lista registros de mensagem

### Links e Fiscalização
- `GET /api/contratos/links/` - Lista links
- `GET /api/contratos/fiscalizacao/` - Lista fiscalizações

### Dados Offline
- `GET /api/contratos/historico/` - Lista histórico
- `GET /api/contratos/empenhos/` - Lista empenhos
- `GET /api/contratos/itens/` - Lista itens
- `GET /api/contratos/arquivos/` - Lista arquivos

## Filtros

### Contratos
- `?uasg=787010` - Filtrar por UASG
- `?status=ALERTA PRAZO` - Filtrar por status
- `?manual=true` - Filtrar contratos manuais
- `?vigencia_fim__gte=2025-01-01` - Filtrar por data de fim
- `?fornecedor_cnpj=12345678901234` - Filtrar por CNPJ

### Busca
- `?search=termo` - Busca em número, processo, fornecedor_nome, objeto

### Ordenação
- `?ordering=-vigencia_fim` - Ordenar por data de fim (decrescente)
- `?ordering=numero` - Ordenar por número

## Management Commands

### Sincronizar dados da API ComprasNet

```bash
# Sincronizar uma UASG específica
python manage.py sync_comprasnet --uasg 787010

# Sincronizar todas as UASGs cadastradas
python manage.py sync_comprasnet --all

# Sincronizar detalhes de um contrato específico
python manage.py sync_comprasnet --contrato 210813
```

### Migrar dados do SQLite

```bash
# Migrar dados do SQLite para PostgreSQL
python manage.py migrate_from_sqlite --db-path /path/to/gerenciador_uasg.db

# Dry run (apenas valida, não salva)
python manage.py migrate_from_sqlite --db-path /path/to/gerenciador_uasg.db --dry-run
```

## Migrations

Para criar as migrations iniciais:

```bash
python manage.py makemigrations gestao_contratos
python manage.py migrate gestao_contratos
```

## Admin Django

Todos os models estão registrados no admin Django. Acesse `/admin/` para gerenciar os dados.

## Próximos Passos

1. Criar migrations iniciais: `python manage.py makemigrations gestao_contratos`
2. Aplicar migrations: `python manage.py migrate gestao_contratos`
3. Migrar dados do SQLite: `python manage.py migrate_from_sqlite --db-path /path/to/db.db`
4. Sincronizar dados da API: `python manage.py sync_comprasnet --uasg 787010`

