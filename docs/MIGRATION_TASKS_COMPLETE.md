# Plano Completo de Tarefas - Migração PyQt6 → Django + Angular + PostgreSQL

Este documento detalha todas as tarefas necessárias para migrar o aplicativo desktop PyQt6 (SQLite + JSON) para uma aplicação web Django + Angular + PostgreSQL usando Docker Compose.

**Foco inicial:** Backend Django (frontend Angular será implementado posteriormente)

---

## Fase 1: Preparação de Infraestrutura (Docker Compose)

### 1.1. Configuração do Docker Compose
- [ ] **Atualizar `docker-compose.yml`** com serviços:
  - `postgres`: Banco de dados PostgreSQL
    - Volume nomeado: `postgres_data`
    - Variáveis: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
    - Porta: `5432`
  - `backend`: Serviço Django
    - Build a partir de `backend/Dockerfile`
    - Depende de `postgres`
    - Porta: `8000`
    - Volumes: código fonte e arquivos estáticos
  - `frontend`: Serviço Angular (preparação futura)
    - Build a partir de `frontend/Dockerfile`
    - Porta: `4200` (dev) ou `80` (prod)
  - `nginx`: Reverse proxy (opcional para produção)
    - Configuração em `nginx/nginx.conf`

### 1.2. Dockerfile do Backend
- [ ] **Criar/atualizar `backend/Dockerfile`**:
  - Base: `python:3.11-slim`
  - Instalar dependências do `requirements.txt`
  - Copiar código do backend
  - Executar `python manage.py migrate` na inicialização
  - Executar `python manage.py collectstatic --noinput`
  - Comando padrão: `gunicorn django_licitacao360.wsgi:application --bind 0.0.0.0:8000`

### 1.3. Variáveis de Ambiente
- [ ] **Criar `.env.example`** com:
  - `POSTGRES_DB=appdb`
  - `POSTGRES_USER=postgres`
  - `POSTGRES_PASSWORD=postgres`
  - `DJANGO_SECRET_KEY=...`
  - `DJANGO_DEBUG=True`
  - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
  - `DATABASE_URL=postgresql://postgres:postgres@db:5432/appdb`
- [ ] **Criar `.env`** (não versionado) a partir do exemplo
- [ ] **Atualizar `settings.py`** para usar `django-environ` ou `python-decouple`

### 1.4. Documentação de Infraestrutura
- [ ] **Criar `docs/DEPLOYMENT.md`** com:
  - Comandos: `docker compose up`, `docker compose down`
  - Comandos úteis: `docker compose exec backend python manage.py shell`
  - Como acessar logs: `docker compose logs -f backend`
  - Como fazer backup do PostgreSQL: `docker compose exec postgres pg_dump -U postgres appdb > backup.sql`

---

## Fase 2: Estruturação do Backend Django

### 2.1. App de Gestão de Contratos
- [ ] **Verificar estrutura do app `gestao_contratos`**:
  - Localização: `backend/django_licitacao360/apps/gestao_contratos/`
  - Verificar se está registrado em `INSTALLED_APPS`
- [ ] **Criar estrutura de diretórios**:
  ```
  gestao_contratos/
  ├── models/
  │   ├── __init__.py
  │   ├── uasg.py
  │   ├── contrato.py
  │   ├── status.py
  │   ├── links.py
  │   ├── fiscalizacao.py
  │   ├── historico.py
  │   ├── empenho.py
  │   ├── item.py
  │   └── arquivo.py
  ├── serializers/
  │   ├── __init__.py
  │   └── ...
  ├── views/
  │   ├── __init__.py
  │   └── ...
  ├── services/
  │   ├── __init__.py
  │   └── ingestion.py
  └── management/
      └── commands/
          ├── __init__.py
          ├── migrate_from_sqlite.py
          └── sync_comprasnet.py
  ```

### 2.2. App de Gestão de Atas
- [ ] **Criar app `gestao_atas`** (ou incluir em `gestao_contratos`):
  - Models: `Ata`, `StatusAta`, `RegistroAta`, `LinksAta`, `FiscalizacaoAta`
  - Seguir mesma estrutura do app de contratos

### 2.3. URLs e Roteamento
- [ ] **Verificar `backend/django_licitacao360/urls.py`**:
  - Rota `api/contratos/` já existe e aponta para `gestao_contratos.urls`
- [ ] **Criar `gestao_contratos/urls.py`** com:
  - `api/contratos/` → listagem e CRUD
  - `api/contratos/<id>/` → detalhes
  - `api/contratos/<id>/status/` → status
  - `api/contratos/<id>/historico/` → histórico
  - `api/contratos/<id>/empenhos/` → empenhos
  - `api/contratos/<id>/itens/` → itens
  - `api/contratos/<id>/arquivos/` → arquivos
  - `api/contratos/<id>/links/` → links
  - `api/contratos/<id>/fiscalizacao/` → fiscalização
- [ ] **Criar `gestao_atas/urls.py`** (se app separado) com rotas equivalentes

### 2.4. Configuração DRF
- [ ] **Verificar configuração do DRF** em `settings.py`:
  - Autenticação JWT já configurada
  - Paginação configurada (100 itens por página)
  - Filtros (`django_filters`) configurados
- [ ] **Adicionar versionamento de API** (`/api/v1/...`)
- [ ] **Configurar CORS** para aceitar requisições do Angular (já configurado)

---

## Fase 3: Modelagem de Dados (PostgreSQL)

### 3.1. Models de Contratos
- [ ] **Criar `models/uasg.py`**:
  - Model `Uasg` conforme guia completo
  - Campos: `uasg_code` (PK), `nome_resumido`
- [ ] **Criar `models/contrato.py`**:
  - Model `Contrato` conforme guia completo
  - Todos os campos mapeados do SQLite
  - Conversões: TEXT → DateField, TEXT → DecimalField, TEXT → JSONField
  - Campo `manual` incluído
- [ ] **Criar `models/status.py`**:
  - `StatusContrato` (1:1 com Contrato)
  - `RegistroStatus` (N:1 com Contrato)
  - `RegistroMensagem` (N:1 com Contrato)
- [ ] **Criar `models/links.py`**:
  - `LinksContrato` (1:1 com Contrato)
- [ ] **Criar `models/fiscalizacao.py`**:
  - `FiscalizacaoContrato` (1:1 com Contrato)
  - Campos de timestamps convertidos para DateTimeField
- [ ] **Criar `models/historico.py`**:
  - `HistoricoContrato` (N:1 com Contrato)
- [ ] **Criar `models/empenho.py`**:
  - `Empenho` (N:1 com Contrato)
- [ ] **Criar `models/item.py`**:
  - `ItemContrato` (N:1 com Contrato)
- [ ] **Criar `models/arquivo.py`**:
  - `ArquivoContrato` (N:1 com Contrato)

### 3.2. Models de Atas
- [ ] **Criar models de atas**:
  - `Ata` (tabela principal)
  - `StatusAta` (1:1 com Ata)
  - `RegistroAta` (N:1 com Ata)
  - `LinksAta` (1:1 com Ata)
  - `FiscalizacaoAta` (1:1 com Ata)

### 3.3. Models de Dados Manuais
- [ ] **Criar `models/dados_manuais.py`**:
  - `DadosManuaisContrato` (1:1 com Contrato)
  - Campos: `sigla_om_resp`, `orgao_responsavel`, `portaria`, `created_by`

### 3.4. Índices e Constraints
- [ ] **Adicionar índices** conforme guia completo:
  - Índices em `contrato_id` em todas as tabelas relacionadas
  - Índices compostos para buscas frequentes
- [ ] **Adicionar UniqueConstraints**:
  - `RegistroStatus`: unique em `(contrato, texto)`
  - `RegistroMensagem`: unique em `texto`
- [ ] **Adicionar validações**:
  - `clean()` methods nos models principais
  - Validação de datas (vigência)
  - Validação de valores monetários

### 3.5. Migrações
- [ ] **Criar migrações iniciais**:
  - `python manage.py makemigrations gestao_contratos`
  - `python manage.py makemigrations gestao_atas` (se app separado)
- [ ] **Aplicar migrações**:
  - `python manage.py migrate`
- [ ] **Validar schema**:
  - Verificar se todas as tabelas foram criadas
  - Verificar índices e constraints

### 3.6. Admin Django
- [ ] **Registrar models no admin**:
  - `admin.py` para cada app
  - Configurar `list_display`, `list_filter`, `search_fields`
  - Adicionar ações customizadas (ex: exportar para JSON)

---

## Fase 4: Serviço de Ingestão (API ComprasNet)

### 4.1. Serviço de Ingestão
- [ ] **Criar `services/ingestion.py`**:
  - Migrar lógica do `OfflineDBController.process_and_save_all_data()`
  - Função `sync_contratos_por_uasg(uasg_code: str)`
  - Função `sync_contrato_detalhes(contrato_id: str)`
  - Função `sync_todos_contratos()`
- [ ] **Implementar filtro de vigência**:
  - Contratos sem `vigencia_fim` → incluir
  - Contratos com `vigencia_fim` até 100 dias atrás → incluir
  - Lógica existente em `offline_db_model.py`
- [ ] **Implementar salvamento de dados offline**:
  - `sync_historico(contrato_id)`
  - `sync_empenhos(contrato_id)`
  - `sync_itens(contrato_id)`
  - `sync_arquivos(contrato_id)`
- [ ] **Implementar retentativas**:
  - 3 tentativas por requisição
  - Timeout de 20 segundos
  - Log de erros

### 4.2. Management Commands
- [ ] **Criar `management/commands/sync_comprasnet.py`**:
  - Comando: `python manage.py sync_comprasnet --uasg 787010`
  - Comando: `python manage.py sync_comprasnet --all`
  - Opções: `--force` (sobrescrever dados existentes)
  - Progress bar usando `tqdm` ou similar
- [ ] **Criar `management/commands/migrate_from_sqlite.py`**:
  - Comando: `python manage.py migrate_from_sqlite --db-path /path/to/gerenciador_uasg.db`
  - Migrar todos os dados do SQLite para PostgreSQL
  - Validar integridade dos dados migrados
  - Log de progresso e erros

### 4.3. Tarefas Assíncronas (Celery - Opcional)
- [ ] **Configurar Celery** (se necessário):
  - Broker: Redis ou RabbitMQ
  - Tasks para sincronização periódica
  - Task para sincronização por UASG
- [ ] **Criar `tasks/sync_tasks.py`**:
  - `sync_contratos_async(uasg_code)`
  - `sync_contrato_detalhes_async(contrato_id)`

### 4.4. Tratamento de Contratos Manuais
- [ ] **Implementar lógica para contratos manuais**:
  - Flag `manual=True` em contratos criados manualmente
  - Endpoint para criar contrato manual via API
  - Validação: IDs manuais começam com `MANUAL-{uasg}-{numero}`
  - Campos adicionais salvos em `DadosManuaisContrato`

---

## Fase 5: APIs e Funcionalidades de Negócio

### 5.1. Serializers DRF
- [ ] **Criar serializers para Contrato**:
  - `ContratoSerializer` (listagem)
  - `ContratoDetailSerializer` (detalhes completos)
  - `ContratoCreateSerializer` (criação manual)
  - `ContratoUpdateSerializer` (atualização)
- [ ] **Criar serializers para Status**:
  - `StatusContratoSerializer`
  - `RegistroStatusSerializer`
  - `RegistroMensagemSerializer`
- [ ] **Criar serializers para Links e Fiscalização**:
  - `LinksContratoSerializer`
  - `FiscalizacaoContratoSerializer`
- [ ] **Criar serializers para Dados Offline**:
  - `HistoricoContratoSerializer`
  - `EmpenhoSerializer`
  - `ItemContratoSerializer`
  - `ArquivoContratoSerializer`
- [ ] **Criar serializers para Atas** (se app separado):
  - Serializers equivalentes para todos os models de atas

### 5.2. ViewSets e Views
- [ ] **Criar `views/contrato_views.py`**:
  - `ContratoViewSet` (CRUD completo)
  - Filtros: `uasg`, `status`, `vigencia_fim`, `manual`
  - Ordenação: `vigencia_fim`, `numero`
- [ ] **Criar `views/status_views.py`**:
  - `StatusContratoViewSet`
  - `RegistroStatusViewSet`
  - `RegistroMensagemViewSet`
- [ ] **Criar `views/links_views.py`**:
  - `LinksContratoViewSet`
- [ ] **Criar `views/fiscalizacao_views.py`**:
  - `FiscalizacaoContratoViewSet`
- [ ] **Criar `views/offline_views.py`**:
  - `HistoricoContratoViewSet`
  - `EmpenhoViewSet`
  - `ItemContratoViewSet`
  - `ArquivoContratoViewSet`
- [ ] **Criar views agregadas**:
  - `ContratoDetalhesView`: Retorna contrato + status + registros + links + fiscalização + dados offline em uma única resposta

### 5.3. Endpoints Específicos
- [ ] **Criar endpoints de sincronização**:
  - `POST /api/contratos/sync/` → Sincronizar todos os contratos
  - `POST /api/contratos/sync/<uasg>/` → Sincronizar por UASG
  - `POST /api/contratos/<id>/sync-detalhes/` → Sincronizar detalhes de um contrato
- [ ] **Criar endpoints de exportação/importação**:
  - `GET /api/contratos/export/` → Exportar status para JSON (equivalente a GERAL.json)
  - `POST /api/contratos/import/` → Importar status de JSON
  - `GET /api/contratos/manuais/export/` → Exportar contratos manuais
  - `POST /api/contratos/manuais/import/` → Importar contratos manuais

### 5.4. Autenticação e Permissões
- [ ] **Configurar permissões**:
  - Leitura: `AllowAny` ou `IsAuthenticated`
  - Escrita: `IsAuthenticated` + permissões customizadas
  - Exemplo: Apenas usuários com perfil "Gestor" podem alterar status/links
- [ ] **Criar grupos de usuários**:
  - `Gestor`: Pode criar/editar/deletar contratos e status
  - `Visualizador`: Apenas leitura
  - `Fiscal`: Pode editar fiscalização

### 5.5. Filtros e Buscas
- [ ] **Implementar filtros avançados**:
  - Por UASG
  - Por status
  - Por vigência (vencidos, próximos a vencer, ativos)
  - Por fornecedor (CNPJ ou nome)
  - Por processo
  - Por valor (faixa)
- [ ] **Implementar busca textual**:
  - Busca em `objeto`, `numero`, `processo`, `fornecedor_nome`
  - Usar `SearchVector` do PostgreSQL para busca full-text

---

## Fase 6: Migração de Dados JSON

### 6.1. Script de Migração de Contratos Manuais
- [ ] **Criar script** `management/commands/migrate_contratos_manuais.py`:
  - Ler `jsons/contratos_manuais.json`
  - Para cada contrato:
    - Criar `Contrato` com `manual=True`
    - Criar `DadosManuaisContrato` com campos adicionais
    - Criar `StatusContrato` se houver `portaria_edit`
  - Validar IDs únicos
  - Log de progresso

### 6.2. Script de Migração de Status (GERAL.json)
- [ ] **Criar script** `management/commands/migrate_status_contratos.py`:
  - Ler `jsons/GERAL.json`
  - Para cada entrada:
    - Validar `data_registro` antes de atualizar (lógica existente)
    - Criar/atualizar `StatusContrato`
    - Criar/atualizar `LinksContrato`
    - Criar/atualizar `FiscalizacaoContrato`
    - Criar registros em `RegistroStatus` e `RegistroMensagem`
  - Validar relacionamentos (contrato deve existir)

### 6.3. Script de Migração de Atas
- [ ] **Criar script** `management/commands/migrate_atas.py`:
  - Ler `jsons/atas_principais-submend.json`
  - Importar atas principais
  - Ler `jsons/atas_complementares-submend.json`
  - Importar status, registros, links e fiscalização
  - Validar `ata_parecer` antes de criar relacionamentos

### 6.4. Script de Migração do SQLite
- [ ] **Criar script** `management/commands/migrate_from_sqlite.py`:
  - Conectar ao SQLite (`gerenciador_uasg.db`)
  - Migrar tabela `uasgs`
  - Migrar tabela `contratos`
  - Migrar tabelas de status (`status_contratos`, `registros_status`, etc.)
  - Migrar tabelas offline (`historico`, `empenhos`, `itens`, `arquivos`)
  - Migrar tabela `fiscalizacao` (se existir)
  - Converter tipos de dados (TEXT → DateField, TEXT → DecimalField)
  - Validar integridade referencial
  - Log detalhado de progresso e erros

---

## Fase 7: Qualidade, Observabilidade e Segurança

### 7.1. Testes Unitários
- [ ] **Criar testes para models**:
  - `tests/test_models.py`
  - Testar criação de contratos, status, links, etc.
  - Testar relacionamentos e cascade
  - Testar validações
- [ ] **Criar testes para serializers**:
  - `tests/test_serializers.py`
  - Testar serialização e deserialização
- [ ] **Criar testes para views**:
  - `tests/test_views.py`
  - Testar endpoints CRUD
  - Testar filtros e buscas
- [ ] **Criar testes para serviços**:
  - `tests/test_services.py`
  - Testar ingestão de dados da API ComprasNet (mock)
  - Testar migração de dados

### 7.2. Testes de Integração
- [ ] **Criar testes de integração**:
  - `tests/test_integration.py`
  - Testar fluxo completo: criar contrato → adicionar status → adicionar registros
  - Testar sincronização com API externa (mock)

### 7.3. Validações Automáticas
- [ ] **Configurar linting**:
  - `flake8` ou `ruff`
  - `black` para formatação
  - `isort` para ordenação de imports
  - `mypy` para type checking (opcional)
- [ ] **Configurar pre-commit hooks**:
  - Executar linting antes de commit
  - Executar testes antes de commit

### 7.4. Observabilidade
- [ ] **Adicionar logging estruturado**:
  - Configurar `logging` do Python
  - Logs de sincronização, migração, erros
- [ ] **Adicionar métricas** (opcional):
  - Prometheus metrics
  - Contadores: contratos sincronizados, erros de API, etc.
- [ ] **Health check**:
  - Endpoint `/api/health/` já existe
  - Adicionar verificação de conexão com PostgreSQL
  - Adicionar verificação de última sincronização

### 7.5. Segurança
- [ ] **Revisar configurações de segurança**:
  - `SECRET_KEY` em variável de ambiente
  - `DEBUG=False` em produção
  - `ALLOWED_HOSTS` configurado
  - CORS configurado corretamente
- [ ] **Implementar rate limiting**:
  - Limitar requisições de sincronização
  - Limitar criação de contratos manuais
- [ ] **Validação de entrada**:
  - Validar todos os inputs dos serializers
  - Sanitizar dados de arquivos JSON importados

### 7.6. Backup e Recuperação
- [ ] **Script de backup**:
  - `scripts/backup_postgres.sh`
  - Backup diário do PostgreSQL
  - Retenção de 30 dias
- [ ] **Script de restore**:
  - `scripts/restore_postgres.sh`
  - Restaurar backup do PostgreSQL

---

## Fase 8: Documentação e Entregáveis

### 8.1. Documentação de API
- [ ] **Gerar documentação OpenAPI/Swagger**:
  - Usar `drf-spectacular` ou `drf-yasg`
  - Endpoint `/api/schema/swagger-ui/`
  - Documentar todos os endpoints
  - Exemplos de requisições/respostas

### 8.2. Documentação de Models
- [ ] **Criar documentação dos models**:
  - `docs/MODELS.md`
  - Descrição de cada model
  - Relacionamentos
  - Campos importantes

### 8.3. Fixtures de Exemplo
- [ ] **Criar fixtures**:
  - `fixtures/contratos_exemplo.json`
  - `fixtures/atas_exemplo.json`
  - Dados de exemplo para desenvolvimento e testes
- [ ] **Comando para carregar fixtures**:
  - `python manage.py loaddata fixtures/contratos_exemplo.json`

### 8.4. Guia de Migração
- [ ] **Criar `docs/MIGRATION_GUIDE.md`**:
  - Passo a passo para migrar dados do SQLite
  - Passo a passo para migrar dados JSON
  - Troubleshooting comum
  - Rollback procedures

### 8.5. README do Backend
- [ ] **Atualizar `backend/README.md`**:
  - Como executar localmente
  - Como executar com Docker
  - Como executar migrações
  - Como executar sincronização
  - Estrutura do projeto

---

## Fase 9: Otimizações e Melhorias

### 9.1. Performance
- [ ] **Otimizar queries**:
  - Usar `select_related()` e `prefetch_related()` nas views
  - Adicionar índices adicionais conforme necessário
  - Analisar queries lentas com `django-debug-toolbar`
- [ ] **Cache**:
  - Cache de listagens de contratos (Redis)
  - Cache de dados de UASGs
  - Invalidar cache ao atualizar dados

### 9.2. Paginação
- [ ] **Otimizar paginação**:
  - Usar `CursorPagination` para grandes volumes
  - Configurar tamanho de página adequado

### 9.3. Processamento Assíncrono
- [ ] **Implementar Celery** (se necessário):
  - Tasks para sincronização periódica
  - Tasks para processamento de grandes volumes
  - Monitoramento com Flower

---

## Checklist Final

### Antes de Considerar Backend Completo

- [ ] Todos os models criados e migrados
- [ ] Todos os endpoints implementados e testados
- [ ] Migração de dados do SQLite funcionando
- [ ] Migração de dados JSON funcionando
- [ ] Sincronização com API ComprasNet funcionando
- [ ] Testes unitários e de integração passando
- [ ] Documentação completa
- [ ] Docker Compose funcionando
- [ ] Health checks implementados
- [ ] Logging configurado
- [ ] Backup configurado

---

## Próximos Passos (Frontend Angular)

Após conclusão do backend:

1. Criar serviços Angular para consumir APIs
2. Criar componentes para listagem de contratos
3. Criar componentes para detalhes de contratos
4. Criar formulários para criação/edição
5. Implementar sincronização no frontend
6. Implementar exportação/importação de dados

---

**Nota:** Este plano é abrangente e pode ser executado incrementalmente. Priorize as fases 1-4 para ter um backend funcional básico, depois avance para as demais fases conforme necessário.

