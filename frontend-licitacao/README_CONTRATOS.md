# Módulo de Contratos - Frontend Angular

## 📦 Estrutura Implementada

### ✅ Componentes Core
- **ShellLayoutComponent** - Layout principal com navegação lateral
- **SideNavComponent** - Menu lateral fixo (70px)
- **HomeComponent** - Página inicial com botões de ação

### ✅ Componentes Reutilizáveis
- **StatusBadgeComponent** - Badge colorido por status
- **PreviewTableComponent** - Tabela compacta de preview
- **KpiCardComponent** - Card de KPI para dashboard

### ✅ Páginas do Módulo Contratos
- **UasgSearchComponent** - Buscar e sincronizar UASG
- **ContractsTableComponent** - Visualizar tabela de contratos
- **DashboardComponent** - Dashboard com KPIs
- **ContractDetailsComponent** - Detalhes do contrato (estrutura básica)
- **MessageBuilderComponent** - Gerador de mensagens (placeholder)
- **SettingsComponent** - Configurações (placeholder)

### ✅ Services
Todos os services estão implementados e prontos para consumo da API Django:
- `UasgService`
- `ContractsService`
- `StatusService`
- `LinksService`
- `FiscalizacaoService`
- `EmpenhosService`
- `ItensService`
- `ArquivosService`
- `DashboardService`
- `SettingsService`

### ✅ Interfaces TypeScript
Todas as interfaces estão alinhadas com os serializers Django:
- `Uasg`
- `Contrato`, `ContratoDetail`, `ContratoCreate`
- `StatusContrato`, `RegistroStatus`, `RegistroMensagem`
- `LinksContrato`
- `FiscalizacaoContrato`
- `HistoricoContrato`, `Empenho`, `ItemContrato`, `ArquivoContrato`
- `DashboardSummary`

## 🎨 Tema Dracula - Dark Mode Compact

### Características
- ✅ Fundo escuro (#282a36)
- ✅ Espaçamentos compactos (2px, 4px, 6px, 8px)
- ✅ Tipografia limpa e legível
- ✅ Cores vibrantes (azul, verde, amarelo, vermelho)
- ✅ Overrides do Angular Material

### Variáveis SCSS
- `styles/_variables.scss` - Todas as variáveis do tema
- `styles/_mixins.scss` - Mixins reutilizáveis
- `styles/_base.scss` - Estilos base globais
- `styles/_material-overrides.scss` - Overrides do Material

## 🚀 Como Usar

### 1. Instalar Dependências
```bash
cd frontend-licitacao
npm install
```

### 2. Configurar Environment
Edite `src/app/environments/environment.ts`:
```typescript
apiUrl: 'http://localhost/api/contratos'  // Via nginx
```

### 3. Executar em Desenvolvimento
```bash
ng serve
```

### 4. Acessar
- Login: `http://localhost:4200/login`
- Home: `http://localhost:4200/`
- Contratos: `http://localhost:4200/contratos`
- Dashboard: `http://localhost:4200/dashboard`

## 📋 Rotas Disponíveis

| Rota | Componente | Descrição |
|------|-----------|-----------|
| `/` | HomeComponent | Página inicial |
| `/contratos` | UasgSearchComponent | Buscar UASG |
| `/contratos/lista` | ContractsTableComponent | Visualizar tabelas |
| `/contratos/:id` | ContractDetailsComponent | Detalhes do contrato |
| `/contratos/mensagens` | MessageBuilderComponent | Gerador de mensagens |
| `/contratos/configuracoes` | SettingsComponent | Configurações |
| `/dashboard` | DashboardComponent | Dashboard de KPIs |

## 🔧 Próximos Passos

### Componentes a Implementar
1. **Tabs de Detalhes do Contrato**
   - ContractGeneralTabComponent
   - ContractLinksTabComponent
   - ContractFiscalTabComponent
   - ContractStatusTabComponent
   - ContractEmpenhosTabComponent
   - ContractItensTabComponent
   - ContractExtrasTabComponent

2. **Dialogs**
   - StatusOptionsDialogComponent
   - TableOptionsDialogComponent
   - ManualContractDialogComponent
   - RecordPopupComponent

3. **Componentes Reutilizáveis**
   - JsonViewerComponent
   - LinkFieldComponent
   - SearchBarComponent

### Endpoints Backend Necessários
Alguns endpoints ainda precisam ser criados no backend (ver seção 8 do guia completo):
- `/api/contratos/sync/`
- `/api/contratos/status/export/`
- `/api/contratos/empenhos/report/`
- `/api/contratos/messages/templates/`
- `/api/contratos/settings/`

## 📝 Notas Importantes

### Compatibilidade
- IDs são strings (compatível com backend Django)
- Datas em formato ISO (YYYY-MM-DD)
- Valores monetários como number (não string)
- JSON Fields são objetos JavaScript

### Estilo
- Tema Dracula com espaçamentos compactos
- Componentes densos e funcionais
- Foco em produtividade e densidade de informação

## 🐛 Troubleshooting

### Erro: Cannot find module '@angular/material'
```bash
ng add @angular/material
```

### Erro: Module not found
Verifique se todos os imports estão corretos e os arquivos foram criados.

### Erro: CORS
Certifique-se de que o backend Django está configurado para aceitar requisições do frontend.

