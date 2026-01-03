# Guia de implementação do frontend Angular (Licitação 360)

> **⚠️ ATENÇÃO:** Este documento foi substituído por versões completas e detalhadas. Consulte:
> - **[ANGULAR_FRONTEND_COMPLETE_GUIDE.md](./docs/ANGULAR_FRONTEND_COMPLETE_GUIDE.md)** - Guia completo com estrutura, interfaces, services e rotas
> - **[ANGULAR_COMPONENTS_DETAILED.md](./docs/ANGULAR_COMPONENTS_DETAILED.md)** - Detalhes de implementação de componentes

Este documento descreve como migrar a interface PyQt6/SQLite (`Contratos/view` e `main.py`) para Angular + Django REST + Postgres (via Docker). Ele detalha os componentes esperados em `frontend-licitacao/src/app`, os contratos de dados esperados pelo backend (`backend/django_licitacao360`), e como dividir rotas, módulos, guards e serviços.

## 1. Contexto e referências

- **Shell principal**: Navegação lateral e módulos de "Contratos" e "Atas" exibidos pela `MainShellView` (`view/main_shell_view.py`), com home cards para informações, backup e ajuda.
- **Módulo de contratos**: `Contratos/view/main_window.py` define três abas (Buscar UASG, Visualizar Tabelas, Dashboard) com botões de ação, tabela principal e preview de contratos.
- **Detalhes de contrato**: `Contratos/view/details_dialog.py` e sub-abas em `view/abas_detalhes/` mostram todas as informações (geral, links, fiscalização, status, empenhos, itens, extras, fluxos manuais) e interagem com modelos/SQLite.
- **Outros fluxos**: mensagens (`mensagem_view.py`), configurações (`settings_dialog.py`), pop-ups de status/tabelas (`view/menus`), preview de registros (`record_popup.py`).
- **Back-end exposto via API**: `backend/django_licitacao360/apps/gestao_contratos/README.md` fornece os endpoints REST que precisam ser consumidos pelos serviços Angular.

## 2. Organização Angular sugerida

```
src/app/
├── app.routes.ts                 # rotas raiz
├── environments/                 # environment.ts|prod.ts
├── guards/                       # auth.guard.ts etc.
├── interfaces/                   # modelos TS
├── services/                     # chamadas HTTP + sinalização
├── modules/
│   ├── core/                     # ShellLayout, Auth, interceptors
│   ├── shared/                   # componentes reutilizáveis (cards KPI, tabelas, dialog base)
│   └── features/
│       ├── contratos/            # telas derivadas do PyQt
│       └── atas/                 # placeholder para o módulo Atas
└── components/                   # widgets atômicos (menu lateral, barra de busca, card, etc.)
```

Use `modules/features/contratos` como container para páginas + componentes de negócio. Componentes especializados devem residir sob `components/` quando reutilizáveis (e.g., `status-badge`, `preview-table`, `json-viewer`, `link-field`).

## 3. Environments e guardas

- Ajuste `src/app/environments/environment.ts` e `.prod.ts` para refletir o host Docker (e.g., `apiUrl`, `mediasBasePath`, `reportsUrl`, `wsUrl`). Acrescente flags como `useMockData`, `defaultUasg`, `features` (para habilitar módulos progressivamente).
- Reaproveite `authGuard` (`guards/auth.guard.ts`) para proteger todas as rotas após login. Rotas públicas: `/login`, `/ajuda`. As demais devem carregar `canActivate: [authGuard]`.
- Centralize o armazenamento do token e refresh em `services/auth.service.ts`. Injetar `AuthService` nos interceptors para anexar tokens.

## 4. Rotas e módulos

### Rotas raiz (`app.routes.ts`)

| Rota | Componente/Página | Observações |
| ---- | ----------------- | ----------- |
| `/login` | `pages/login` | pública |
| `/` | `modules/core/shell-layout` | contém nav lateral e router-outlet |
| `/dashboard` | `features/contratos/pages/dashboard` | corresponde à aba Dashboard |
| `/contratos` | `features/contratos/pages/uasg-search` | aba "Buscar UASG" |
| `/contratos/lista` | `features/contratos/pages/contracts-table` | aba "Visualizar Tabelas" |
| `/contratos/:id` | `features/contratos/pages/contract-details` | dialog convertido em página com tabs |
| `/contratos/mensagens` | `features/contratos/pages/message-builder` | espelha `MensagemDialog` |
| `/contratos/configuracoes` | `features/contratos/pages/settings` | espelha `SettingsDialog` |
| `/atas` | módulo Atas (placeholder) | |
| `/backup` | página que chama o módulo de backup | |

Rotas filhas devem receber GUARD e `data: { breadcrumb }` para compor navegação. As abas internas (detalhes) podem usar rotas filhas (`/contratos/:id/(tab:geral|links|fiscalizacao|status|empenhos|itens|extras)`).

## 5. Componentes principais por funcionalidade

### 5.1 Shell / Home

- **`ShellLayoutComponent`** (`modules/core`): renderiza nav vertical com os ícones de Home, Contratos e Atas conforme `MainShellView` (linhas 28-79). Deve injetar um `SideNavService` para controlar seleção, e conter botões para "Informações", "Backup" e "Ajuda" ligados a dialogs Angular.

### 5.2 Aba "Buscar UASG" (`Contratos/view/main_window.py` linhas 34-109)

Criar `UasgSearchComponent` com duas colunas:
1. **Painel de ações**: 
   - Campo `input` para número da UASG + botões "Criar/Atualizar tabela", "Deletar", "Status", "Tabelas", "Contrato Manual".
   - Botões devem abrir dialogs Angular equivalentes a `StatusOptionsDialog` e `TableOptionsDialog` (menus em `Contratos/view/menus/*`).
   - Badge de status (Online/Offline) sincronizado com `SettingsService`.
2. **Pré-visualização**:
   - Reutilizar `PreviewTableComponent` (ver §5.4) mostrando contratos mais relevantes (colunas UASG, Dias, Contrato/Ata, Processo, Fornecedor, Status). Implementar indicadores de cor/ícone replicando `preview_table.py` (linhas 9-75 e 117-171).

### 5.3 Aba "Visualizar Tabelas" (linhas 110-190)

`ContractsTableComponent` deve oferecer:
- Toolbar com menu de UASG, botões "Mensagens" (abrir builder), "Limpar", label "UASG: ...".
- `MatTable`/`cdk-table` com filtro global (barra de busca com ícone), ordenação multi-coluna e context menu para ações específicas (abrir detalhes, gerar relatórios, deletar, etc.). O layout e filtros seguem `controller/controller_table.py`.
- Sincronização com `ContractsStore` (RxJS `signal`/`BehaviorSubject`) contendo `currentUasg`, `rows`, `selection`.

### 5.4 Componentes reutilizáveis

- `preview-table` (cards/linha) replicando `PreviewTableWidget`.
- `status-badge` (cores e ícones de status).
- `search-bar` com debounce + ícone.
- `json-viewer` com sintaxe destacada (como `extras_link.py`).
- `link-field` (label, input, botões copy/open) para reutilizar nos tabs de links.
- `kpi-card` e `pie-chart` (Dashboard).

### 5.5 Dashboard (linhas 192-205 + `dashboard_tab.py`)

`DashboardPageComponent`:
- Header com `<h1>` + botão "Atualizar Dados".
- Grid de quatro cards (`total_contratos`, `valor_total`, `ativos`, `expirando`), cada card reutiliza `kpi-card`.
- Painel com `StatusChartComponent` (pie/donut) alimentado por `DashboardService`.
- Placeholder para gráfico 2 (valores por ano) mantendo container do PyQt.

### 5.6 Detalhes do contrato (`details_dialog.py`)

Criar página `ContractDetailsPage` com tabs horizontais. Cada tab vira componente dedicado em `components/contract-details/`:

1. **`contract-general-tab`** (linhas 30-245):
   - Visualização em duas colunas, campos somente leitura com botões de copiar. Converter `radio buttons` ("Pode Renovar?", "Custeio?" etc.) para `FormGroup` + binding a `StatusContrato`.
   - Botão "Editar Objeto" abre `object-editor` modal (textarea em `EditObjectDialog`).
2. **`contract-links-tab`** (`pdfs_view.py`): exibir links automáticos, campos editáveis, botão para buscar arquivos (chamada `GET /arquivos/`).
3. **`contract-fiscal-tab`** (`fiscal_tab.py`): formulário com sete campos, persistindo via `PUT /fiscalizacao/:id` e mantendo botões de copiar.
4. **`contract-status-tab`** (`status_tab.py`): dropdown com os 11 status, lista de registros, botões "Adicionar", "Excluir", "Copiar". Requer componentes para modais de registro e integração com `StatusService`.
5. **`contract-empenhos-tab`** (`empenhos_tab.py`): botão para buscar dados, cards por empenho, filtro por ano, botões de relatório XLSX e email (veja §7).
6. **`contract-itens-tab`** (`itens_tab.py`): cards com valor total, grupo, catmat/ser, botão para gerar relatório e enviar e-mail.
7. **`contract-extras-tab`** (`extras_link.py`): lista lateral de fontes (`historico`, `empenhos`, `itens`, `arquivos`), viewer JSON com destaque, cache local para cada chave.
8. **`contract-manual-general-tab`** e `contract-manual-links-tab` para contratos com `manual: true` (veja `detalhes_manual/`). Inclua máscaras (CNPJ, moeda, datas) e validações.

Todos os tabs devem compartilhar `ContractDetailsStore` (signals) com `data$, status$, registros$, fiscalizacao$`.

### 5.7 Pop-ups e dialogs auxiliares

- **`record-preview-dialog`**: substitui `RecordPopup` (linhas 7-61) e permite abrir `ContractDetailsPage`.
- **`status-options-dialog`** e **`table-options-dialog`** replicam as opções de backup/import (ver `view/menus/*.py`).
- **`manual-contract-dialog`**: formulário para criar contratos manuais.
- **`message-builder-page`**: duas abas (Gerador/Comentários) com lista de variáveis, edição de template e preview (ver `mensagem_view.py` linhas 19-118). Use `textarea` + `cdkDrag` se necessário.
- **`settings-page`**: reproduz `SettingsDialog` (linhas 19-122) com switches para modo online/offline, seleção de pasta (via API), input de UASG para baixar/excluir base offline.

## 6. Serviços e compatibilidade com a API Django

Crie os serviços abaixo em `src/app/services` (ou subpastas). Cada serviço deve consumir os endpoints da `gestao_contratos` (README linhas 51-99) e expor Observables + métodos de comando.

| Serviço | Responsabilidades | Endpoints principais |
| ------- | ----------------- | -------------------- |
| `UasgService` | buscar lista de UASGs, sincronizar dados locais | `GET /uasgs/`, `GET /uasgs/{code}` |
| `ContractsService` | CRUD de contratos, busca por UASG, preview/detalhes | `GET /contratos/`, `/contratos/{id}`, `/contratos/{id}/detalhes/`, filtros `?uasg=` |
| `DashboardService` | KPIs e status chart | `GET /contratos/contratos/ativos`, `/proximos_vencer`, agregações customizadas |
| `StatusService` | status atuais, registros, import/export | `GET/POST /status/`, `GET/POST /registros-status/`, endpoints customizados para backup |
| `LinksService` | links manuais e arquivos | `GET /links/`, `GET /arquivos/`, `POST/PUT` correspondentes |
| `FiscalizacaoService` | campos editáveis da aba Fiscalização | `GET/PUT /fiscalizacao/` |
| `ItensService` | itens + geração de relatórios | `GET /itens/?contrato={id}`, endpoint de relatório CSV/XLSX |
| `EmpenhosService` | empenhos, filtro por ano | `GET /empenhos/?contrato={id}`, endpoint de relatório |
| `ExtrasService` | histórico/JSONs com caching | `GET /historico/`, `/itens/`, `/empenhos/`, `/arquivos/` dependendo da chave |
| `MessageTemplatesService` | templates, variáveis e registros de mensagens | `GET/POST /registros-mensagem/`, endpoints auxiliares |
| `SettingsService` | modo online/offline, diretórios, sincronização | endpoints dedicados no backend (criar se ainda não existirem) |
| `ReportsService` | geração/download e envio de XLSX | endpoints específicos, reutilizado pelos tabs Itens/Empenhos |

Todos os serviços devem usar `HttpClient` com interceptors (tratamento de erros, loader). Para chamadas demoradas (buscar itens/empenhos), exiba spinner e desabilite botões como no PyQt.

## 7. Interfaces TypeScript

Coloque todas em `src/app/interfaces/`. Sugestão:

- `uasg.ts`: `{ codigo: string; nome: string; situacao: string; }`
- `contrato.ts`: `{ id: number; numero: string; processo: string; licitacaoNumero: string; valorGlobal: number; vigenciaInicio: string; vigenciaFim: string; status: string; fornecedor: Fornecedor; contratante: Contratante; manual: boolean; links?: ContratoLinks; }`
- `fornecedor.ts`: `{ nome: string; cnpjCpfIdgener: string; }`
- `contratante.ts`: `{ orgao: { unidadeGestora: { nomeResumido: string; codigo: string; }}}`
- `status-contrato.ts`: `{ contratoId: number; status: string; podeRenovar: boolean; custeio: boolean; naturezaContinuada: boolean; tipoMaterialServico: 'Material' | 'Serviço'; portaria: string; termoAditivo: string; registros: RegistroStatus[]; }`
- `registro-status.ts`: `{ id: number; contratoId: number; descricao: string; criadoEm: string; }`
- `fiscalizacao.ts`: campos de `fiscal_tab.py` (gestor, substituto, técnicos, observações).
- `empenho.ts`, `item.ts`, `arquivo.ts`, `link.ts`.
- `dashboard-summary.ts`: `{ totalContratos: number; valorTotal: number; ativos: number; expirando90dias: number; statusDistribuicao: Record<string, number>; }`
- `mensagem-template.ts`, `mensagem-comentario.ts`.

Os nomes de campo devem espelhar os serializers existentes para evitar mappers desnecessários. Documente nos comentários dos arquivos as propriedades opcionais e formato (ISO date, BRL string).

## 8. Requisitos específicos por aba

- **Preview/Table**: Calcular `dias_restantes` como no PyQt (`vigencia_fim - hoje`). Aplicar cores/ícones (verde >180 dias, amarelo até 179, laranja até 89, vermelho negativo). Permitir clique para abrir registros anteriores (record popup).
- **Status Tab**: Dropdown com valores fixos (`SEÇÃO CONTRATOS`, `EMPRESA`, etc.). Manter botões `Adicionar`, `Excluir`, `Copiar` que disparam modais de texto; persistir via `StatusService`. O list view precisa suportar seleção múltipla (Ctrl/Cmd) para exclusão.
- **Empenhos/Itens**: Botões para "Gerar Relatório XLSX" e "Disparar XLSX por E-mail" devem acionar `ReportsService` (download) e `EmailService` (enviar). Exibir loading e mensagens de erro se a API retornar vazio.
- **Links**: Preencher automaticamente links públicos (Comprasnet, PNCP) usando `objeto.process`. Campos editáveis devem ter ações "Copiar" e "Abrir" (usar `cdkCopyToClipboard` e `window.open`).
- **Extras**: Implementar `JsonHighlighter` com `highlight.js` ou `Prism.js`. Cache por chave para evitar múltiplas chamadas.
- **Mensagens**: Carregar lista de variáveis fornecida pela API, permitir inserir tokens no texto, gerar preview substituindo `{{variavel}}`.
- **Settings**: Alternar Modo Online/Offline com `mat-slide-toggle`. Campos para caminho do banco podem usar `file input` via API (o backend precisa retornar e atualizar `config.json`). Botões "Fazer DB" e "Excluir UASG" chamam endpoints que criam ou removem caches offline.
- **Manual Contracts**: Formulários totalmente editáveis com validações (CNPJ regex, moeda em BRL, datas). Persistir em `/contratos/` com `manual=true` e `dados_manuais`.

## 9. Compatibilização com o backend

- Utilize os filtros documentados (README linhas 84-98) para replicar a busca avançada presente na barra de pesquisa do PyQt.
- Para cada ação visual, verifique se o endpoint já existe. Exemplos:
  - **Import/Export status**: criar endpoints `POST /status/import` e `GET /status/export` se necessários.
  - **Relatórios XLSX**: expor `GET /contratos/{id}/itens/xlsx` e `GET /contratos/{id}/empenhos/xlsx`.
  - **Mensagens**: armazenar modelos em `RegistroMensagem`.
  - **Backup**: se a lógica continuar local, exponha endpoints `POST /backup/run`, `GET /backup/status`.
- Adote DTOs consistentes com o backend para permitir reuso do modelo `Contrato` tanto no preview (campos resumidos) quanto no detalhe (expandido). Caso necessário, crie endpoints "resumidos" (`?fields=`) para otimizar listas.
- Utilize paginação e lazy loading na tabela completa para lidar com grandes conjuntos.

## 10. Próximos passos sugeridos

1. **Modelar interfaces TS** com base nos serializers existentes e validar com o time backend.
2. **Criar módulos Angular** (`CoreModule`, `SharedModule`, `ContratosModule`) e configurar rotas protegidas pelo `authGuard`.
3. **Implementar ShellLayout + nav** mantendo os botões do PyQt.
4. **Construir UasgSearch + Preview** usando `ContractsService` para alimentar dados iniciais.
5. **Migrar ContractsTable** com filtros, menu de UASG e actions contextuais.
6. **Portar Dashboard** (cards + pie chart) usando dados reais.
7. **Transformar DetailsDialog** em página com tabs (começando pelo tab Geral e Links).
8. **Adicionar serviços para itens/empenhos/status** e conectar aos respectivos componentes.
9. **Migrar Mensagens e Configurações** como páginas dedicadas.
10. **Testar fluxo ponta a ponta** (buscar UASG → abrir contrato → atualizar status → gerar relatório) garantindo que as APIs entregam todos os valores necessários.

Seguindo este guia, todos os componentes Angular ficarão compatíveis com o backend Django, e o comportamento visual/funcional refletirá fielmente a experiência do aplicativo desktop existente.
