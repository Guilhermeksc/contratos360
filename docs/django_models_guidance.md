# Guia de Modelagem Django para o domínio de contratos

> **⚠️ ATENÇÃO:** Este documento foi substituído por uma versão completa e detalhada. Consulte **[DJANGO_MODELS_COMPLETE_GUIDE.md](./DJANGO_MODELS_COMPLETE_GUIDE.md)** para a análise minuciosa completa dos models SQLite e orientações detalhadas para criação dos models Django.

Este documento descreve a estrutura persistida hoje pelo aplicativo PyQt (SQLite + JSON) para servir como referência na construção de uma nova base (Django + PostgreSQL). O objetivo é reproduzir a lógica funcional existente — incluindo a ingestão dos dados pela API pública do ComprasNet — em uma aplicação web moderna que futuramente abastecerá um frontend Angular.

## 1. Arquitetura de persistência atual (PyQt + SQLite + JSON)
- O ORM utilizado é SQLAlchemy (`Contratos/model/models.py`). Ele define as tabelas `uasgs`, `contratos`, entidades auxiliares (status, links, fiscalizações etc.) e tabelas de dados offline (histórico, empenhos, itens e arquivos).
- O processo `OfflineDBController` (`Contratos/model/offline_db_model.py`) cria/atualiza o schema e consolida os dados vindos da API pública do ComprasNet, salvando os raw payloads (JSON serializado em texto) em cada registro.
- Parte do estado da aplicação não é gravado no SQLite. A pasta `jsons/` guarda estruturas auxiliares, por exemplo:
  - `GERAL.json`: espelha o status corrente dos contratos, os registros cronológicos e os links trabalhados na GUI.
  - `contratos_manuais.json`: contratos cadastrados manualmente (sem vínculo com a API pública).
  - `atas_principais-submend.json` e `atas_complementares-submend.json`: metadados e status das atas.
  - `test_para_jutars_depois.json`: usado para rascunhos; deve ser tratado como dados temporários.
- O SQLite mantém vários índices (`idx_*_contrato_id`) para acelerar buscas por `contrato_id`. Esses índices devem virar `db_index=True` ou índices compostos nas models Django/PostgreSQL.

## 2. Estrutura das tabelas SQLite

### 2.1. `uasgs`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `uasg_code` | TEXT (PK) | Código textual (ex.: `787010`). |
| `nome_resumido` | TEXT | Nome resumido da UASG. |

### 2.2. `contratos`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | TEXT (PK) | ID fornecido pela API; usado como chave em todas as tabelas filhas. |
| `uasg_code` | TEXT (FK) | FK para `uasgs.uasg_code`, obrigatório. |
| `numero`, `licitacao_numero`, `processo` | TEXT | Identificadores administrativos. |
| `fornecedor_nome`, `fornecedor_cnpj` | TEXT | Dados do fornecedor. |
| `objeto` | TEXT | Descrição do objeto contratual. |
| `valor_global` | TEXT | Valor numérico guardado como string (precisa virar `DecimalField`). |
| `vigencia_inicio`, `vigencia_fim` | TEXT | Datas no formato ISO (`YYYY-MM-DD`). |
| `tipo`, `modalidade` | TEXT | Classificações da contratação. |
| `contratante_orgao_unidade_gestora_codigo` | TEXT | Código UG. |
| `contratante_orgao_unidade_gestora_nome_resumido` | TEXT | Nome UG. |
| `manual` | BOOLEAN | Flag presente no ORM mas **não** criada pela rotina `_create_tables`. Necessário garantir a coluna no novo schema. |
| `raw_json` | TEXT | Snapshot do payload completo do contrato. |

Relacionamentos: `Contrato` possui associações 1:N com `RegistroStatus`, `RegistroMensagem`, `Historico`, `Empenho`, `Item`, `Arquivo` e 1:1 com `StatusContrato`, `LinksContrato` e `Fiscalizacao`.

### 2.3. `status_contratos`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `contrato_id` | TEXT (PK) | Também é FK para `contratos.id`. |
| `uasg_code` | TEXT | Redundância para filtros. |
| `status` | TEXT | Ex.: `ALERTA PRAZO`, `PORTARIA`. |
| `objeto_editado` | TEXT | Texto usado para exibir objeto ajustado. |
| `portaria_edit` | TEXT | Valor exibido em interface. |
| `termo_aditivo_edit` | TEXT | Campo presente no ORM mas faltante na SQL criada; deve existir no novo schema. |
| `radio_options_json` | TEXT | JSON serializado com flags como “Pode Renovar?”, “Custeio?”, etc. |
| `data_registro` | TEXT | Timestamp textual (ex.: `14/10/2025 11:31:45`). |

### 2.4. `registros_status`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK autoincrement) | |
| `contrato_id` | TEXT (FK, indexado) | |
| `uasg_code` | TEXT | |
| `texto` | TEXT (UNIQUE) | Linha formatada “DD/MM/AAAA - mensagem - STATUS”. |

### 2.5. `registro_mensagem`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK autoincrement) | |
| `contrato_id` | TEXT (FK, indexado) | |
| `texto` | TEXT (UNIQUE opcional) | Mensagens soltas ligadas ao contrato. |

### 2.6. `links_contratos`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK) | |
| `contrato_id` | TEXT (FK, UNIQUE) | Garante relacionamento 1:1. |
| `link_contrato`, `link_ta`, `link_portaria`, `link_pncp_espc`, `link_portal_marinha` | TEXT | URLs para documentos oficiais. |

### 2.7. `fiscalizacao`
*Tabela definida no ORM, mas não criada em `_create_tables`. É necessário incluí-la no novo banco.*
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK autoincrement) | |
| `contrato_id` | TEXT (FK, UNIQUE, indexado) | Ligações 1:1. |
| `gestor`, `gestor_substituto`, `fiscal_tecnico`, `fiscal_tec_substituto`, `fiscal_administrativo`, `fiscal_admin_substituto` | TEXT | Responsáveis e substitutos. |
| `observacoes` | TEXT | Comentários gerais. |
| `data_criacao`, `data_atualizacao` | TEXT | Guardados como string (devem virar `DateTimeField`). |

## 3. Tabelas de dados offline (cache de APIs)

### 3.1. `historico`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK) | |
| `contrato_id` | TEXT (FK, indexado) | |
| `receita_despesa`, `numero`, `observacao`, `ug`, `gestao`, `fornecedor_cnpj`, `fornecedor_nome`, `tipo`, `categoria`, `processo`, `objeto`, `modalidade`, `licitacao_numero` | TEXT | Provenientes dos endpoints históricos. |
| `data_assinatura`, `data_publicacao`, `vigencia_inicio`, `vigencia_fim` | TEXT | Datas no formato ISO. |
| `valor_global` | TEXT | Valor numérico como string. |
| `raw_json` | TEXT | Payload integral da API. |

### 3.2. `empenhos`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK) | |
| `contrato_id` | TEXT (FK, indexado) | |
| `unidade_gestora`, `gestao`, `numero`, `data_emissao`, `credor_cnpj`, `credor_nome` | TEXT | |
| `empenhado`, `liquidado`, `pago` | TEXT | Valores monetários armazenados como string (precisam virar `DecimalField`). |
| `informacao_complementar` | TEXT | Campo livre. |
| `raw_json` | TEXT | Payload integral. |

### 3.3. `itens`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK) | |
| `contrato_id` | TEXT (FK, indexado) | |
| `tipo_id`, `tipo_material`, `grupo_id`, `catmatseritem_id` | TEXT | Classificadores de materiais/serviços. |
| `descricao_complementar` | TEXT | |
| `quantidade`, `valorunitario`, `valortotal` | TEXT | Números guardados como string. |
| `numero_item_compra` | TEXT | |
| `raw_json` | TEXT | Payload integral. |

### 3.4. `arquivos`
| Campo | Tipo | Observações |
| --- | --- | --- |
| `id` | INTEGER (PK) | |
| `contrato_id` | TEXT (FK, indexado) | |
| `tipo`, `descricao` | TEXT | Tipo/descrição do arquivo. |
| `path_arquivo`, `origem`, `link_sei` | TEXT | URLs ou caminhos locais. |
| `raw_json` | TEXT | Payload integral. |

## 4. Conteúdo mantido em arquivos JSON

### 4.1. `jsons/GERAL.json`
- Estrutura: lista de objetos com `contrato_id`, `uasg_code`, `status`, `objeto_editado`, `portaria_edit`, `termo_aditivo_edit`, `radio_options_json`, `data_registro`, `registros` (lista de strings), `registros_mensagem` (lista), além dos links.
- O novo backend deve oferecer models/serializers equivalentes (`StatusContrato`, `RegistroStatus`, `RegistroMensagem`, `LinksContrato`), garantindo endpoints para manter essas informações que hoje ficam em arquivo.

### 4.2. `jsons/contratos_manuais.json`
- Contém contratos que só existem localmente. Cada item replica o formato da API pública, mas inclui `manual = true`, campos específicos (`sigla_om_resp`, `orgao_responsavel`, `portaria`, `portaria_edit`) e `raw_json` simplificado.
- No novo backend, defina um flag em `Contrato` (`manual = models.BooleanField(default=False)`) e garanta que os campos adicionais tenham colunas próprias ou um JSONField dedicado (`dados_manuais`). Inclua ainda rastreabilidade (usuário que criou, timestamps).

### 4.3. `jsons/atas_principais-submend.json`
- Lista de atas com campos (`setor`, `modalidade`, `numero`, `ano`, `empresa`, `contrato_ata_parecer`, `objeto`, `celebracao`, `termino`, `observacoes`, `termo_aditivo`, `portaria_fiscalizacao`).
- Deve inspirar uma nova model `AtaPrincipal` (com `contrato_ata_parecer` único) e fluxos de status equivalentes.

### 4.4. `jsons/atas_complementares-submend.json`
- Mantém um objeto `{ "status_atas": [ ... ] }` que associa `ata_parecer` → `status`.
- Deve virar uma tabela `StatusAta` ou reusar `StatusContrato` com um `ContentType`/GenericForeignKey. Avaliar durante o refinamento dos models.

### 4.5. Demais arquivos
- `test_para_jutars_depois.json` funciona como sandbox; definir estratégia (armazenar como rascunho em tabela separada ou descartar).

## 5. Recomendações para models Django/PostgreSQL

1. **Apps sugeridos**  
   - Criar um app dedicado (`django_licitacao360.apps.gestao_contratos`) para o domínio “Contratos / UASG / Atas”.  
   - Separar subdomínios em models específicos (`Contrato`, `StatusContrato`, `RegistroStatus`, `HistoricoContrato`, `Empenho`, `ItemContrato`, `ArquivoContrato`, `FiscalizacaoContrato`, `AtaPrincipal`, `StatusAta`, etc.).

2. **Tipos de campo**  
   - `CharField` para campos textuais curtos (definir `max_length` baseado no tamanho real).  
   - `TextField` para descrições longas (`objeto`, `observacoes`).  
   - `DecimalField` (adequado `max_digits=18`, `decimal_places=2`) para valores monetários (`valor_global`, `empenhado`, etc.).  
   - `DateField`/`DateTimeField` para datas hoje armazenadas como texto.  
   - `JSONField` para `raw_json`, `radio_options_json` e demais snapshots.

3. **Chaves e relacionamentos**  
   - Manter `Contrato.id` como `CharField(primary_key=True)` para preservar compatibilidade com dados existentes.  
   - `Uasg` deve ser `models.CharField(max_length=6, primary_key=True)` e referenciado por FK com `on_delete=models.PROTECT`.  
   - Tabelas historizadas (`Historico`, `Empenho`, `Item`, `Arquivo`) e registros (`RegistroStatus`, `RegistroMensagem`) precisam de `ForeignKey(Contrato, related_name=...)` com `db_index=True`.

4. **Constraints e índices**  
   - Replicar unicidades atuais (`RegistroStatus.texto`, `LinksContrato.contrato`, `Fiscalizacao.contrato`).  
   - Adicionar `indexes = [models.Index(fields=["contrato", "created_at"])]` quando necessário para consultas recentes.  
   - Usar `UniqueConstraint` combinado para garantir que um `RegistroStatus` não seja duplicado por `contrato + texto`.

5. **Campos auditáveis**  
   - Incluir `created_at`, `updated_at` (`auto_now_add`, `auto_now`) nas tabelas principais para rastreabilidade que hoje não existe.

6. **Integração com dados manuais**  
   - Prever FK para usuário (`ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)`) nos registros manuais.  
   - Guardar `sigla_om_resp` / `orgao_responsavel` em colunas dedicadas no contrato ou tabela auxiliar `ResponsavelContrato`.

7. **Ingestão contínua a partir da API ComprasNet**  
   - Reimplementar a lógica do `OfflineDBController`: consulta aos endpoints públicos, filtros por vigência, inserção/atualização de contratos e dados auxiliares.  
   - Persistir `raw_json` e manter relacionamentos completos (histórico, empenhos, itens, arquivos).  
   - Prever reprocessamento por UASG e rotinas de retry/cancelamento semelhantes ao aplicativo PyQt.

8. **Docker Compose e Postgres**  
   - Configurar serviço `postgres` com volume nomeado e definir `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.  
   - Ajustar o serviço `backend` para aplicar migrações automaticamente (`python manage.py migrate && gunicorn ...`).  
   - Utilizar variáveis de ambiente (`DATABASE_URL=postgresql://...`) e `django-environ` para leitura segura.

9. **URLs e apps**  
   - Registrar o novo app no `INSTALLED_APPS` e criar rotas REST em `django_licitacao360/urls.py` (ex.: `path('api/contratos/', include('django_licitacao360.apps.gestao_contratos.urls'))`).  
   - Expor endpoints específicos para cada agregado (`contratos`, `status`, `historico`, `empenhos`, `itens`, `arquivos`, `atas`), além de webhooks para sincronização offline.

10. **Processamento assíncrono e cache offline**  
   - Transformar `OfflineDBController.process_and_save_all_data` em uma `management command` ou `Celery task` que roda em segundo plano para alimentar PostgreSQL.  
   - Prever log de importação e flags `last_synced_at` por UASG para saber se o cache está atualizado.

Seguir estas orientações permitirá criar os models Django com fidelidade à lógica atual e, ao mesmo tempo, aproveitar recursos do PostgreSQL (tipagem forte, constraints e consultas otimizadas) dentro do ecossistema Docker Compose.
