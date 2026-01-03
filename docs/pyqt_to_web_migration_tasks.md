# Plano de tarefas para construir o novo backend Django + Angular + PostgreSQL

> **⚠️ ATENÇÃO:** Este documento foi substituído por uma versão completa e detalhada. Consulte **[MIGRATION_TASKS_COMPLETE.md](./MIGRATION_TASKS_COMPLETE.md)** para o plano completo de migração com todas as tarefas detalhadas.

Este documento contém um plano básico de tarefas. Para uma versão completa e detalhada, consulte o documento referenciado acima.

## 1. Preparação de infraestrutura (Docker Compose)
- [ ] Atualizar/crear `docker-compose.yml` com serviços `postgres`, `backend` (Django), `frontend` (Angular builder) e `nginx`/`caddy` (reverse proxy), definindo redes e volumes nomeados.
- [ ] Criar Dockerfile do backend que instale dependências, copie o código e execute `python manage.py migrate && python manage.py collectstatic --noinput`.
- [ ] Preparar imagem Angular (mesmo que o frontend seja implementado depois) para liberar a porta e permitir testes de integração.
- [ ] Configurar variáveis sensíveis via `.env` (credenciais do Postgres, secret key, hosts permitidos).
- [ ] Documentar comandos (`docker compose up`, `docker compose exec backend python manage.py shell`) para onboarding.

## 2. Estruturação do backend Django
- [ ] Criar app dedicado (ex.: `django_licitacao360.apps.gestao_contratos`) e registrá-lo em `INSTALLED_APPS`.
- [ ] Atualizar `django_licitacao360/urls.py` para incluir `path('api/contratos/', include('django_licitacao360.apps.gestao_contratos.urls'))` e outras rotas necessárias (`atas`, `offline`, etc.).
- [ ] Configurar DRF (caso ainda não esteja no projeto) ou revisar settings existentes para habilitar autenticação JWT usada pelo restante do backend.
- [ ] Definir versionamento de API (`/api/v1/...`) e middleware de CORS para o futuro frontend Angular.

## 3. Modelagem de dados (PostgreSQL)
- [ ] Implementar os models descritos em `docs/django_models_guidance.md`, incluindo: `Uasg`, `Contrato`, `StatusContrato`, `RegistroStatus`, `RegistroMensagem`, `LinksContrato`, `FiscalizacaoContrato`, `HistoricoContrato`, `Empenho`, `ItemContrato`, `ArquivoContrato`, `AtaPrincipal`, `StatusAta` (ou estrutura equivalente).
- [ ] Adicionar campos de auditoria (`created_at`, `updated_at`, `created_by`, `updated_by`) e constraints (`UniqueConstraint`, índices) para replicar as validações do SQLite.
- [ ] Criar migrations e validar `python manage.py makemigrations gestao_contratos && python manage.py migrate`.
- [ ] Registrar os models relevantes no admin Django para facilitar conferência manual dos dados importados.

## 4. Serviço de ingestão (API ComprasNet)
- [ ] Reescrever a lógica do `OfflineDBController` como um serviço Django (management command + Celery beat/task) que consulta os endpoints públicos do ComprasNet, aplica os mesmos filtros por vigência e salva os dados completos (contratos, históricos, empenhos, itens, arquivos) no PostgreSQL.
- [ ] Persistir `raw_json` em todas as entidades relevantes e manter os laços 1:1 / 1:N descritos no guia.
- [ ] Permitir execução por UASG ou em lote, com logs de progresso, cancelamento e retentativas configuráveis.
- [ ] Expor parâmetros para distinguir contratos manuais dos importados via API, garantindo que o fluxo manual use os mesmos models.
- [ ] Criar testes que simulem respostas da API pública/local para garantir fidelidade à lógica atual.

## 5. APIs e funcionalidades de negócio
- [ ] Expor endpoints REST para: listar/filtrar contratos (por `uasg`, `status`, vigência, manual/API), CRUD de status/registro, CRUD das tabelas offline (histórico, empenhos, itens, arquivos), administração de fiscalizações e atas.
- [ ] Criar endpoints para upload e associação de arquivos complementares quando a API pública não o fornecer.
- [ ] Disponibilizar endpoints agregados para o Angular (ex.: `/api/contratos/<id>/detalhes` trazendo contrato + status + registros + offline data em uma única resposta).
- [ ] Integrar autenticação (JWT) e permissões (ex.: somente usuários com perfil “Gestor” alteram status/links).

## 6. Qualidade, observabilidade e segurança
- [ ] Configurar validações automáticas (flake8/black/isort/mypy ou equivalente) e pipeline CI para o backend.
- [ ] Escrever testes unitários e de API cobrindo models, serializers e views principais.
- [ ] Adicionar monitoramento básico (health-check existente em `/api/health/`, métricas Prometheus ou logs estruturados).
- [ ] Implementar backups e seeds do banco: `pg_dump` periódico + script para carregar dados de demonstração.

## 7. Entregáveis prévios ao frontend Angular
- [ ] Documentar todos os endpoints disponíveis (OpenAPI/Swagger gerado pelo DRF ou `drf-spectacular`), para que o time de frontend consuma posteriormente.
- [ ] Criar fixtures de exemplo (contrato completo, status, histórico) para que o Angular possa trabalhar desacoplado do banco real.
- [ ] Garantir CORS configurado para aceitar o domínio/localhost do Angular.

Seguir este checklist garante que o backend Django, já rodando em Docker com PostgreSQL, espelhe toda a lógica do aplicativo PyQt e exponha as APIs necessárias para a futura interface Angular.
