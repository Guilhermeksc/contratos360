# Guia Completo de Implementação - Frontend Angular

Este documento fornece orientações detalhadas para migrar a interface PyQt6 para Angular, garantindo compatibilidade total com o backend Django já implementado.

## 📋 Índice

1. [Estrutura de Diretórios](#1-estrutura-de-diretórios)
2. [Interfaces TypeScript](#2-interfaces-typescript)
3. [Services](#3-services)
4. [Componentes](#4-componentes)
5. [Rotas e Guards](#5-rotas-e-guards)
6. [Environments](#6-environments)
7. [Mapeamento PyQt → Angular](#7-mapeamento-pyqt--angular)

---

## 1. Estrutura de Diretórios

```
frontend-licitacao/src/app/
├── components/                    # Componentes reutilizáveis
│   ├── status-badge/
│   ├── preview-table/
│   ├── json-viewer/
│   ├── link-field/
│   ├── kpi-card/
│   ├── search-bar/
│   └── loading-spinner/
├── environments/
│   ├── environment.ts
│   └── environment.prod.ts
├── guards/
│   ├── auth.guard.ts
│   └── login.guard.ts
├── interceptors/
│   ├── auth.interceptor.ts
│   └── error.interceptor.ts
├── interfaces/
│   ├── uasg.interface.ts
│   ├── contrato.interface.ts
│   ├── status.interface.ts
│   ├── fiscalizacao.interface.ts
│   ├── empenho.interface.ts
│   ├── item.interface.ts
│   ├── arquivo.interface.ts
│   └── dashboard.interface.ts
├── modules/
│   ├── core/
│   │   ├── shell-layout/
│   │   └── side-nav/
│   ├── shared/
│   │   └── shared.module.ts
│   └── features/
│       ├── contratos/
│       │   ├── pages/
│       │   │   ├── uasg-search/
│       │   │   ├── contracts-table/
│       │   │   ├── contract-details/
│       │   │   ├── dashboard/
│       │   │   ├── message-builder/
│       │   │   └── settings/
│       │   └── components/
│       │       ├── contract-general-tab/
│       │       ├── contract-links-tab/
│       │       ├── contract-fiscal-tab/
│       │       ├── contract-status-tab/
│       │       ├── contract-empenhos-tab/
│       │       ├── contract-itens-tab/
│       │       ├── contract-extras-tab/
│       │       └── contract-manual-tabs/
│       └── atas/                  # Placeholder para futuro
├── routes/
│   └── app.routes.ts
└── services/
    ├── uasg.service.ts
    ├── contracts.service.ts
    ├── status.service.ts
    ├── links.service.ts
    ├── fiscalizacao.service.ts
    ├── empenhos.service.ts
    ├── itens.service.ts
    ├── arquivos.service.ts
    ├── dashboard.service.ts
    ├── messages.service.ts
    ├── settings.service.ts
    └── reports.service.ts
```

---

## 2. Interfaces TypeScript

### 2.1. UASG (`interfaces/uasg.interface.ts`)

```typescript
export interface Uasg {
  uasg_code: string;
  nome_resumido: string | null;
}
```

### 2.2. Contrato (`interfaces/contrato.interface.ts`)

```typescript
import { StatusContrato } from './status.interface';
import { LinksContrato } from './links.interface';
import { FiscalizacaoContrato } from './fiscalizacao.interface';

export interface Contrato {
  id: string;  // String (vem da API)
  numero: string | null;
  uasg: string;  // FK para Uasg.uasg_code
  uasg_nome?: string;  // Campo calculado do serializer
  licitacao_numero: string | null;
  processo: string | null;
  fornecedor_nome: string | null;
  fornecedor_cnpj: string | null;
  objeto: string | null;
  valor_global: number | null;  // DecimalField convertido
  vigencia_inicio: string | null;  // DateField (ISO: YYYY-MM-DD)
  vigencia_fim: string | null;  // DateField (ISO: YYYY-MM-DD)
  tipo: string | null;
  modalidade: string | null;
  contratante_orgao_unidade_gestora_codigo: string | null;
  contratante_orgao_unidade_gestora_nome_resumido: string | null;
  manual: boolean;
  raw_json: any | null;  // JSONField
  status_atual?: string;  // Campo calculado do serializer
  created_at?: string;  // DateTimeField (ISO)
  updated_at?: string;  // DateTimeField (ISO)
}

export interface ContratoDetail extends Contrato {
  status: StatusContrato | null;
  links: LinksContrato | null;
  fiscalizacao: FiscalizacaoContrato | null;
  registros_status: string[];  // Array de textos
  registros_mensagem: string[];  // Array de textos
  historicos_count: number;
  empenhos_count: number;
  itens_count: number;
  arquivos_count: number;
}

export interface ContratoCreate {
  id: string;
  uasg: string;
  numero: string;
  licitacao_numero?: string | null;
  processo?: string | null;
  fornecedor_nome?: string | null;
  fornecedor_cnpj?: string | null;
  objeto?: string | null;
  valor_global?: number | null;
  vigencia_inicio?: string | null;
  vigencia_fim?: string | null;
  tipo?: string | null;
  modalidade?: string | null;
  contratante_orgao_unidade_gestora_codigo?: string | null;
  contratante_orgao_unidade_gestora_nome_resumido?: string | null;
  manual: boolean;
  raw_json?: any | null;
}
```

### 2.3. Status (`interfaces/status.interface.ts`)

```typescript
export interface StatusContrato {
  contrato: string;  // FK para Contrato.id
  uasg_code: string | null;
  status: string | null;  // Ex: "ALERTA PRAZO", "PORTARIA", etc.
  objeto_editado: string | null;
  portaria_edit: string | null;
  termo_aditivo_edit: string | null;
  radio_options_json: RadioOptions | null;  // JSONField parseado
  data_registro: string | null;  // Formato: "DD/MM/AAAA HH:MM:SS"
}

export interface RadioOptions {
  "Pode Renovar?": string;
  "Custeio?": string;
  "Natureza Continuada?": string;
  "Material/Serviço:": string;
}

export interface RegistroStatus {
  id: number;
  contrato: string;
  uasg_code: string | null;
  texto: string;  // Formato: "DD/MM/AAAA - mensagem - STATUS"
}

export interface RegistroMensagem {
  id: number;
  contrato: string;
  texto: string;
}
```

### 2.4. Links (`interfaces/links.interface.ts`)

```typescript
export interface LinksContrato {
  id: number;
  contrato: string;
  link_contrato: string | null;
  link_ta: string | null;  // Termo Aditivo
  link_portaria: string | null;
  link_pncp_espc: string | null;
  link_portal_marinha: string | null;
}
```

### 2.5. Fiscalização (`interfaces/fiscalizacao.interface.ts`)

```typescript
export interface FiscalizacaoContrato {
  id: number;
  contrato: string;
  gestor: string | null;
  gestor_substituto: string | null;
  fiscal_tecnico: string | null;
  fiscal_tec_substituto: string | null;
  fiscal_administrativo: string | null;
  fiscal_admin_substituto: string | null;
  observacoes: string | null;
  data_criacao: string | null;  // DateTimeField (ISO)
  data_atualizacao: string | null;  // DateTimeField (ISO)
}
```

### 2.6. Dados Offline (`interfaces/offline.interface.ts`)

```typescript
export interface HistoricoContrato {
  id: number;
  contrato: string;
  receita_despesa: string | null;
  numero: string | null;
  observacao: string | null;
  ug: string | null;
  gestao: string | null;
  fornecedor_cnpj: string | null;
  fornecedor_nome: string | null;
  tipo: string | null;
  categoria: string | null;
  processo: string | null;
  objeto: string | null;
  modalidade: string | null;
  licitacao_numero: string | null;
  data_assinatura: string | null;  // DateField (ISO)
  data_publicacao: string | null;  // DateField (ISO)
  vigencia_inicio: string | null;  // DateField (ISO)
  vigencia_fim: string | null;  // DateField (ISO)
  valor_global: number | null;  // DecimalField
  raw_json: any | null;
}

export interface Empenho {
  id: number;
  contrato: string;
  unidade_gestora: string | null;
  gestao: string | null;
  numero: string | null;
  data_emissao: string | null;  // DateField (ISO)
  credor_cnpj: string | null;
  credor_nome: string | null;
  empenhado: number | null;  // DecimalField
  liquidado: number | null;  // DecimalField
  pago: number | null;  // DecimalField
  informacao_complementar: string | null;
  raw_json: any | null;
}

export interface ItemContrato {
  id: number;
  contrato: string;
  tipo_id: string | null;
  tipo_material: string | null;
  grupo_id: string | null;
  catmatseritem_id: string | null;
  descricao_complementar: string | null;
  quantidade: number | null;  // DecimalField (4 casas)
  valorunitario: number | null;  // DecimalField
  valortotal: number | null;  // DecimalField
  numero_item_compra: string | null;
  raw_json: any | null;
}

export interface ArquivoContrato {
  id: number;
  contrato: string;
  tipo: string | null;
  descricao: string | null;
  path_arquivo: string | null;
  origem: string | null;
  link_sei: string | null;
  raw_json: any | null;
}
```

### 2.7. Dashboard (`interfaces/dashboard.interface.ts`)

```typescript
export interface DashboardSummary {
  total_contratos: number;
  valor_total: number;
  ativos: number;
  expirando: number;  // Próximos 90 dias
  status_distribuicao: Record<string, number>;  // { "ALERTA PRAZO": 5, ... }
}
```

### 2.8. Dados Manuais (`interfaces/dados-manuais.interface.ts`)

```typescript
export interface DadosManuaisContrato {
  contrato: string;
  sigla_om_resp: string | null;
  orgao_responsavel: string | null;
  portaria: string | null;
  created_by: number | null;  // FK para User
}
```

---

## 3. Services

### 3.1. UASG Service (`services/uasg.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Uasg } from '../interfaces/uasg.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class UasgService {
  private apiUrl = `${environment.apiUrl}/uasgs`;

  constructor(private http: HttpClient) {}

  list(): Observable<Uasg[]> {
    return this.http.get<Uasg[]>(this.apiUrl);
  }

  get(code: string): Observable<Uasg> {
    return this.http.get<Uasg>(`${this.apiUrl}/${code}/`);
  }
}
```

### 3.2. Contracts Service (`services/contracts.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Contrato, ContratoDetail, ContratoCreate } from '../interfaces/contrato.interface';
import { environment } from '../environments/environment';

export interface ContratoFilters {
  uasg?: string;
  status?: string;
  manual?: boolean;
  vigencia_fim__gte?: string;
  vigencia_fim__lte?: string;
  fornecedor_cnpj?: string;
  search?: string;
  ordering?: string;
  page?: number;
}

@Injectable({ providedIn: 'root' })
export class ContractsService {
  private apiUrl = `${environment.apiUrl}/contratos`;

  constructor(private http: HttpClient) {}

  list(filters?: ContratoFilters): Observable<{ count: number; results: Contrato[]; next: string | null; previous: string | null }> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        const value = filters[key as keyof ContratoFilters];
        if (value !== undefined && value !== null) {
          params = params.set(key, value.toString());
        }
      });
    }
    return this.http.get<{ count: number; results: Contrato[]; next: string | null; previous: string | null }>(this.apiUrl, { params });
  }

  get(id: string): Observable<Contrato> {
    return this.http.get<Contrato>(`${this.apiUrl}/${id}/`);
  }

  getDetails(id: string): Observable<ContratoDetail> {
    return this.http.get<ContratoDetail>(`${this.apiUrl}/${id}/detalhes/`);
  }

  create(data: ContratoCreate): Observable<Contrato> {
    return this.http.post<Contrato>(this.apiUrl, data);
  }

  update(id: string, data: Partial<Contrato>): Observable<Contrato> {
    return this.http.put<Contrato>(`${this.apiUrl}/${id}/`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  // Endpoints especiais
  getVencidos(): Observable<Contrato[]> {
    return this.http.get<Contrato[]>(`${this.apiUrl}/vencidos/`);
  }

  getProximosVencer(): Observable<Contrato[]> {
    return this.http.get<Contrato[]>(`${this.apiUrl}/proximos_vencer/`);
  }

  getAtivos(): Observable<Contrato[]> {
    return this.http.get<Contrato[]>(`${this.apiUrl}/ativos/`);
  }

  // Sincronização
  syncUasg(uasgCode: string): Observable<any> {
    // Endpoint a ser criado no backend: POST /api/contratos/sync/?uasg=787010
    return this.http.post(`${environment.apiUrl}/sync/`, null, {
      params: new HttpParams().set('uasg', uasgCode)
    });
  }
}
```

### 3.3. Status Service (`services/status.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { StatusContrato, RegistroStatus, RegistroMensagem, RadioOptions } from '../interfaces/status.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class StatusService {
  private apiUrl = `${environment.apiUrl}`;

  constructor(private http: HttpClient) {}

  // StatusContrato
  getStatus(contratoId: string): Observable<StatusContrato> {
    return this.http.get<StatusContrato>(`${this.apiUrl}/status/?contrato=${contratoId}`).pipe(
      // Retorna primeiro resultado ou cria vazio
    );
  }

  createOrUpdateStatus(data: Partial<StatusContrato>): Observable<StatusContrato> {
    return this.http.post<StatusContrato>(`${this.apiUrl}/status/`, data);
  }

  updateStatus(contratoId: string, data: Partial<StatusContrato>): Observable<StatusContrato> {
    return this.http.put<StatusContrato>(`${this.apiUrl}/status/${contratoId}/`, data);
  }

  // RegistroStatus
  listRegistrosStatus(contratoId: string): Observable<RegistroStatus[]> {
    return this.http.get<RegistroStatus[]>(`${this.apiUrl}/registros-status/?contrato=${contratoId}`);
  }

  createRegistroStatus(data: { contrato: string; uasg_code?: string; texto: string }): Observable<RegistroStatus> {
    return this.http.post<RegistroStatus>(`${this.apiUrl}/registros-status/`, data);
  }

  deleteRegistroStatus(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/registros-status/${id}/`);
  }

  // RegistroMensagem
  listRegistrosMensagem(contratoId: string): Observable<RegistroMensagem[]> {
    return this.http.get<RegistroMensagem[]>(`${this.apiUrl}/registros-mensagem/?contrato=${contratoId}`);
  }

  createRegistroMensagem(data: { contrato: string; texto: string }): Observable<RegistroMensagem> {
    return this.http.post<RegistroMensagem>(`${this.apiUrl}/registros-mensagem/`, data);
  }

  deleteRegistroMensagem(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/registros-mensagem/${id}/`);
  }

  // Import/Export (endpoints a serem criados no backend)
  exportStatus(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/status/export/`, { responseType: 'blob' });
  }

  importStatus(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/status/import/`, formData);
  }
}
```

### 3.4. Links Service (`services/links.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { LinksContrato } from '../interfaces/links.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class LinksService {
  private apiUrl = `${environment.apiUrl}/links`;

  constructor(private http: HttpClient) {}

  get(contratoId: string): Observable<LinksContrato> {
    return this.http.get<LinksContrato>(`${this.apiUrl}/?contrato=${contratoId}`).pipe(
      // Retorna primeiro resultado ou cria vazio
    );
  }

  createOrUpdate(data: Partial<LinksContrato>): Observable<LinksContrato> {
    return this.http.post<LinksContrato>(this.apiUrl, data);
  }

  update(id: number, data: Partial<LinksContrato>): Observable<LinksContrato> {
    return this.http.put<LinksContrato>(`${this.apiUrl}/${id}/`, data);
  }
}
```

### 3.5. Fiscalização Service (`services/fiscalizacao.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FiscalizacaoContrato } from '../interfaces/fiscalizacao.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class FiscalizacaoService {
  private apiUrl = `${environment.apiUrl}/fiscalizacao`;

  constructor(private http: HttpClient) {}

  get(contratoId: string): Observable<FiscalizacaoContrato> {
    return this.http.get<FiscalizacaoContrato>(`${this.apiUrl}/?contrato=${contratoId}`).pipe(
      // Retorna primeiro resultado ou cria vazio
    );
  }

  createOrUpdate(data: Partial<FiscalizacaoContrato>): Observable<FiscalizacaoContrato> {
    return this.http.post<FiscalizacaoContrato>(this.apiUrl, data);
  }

  update(id: number, data: Partial<FiscalizacaoContrato>): Observable<FiscalizacaoContrato> {
    return this.http.put<FiscalizacaoContrato>(`${this.apiUrl}/${id}/`, data);
  }
}
```

### 3.6. Empenhos Service (`services/empenhos.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Empenho } from '../interfaces/offline.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class EmpenhosService {
  private apiUrl = `${environment.apiUrl}/empenhos`;

  constructor(private http: HttpClient) {}

  list(contratoId: string, filters?: { ano?: number }): Observable<Empenho[]> {
    let params = new HttpParams().set('contrato', contratoId);
    if (filters?.ano) {
      params = params.set('data_emissao__year', filters.ano.toString());
    }
    return this.http.get<Empenho[]>(this.apiUrl, { params });
  }

  generateReport(contratoId: string): Observable<Blob> {
    // Endpoint a ser criado: GET /api/contratos/empenhos/report/?contrato={id}
    return this.http.get(`${this.apiUrl}/report/`, {
      params: new HttpParams().set('contrato', contratoId),
      responseType: 'blob'
    });
  }
}
```

### 3.7. Itens Service (`services/itens.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ItemContrato } from '../interfaces/offline.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class ItensService {
  private apiUrl = `${environment.apiUrl}/itens`;

  constructor(private http: HttpClient) {}

  list(contratoId: string): Observable<ItemContrato[]> {
    return this.http.get<ItemContrato[]>(this.apiUrl, {
      params: new HttpParams().set('contrato', contratoId)
    });
  }

  generateReport(contratoId: string): Observable<Blob> {
    // Endpoint a ser criado: GET /api/contratos/itens/report/?contrato={id}
    return this.http.get(`${this.apiUrl}/report/`, {
      params: new HttpParams().set('contrato', contratoId),
      responseType: 'blob'
    });
  }
}
```

### 3.8. Arquivos Service (`services/arquivos.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ArquivoContrato } from '../interfaces/offline.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class ArquivosService {
  private apiUrl = `${environment.apiUrl}/arquivos`;

  constructor(private http: HttpClient) {}

  list(contratoId: string): Observable<ArquivoContrato[]> {
    return this.http.get<ArquivoContrato[]>(this.apiUrl, {
      params: new HttpParams().set('contrato', contratoId)
    });
  }
}
```

### 3.9. Dashboard Service (`services/dashboard.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import { map } from 'rxjs/operators';
import { DashboardSummary } from '../interfaces/dashboard.interface';
import { ContractsService } from './contracts.service';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  constructor(
    private http: HttpClient,
    private contractsService: ContractsService
  ) {}

  getSummary(): Observable<DashboardSummary> {
    // Busca dados agregados
    return forkJoin({
      total: this.contractsService.list().pipe(map(r => r.count)),
      ativos: this.contractsService.getAtivos().pipe(map(r => r.length)),
      proximosVencer: this.contractsService.getProximosVencer().pipe(map(r => r.length)),
      vencidos: this.contractsService.getVencidos().pipe(map(r => r.length))
    }).pipe(
      map(data => {
        // Calcula valor total e distribuição de status
        // (pode ser otimizado com endpoint agregado no backend)
        return {
          total_contratos: data.total,
          valor_total: 0,  // Calcular somando valor_global
          ativos: data.ativos,
          expirando: data.proximosVencer,
          status_distribuicao: {}  // Agregar por status
        };
      })
    );
  }
}
```

### 3.10. Reports Service (`services/reports.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private apiUrl = `${environment.apiUrl}`;

  constructor(private http: HttpClient) {}

  generateEmpenhosReport(contratoId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/empenhos/report/`, {
      params: new HttpParams().set('contrato', contratoId),
      responseType: 'blob'
    });
  }

  generateItensReport(contratoId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/itens/report/`, {
      params: new HttpParams().set('contrato', contratoId),
      responseType: 'blob'
    });
  }

  generateTableExport(filters?: any): Observable<Blob> {
    // Endpoint a ser criado: GET /api/contratos/export/?uasg=787010&format=xlsx
    let params = new HttpParams().set('format', 'xlsx');
    if (filters) {
      Object.keys(filters).forEach(key => {
        params = params.set(key, filters[key]);
      });
    }
    return this.http.get(`${this.apiUrl}/export/`, {
      params,
      responseType: 'blob'
    });
  }

  sendReportByEmail(contratoId: string, reportType: 'empenhos' | 'itens', email: string): Observable<any> {
    // Endpoint a ser criado: POST /api/contratos/reports/send-email/
    return this.http.post(`${this.apiUrl}/reports/send-email/`, {
      contrato_id: contratoId,
      report_type: reportType,
      email
    });
  }
}
```

### 3.11. Messages Service (`services/messages.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { RegistroMensagem } from '../interfaces/status.interface';
import { environment } from '../environments/environment';

export interface MessageTemplate {
  id?: number;
  nome: string;
  conteudo: string;
  variaveis: string[];
}

@Injectable({ providedIn: 'root' })
export class MessagesService {
  private apiUrl = `${environment.apiUrl}/registros-mensagem`;

  constructor(private http: HttpClient) {}

  getTemplates(): Observable<MessageTemplate[]> {
    // Endpoint a ser criado: GET /api/contratos/messages/templates/
    return this.http.get<MessageTemplate[]>(`${environment.apiUrl}/messages/templates/`);
  }

  getVariables(): Observable<string[]> {
    // Lista de variáveis disponíveis (ex: {{numero}}, {{fornecedor_nome}}, etc.)
    return this.http.get<string[]>(`${environment.apiUrl}/messages/variables/`);
  }

  generatePreview(template: string, contratoId: string): Observable<string> {
    // Endpoint a ser criado: POST /api/contratos/messages/preview/
    return this.http.post<string>(`${environment.apiUrl}/messages/preview/`, {
      template,
      contrato_id: contratoId
    });
  }

  saveMessage(contratoId: string, texto: string): Observable<RegistroMensagem> {
    return this.http.post<RegistroMensagem>(this.apiUrl, {
      contrato: contratoId,
      texto
    });
  }
}
```

### 3.12. Settings Service (`services/settings.service.ts`)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { environment } from '../environments/environment';

export interface AppSettings {
  data_mode: 'Online' | 'Offline';
  db_path?: string;
}

@Injectable({ providedIn: 'root' })
export class SettingsService {
  private apiUrl = `${environment.apiUrl}/settings`;
  private modeSubject = new BehaviorSubject<'Online' | 'Offline'>('Online');
  public mode$ = this.modeSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadSettings();
  }

  getSettings(): Observable<AppSettings> {
    // Endpoint a ser criado: GET /api/contratos/settings/
    return this.http.get<AppSettings>(`${this.apiUrl}/`);
  }

  updateSettings(settings: Partial<AppSettings>): Observable<AppSettings> {
    // Endpoint a ser criado: PUT /api/contratos/settings/
    return this.http.put<AppSettings>(`${this.apiUrl}/`, settings).pipe(
      tap(s => {
        if (s.data_mode) {
          this.modeSubject.next(s.data_mode);
        }
      })
    );
  }

  syncContrato(contratoId: string): Observable<any> {
    // Endpoint a ser criado: POST /api/contratos/sync-detalhes/
    return this.http.post(`${environment.apiUrl}/sync-detalhes/`, {
      contrato_id: contratoId
    });
  }

  private loadSettings(): void {
    this.getSettings().subscribe(settings => {
      this.modeSubject.next(settings.data_mode || 'Online');
    });
  }
}
```

---

## 4. Componentes

### 4.1. Shell Layout (`modules/core/shell-layout/`)

**Responsabilidade:** Layout principal com navegação lateral (equivalente a `MainShellView`)

**Estrutura:**
```typescript
// shell-layout.component.ts
@Component({
  selector: 'app-shell-layout',
  template: `
    <div class="shell-container">
      <app-side-nav></app-side-nav>
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `
})
export class ShellLayoutComponent {}
```

### 4.2. Side Navigation (`modules/core/side-nav/`)

**Responsabilidade:** Menu lateral com ícones (Home, Contratos, Atas)

**Funcionalidades:**
- 3 itens principais: Home, Contratos, Atas
- Indicador de seleção
- Tooltips nos ícones

### 4.3. Home Page (`modules/core/home/`)

**Responsabilidade:** Tela inicial com botões (equivalente a `MainShellView` linhas 51-82)

**Componentes:**
- Botão "Informações do Projeto" → abre dialog
- Botão "Backup do Sistema" → abre dialog/página
- Botão "Ajuda e Suporte" → abre dialog

### 4.4. UASG Search (`modules/features/contratos/pages/uasg-search/`)

**Responsabilidade:** Aba "Buscar UASG" (equivalente a `main_window.py` linhas 34-109)

**Estrutura:**
```
uasg-search/
├── uasg-search.component.ts
├── uasg-search.component.html
└── uasg-search.component.scss
```

**Funcionalidades:**
- **Painel esquerdo:**
  - Input para código UASG
  - Botão "Criação ou atualização da tabela" → chama `ContractsService.syncUasg()`
  - Botão "Deletar Arquivo e Banco de Dados" → chama endpoint de delete
  - Botão "Status" → abre `StatusOptionsDialog`
  - Botão "Tabelas" → abre `TableOptionsDialog`
  - Botão "Contrato Manual" → abre dialog de contratos manuais
  - Badge de status (Online/Offline) → sincronizado com `SettingsService`
- **Painel direito:**
  - `PreviewTableComponent` com contratos mais relevantes
  - Colunas: UASG, Dias, Contrato/Ata, Processo, Fornecedor, Status
  - Cores por dias restantes (verde >180, amarelo ≤179, laranja ≤89, vermelho <0)
  - Clique abre `RecordPopupComponent`

### 4.5. Contracts Table (`modules/features/contratos/pages/contracts-table/`)

**Responsabilidade:** Aba "Visualizar Tabelas" (equivalente a `main_window.py` linhas 110-190)

**Funcionalidades:**
- **Toolbar:**
  - Menu dropdown "UASG" → lista UASGs carregadas
  - Botão "Mensagens" → abre `MessageBuilderPage`
  - Botão "Limpar" → limpa tabela
  - Label "UASG: {code}"
- **Tabela:**
  - `MatTable` com filtro global (barra de busca)
  - Ordenação multi-coluna
  - Context menu (clique direito):
    - Abrir detalhes
    - Gerar relatório
    - Deletar
- **Colunas:** UASG, Número, Processo, Fornecedor, Valor, Vigência, Status
- **Filtros:** Por UASG, status, vigência, fornecedor

### 4.6. Contract Details (`modules/features/contratos/pages/contract-details/`)

**Responsabilidade:** Página de detalhes com tabs (equivalente a `details_dialog.py`)

**Estrutura:**
```
contract-details/
├── contract-details.component.ts
├── contract-details.component.html
└── components/
    ├── contract-general-tab/
    ├── contract-links-tab/
    ├── contract-fiscal-tab/
    ├── contract-status-tab/
    ├── contract-empenhos-tab/
    ├── contract-itens-tab/
    ├── contract-extras-tab/
    └── contract-manual-tabs/
```

**Tabs (para contratos normais):**

#### 4.6.1. General Tab (`contract-general-tab/`)
- Layout duas colunas
- Campos somente leitura com botões copiar
- Radio buttons para "Pode Renovar?", "Custeio?", etc. → binding a `StatusContrato.radio_options_json`
- Botão "Editar Objeto" → abre modal `EditObjectDialog`

#### 4.6.2. Links Tab (`contract-links-tab/`)
- Links automáticos (ComprasNet, PNCP)
- Campos editáveis: `link_contrato`, `link_ta`, `link_portaria`, `link_pncp_espc`, `link_portal_marinha`
- Botão "Buscar Arquivos" → chama `ArquivosService.list()`
- Botões copiar/abrir em cada campo

#### 4.6.3. Fiscal Tab (`contract-fiscal-tab/`)
- Formulário com 7 campos editáveis:
  - `gestor`, `gestor_substituto`
  - `fiscal_tecnico`, `fiscal_tec_substituto`
  - `fiscal_administrativo`, `fiscal_admin_substituto`
  - `observacoes` (textarea)
- Botão salvar → `FiscalizacaoService.update()`
- Botões copiar em cada campo

#### 4.6.4. Status Tab (`contract-status-tab/`)
- Dropdown com 11 status possíveis
- Lista de registros (`registros_status`)
- Botões: "Adicionar", "Excluir", "Copiar"
- Modal para adicionar registro → formato: "DD/MM/AAAA - mensagem - STATUS"

#### 4.6.5. Empenhos Tab (`contract-empenhos-tab/`)
- Botão "Buscar Empenhos" → `EmpenhosService.list()`
- Cards por empenho com: número, data, credor, valores (empenhado, liquidado, pago)
- Filtro por ano (dropdown)
- Botões: "Gerar Relatório XLSX", "Disparar XLSX por E-mail"

#### 4.6.6. Itens Tab (`contract-itens-tab/`)
- Botão "Buscar Itens" → `ItensService.list()`
- Cards por item com: tipo, quantidade, valor unitário, valor total
- Botões: "Gerar Relatório XLSX", "Disparar XLSX por E-mail"

#### 4.6.7. Extras Tab (`contract-extras-tab/`)
- Lista lateral: histórico, empenhos, itens, arquivos
- Viewer JSON com syntax highlighting (`JsonHighlighter`)
- Cache local por chave

**Tabs para Contratos Manuais:**
- `contract-manual-general-tab/` → formulário totalmente editável
- `contract-manual-links-tab/` → links sem automáticos

### 4.7. Dashboard (`modules/features/contratos/pages/dashboard/`)

**Responsabilidade:** Dashboard com KPIs e gráficos (equivalente a `dashboard_tab.py`)

**Componentes:**
- Header com título + botão "Atualizar Dados"
- Grid de 4 cards KPI:
  - Total de Contratos
  - Valor Global Total
  - Contratos Ativos
  - Expirando em 90 dias
- Gráfico de Status (pie/donut) → `StatusChartComponent`
- Placeholder para gráfico 2 (valores por ano)

### 4.8. Message Builder (`modules/features/contratos/pages/message-builder/`)

**Responsabilidade:** Gerador de mensagens (equivalente a `mensagem_view.py`)

**Estrutura:**
- **Aba 1: Gerador**
  - Painel esquerdo: Lista de variáveis disponíveis
  - Painel direito:
    - Editor de template (textarea)
    - Pré-visualização (textarea readonly)
    - Botões de modelos disponíveis
- **Aba 2: Comentários**
  - Lista de comentários salvos
  - Botões: Adicionar, Excluir, Copiar

### 4.9. Settings (`modules/features/contratos/pages/settings/`)

**Responsabilidade:** Configurações (equivalente a `settings_dialog.py`)

**Funcionalidades:**
- Toggle "Modo Online/Offline" → `SettingsService.updateSettings()`
- Campo "Local do Banco de Dados" (readonly)
- Botão "Alterar Local" → abre file picker (via API)
- Botão "Abrir Local" → abre pasta
- Seção "UASGs Offline":
  - Lista de UASGs com botão "Excluir"

### 4.10. Componentes Reutilizáveis (`components/`)

#### 4.10.1. Status Badge (`status-badge/`)
- Badge colorido baseado no status
- Cores: conforme `_get_status_style()` do PyQt

#### 4.10.2. Preview Table (`preview-table/`)
- Tabela compacta com colunas: UASG, Dias, Contrato/Ata, Processo, Fornecedor, Status
- Cálculo de dias restantes
- Cores por dias (verde/amarelo/laranja/vermelho)
- Clique abre popup de registros

#### 4.10.3. JSON Viewer (`json-viewer/`)
- Syntax highlighting (usar `highlight.js` ou `Prism.js`)
- Formatação automática

#### 4.10.4. Link Field (`link-field/`)
- Input + botões copiar/abrir
- Validação de URL

#### 4.10.5. KPI Card (`kpi-card/`)
- Card padronizado com título, valor, ícone

---

## 5. Rotas e Guards

### 5.1. Routes (`routes/app.routes.ts`)

```typescript
import { Routes } from '@angular/router';
import { authGuard } from '../guards/auth.guard';
import { loginGuard } from '../guards/login.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('../pages/login/login.component').then(m => m.LoginComponent),
    canActivate: [loginGuard]
  },
  {
    path: '',
    loadComponent: () => import('../modules/core/shell-layout/shell-layout.component').then(m => m.ShellLayoutComponent),
    canActivate: [authGuard],
    children: [
      {
        path: '',
        loadComponent: () => import('../modules/core/home/home.component').then(m => m.HomeComponent),
        data: { breadcrumb: 'Home' }
      },
      {
        path: 'contratos',
        children: [
          {
            path: '',
            loadComponent: () => import('../modules/features/contratos/pages/uasg-search/uasg-search.component').then(m => m.UasgSearchComponent),
            data: { breadcrumb: 'Buscar UASG' }
          },
          {
            path: 'lista',
            loadComponent: () => import('../modules/features/contratos/pages/contracts-table/contracts-table.component').then(m => m.ContractsTableComponent),
            data: { breadcrumb: 'Visualizar Tabelas' }
          },
          {
            path: ':id',
            loadComponent: () => import('../modules/features/contratos/pages/contract-details/contract-details.component').then(m => m.ContractDetailsComponent),
            data: { breadcrumb: 'Detalhes do Contrato' }
          },
          {
            path: 'mensagens',
            loadComponent: () => import('../modules/features/contratos/pages/message-builder/message-builder.component').then(m => m.MessageBuilderComponent),
            data: { breadcrumb: 'Mensagens' }
          },
          {
            path: 'configuracoes',
            loadComponent: () => import('../modules/features/contratos/pages/settings/settings.component').then(m => m.SettingsComponent),
            data: { breadcrumb: 'Configurações' }
          }
        ]
      },
      {
        path: 'dashboard',
        loadComponent: () => import('../modules/features/contratos/pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
        data: { breadcrumb: 'Dashboard' }
      },
      {
        path: 'atas',
        // Placeholder para módulo de atas
        loadComponent: () => import('../modules/features/atas/pages/atas-list/atas-list.component').then(m => m.AtasListComponent),
        data: { breadcrumb: 'Atas' }
      }
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }
];
```

### 5.2. Auth Guard (`guards/auth.guard.ts`)

```typescript
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
  return false;
};
```

---

## 6. Environments

### 6.1. Environment (`environments/environment.ts`)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost/api/contratos',  // Via nginx
  // apiUrl: 'http://localhost:8000/api/contratos',  // Direto (dev)
  useMockData: false,
  defaultUasg: '787010',
  features: {
    contratos: true,
    atas: false,  // Implementar depois
    backup: true,
    reports: true
  }
};
```

### 6.2. Environment Prod (`environments/environment.prod.ts`)

```typescript
export const environment = {
  production: true,
  apiUrl: '/api/contratos',  // Relativo (via nginx)
  useMockData: false,
  defaultUasg: '787010',
  features: {
    contratos: true,
    atas: false,
    backup: true,
    reports: true
  }
};
```

---

## 7. Mapeamento PyQt → Angular

### 7.1. Views PyQt → Componentes Angular

| View PyQt | Componente Angular | Rota |
|-----------|-------------------|------|
| `MainShellView` | `ShellLayoutComponent` | `/` |
| `MainWindow` (aba Buscar UASG) | `UasgSearchComponent` | `/contratos` |
| `MainWindow` (aba Visualizar Tabelas) | `ContractsTableComponent` | `/contratos/lista` |
| `MainWindow` (aba Dashboard) | `DashboardComponent` | `/dashboard` |
| `DetailsDialog` | `ContractDetailsComponent` | `/contratos/:id` |
| `MensagemDialog` | `MessageBuilderComponent` | `/contratos/mensagens` |
| `SettingsDialog` | `SettingsComponent` | `/contratos/configuracoes` |
| `RecordPopup` | `RecordPopupComponent` | (dialog) |
| `StatusOptionsDialog` | `StatusOptionsDialogComponent` | (dialog) |
| `TableOptionsDialog` | `TableOptionsDialogComponent` | (dialog) |
| `ManualContractDialog` | `ManualContractDialogComponent` | (dialog) |

### 7.2. Tabs de Detalhes

| Tab PyQt | Componente Angular |
|----------|-------------------|
| `general_tab.py` | `ContractGeneralTabComponent` |
| `pdfs_view.py` | `ContractLinksTabComponent` |
| `fiscal_tab.py` | `ContractFiscalTabComponent` |
| `status_tab.py` | `ContractStatusTabComponent` |
| `empenhos_tab.py` | `ContractEmpenhosTabComponent` |
| `itens_tab.py` | `ContractItensTabComponent` |
| `extras_link.py` | `ContractExtrasTabComponent` |
| `general_tab_manual.py` | `ContractManualGeneralTabComponent` |
| `links_tab_manual.py` | `ContractManualLinksTabComponent` |

### 7.3. Controllers PyQt → Services Angular

| Controller PyQt | Service Angular |
|----------------|----------------|
| `UASGModel` | `UasgService` |
| `UASGController` | `ContractsService` + `DashboardService` |
| `DashboardController` | `DashboardService` |
| `MensagemController` | `MessagesService` |
| `SettingsController` | `SettingsService` |
| `ItensController` | `ItensService` |
| `EmpenhosController` | `EmpenhosService` |
| `EmailController` | `ReportsService` |
| `ExpImpTableController` | `ReportsService` |

---

## 8. Endpoints Backend Necessários (A Criar)

Alguns endpoints mencionados nos services ainda não existem no backend. Devem ser criados:

### 8.1. Sincronização
- `POST /api/contratos/sync/?uasg=787010` → Sincronizar UASG
- `POST /api/contratos/sync-detalhes/` → Sincronizar detalhes de um contrato

### 8.2. Import/Export
- `GET /api/contratos/status/export/` → Exportar status (JSON)
- `POST /api/contratos/status/import/` → Importar status (JSON)
- `GET /api/contratos/export/?uasg=787010&format=xlsx` → Exportar tabela (XLSX)

### 8.3. Relatórios
- `GET /api/contratos/empenhos/report/?contrato={id}` → Relatório XLSX de empenhos
- `GET /api/contratos/itens/report/?contrato={id}` → Relatório XLSX de itens
- `POST /api/contratos/reports/send-email/` → Enviar relatório por email

### 8.4. Mensagens
- `GET /api/contratos/messages/templates/` → Lista de templates
- `GET /api/contratos/messages/variables/` → Lista de variáveis
- `POST /api/contratos/messages/preview/` → Preview de mensagem

### 8.5. Settings
- `GET /api/contratos/settings/` → Obter configurações
- `PUT /api/contratos/settings/` → Atualizar configurações

---

## 9. Funcionalidades Específicas

### 9.1. Cálculo de Dias Restantes

```typescript
// utils/date.utils.ts
export function calcularDiasRestantes(vigenciaFim: string | null): number | null {
  if (!vigenciaFim) return null;
  
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  
  const fim = new Date(vigenciaFim);
  fim.setHours(0, 0, 0, 0);
  
  const diffTime = fim.getTime() - hoje.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
}

export function getDiasRestantesStyle(dias: number | null): string {
  if (dias === null) return 'gray';
  if (dias < 0) return 'red';
  if (dias <= 89) return 'orange';
  if (dias <= 179) return 'yellow';
  return 'green';
}
```

### 9.2. Formatação de Valores Monetários

```typescript
// utils/currency.utils.ts
export function formatCurrency(value: number | null): string {
  if (value === null) return 'R$ 0,00';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
}
```

### 9.3. Formatação de Datas

```typescript
// utils/date.utils.ts
export function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Não informado';
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR');
}

export function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return 'Não informado';
  const date = new Date(dateStr);
  return date.toLocaleString('pt-BR');
}
```

### 9.4. Status Colors

```typescript
// utils/status.utils.ts
export const STATUS_COLORS: Record<string, string> = {
  'SEÇÃO CONTRATOS': '#FFFFFF',
  'PORTARIA': '#E6E696',
  'EMPRESA': '#E6E696',
  'SIGDEM': '#E6B464',
  'ASSINADO': '#E6B464',
  'PUBLICADO': '#87CEFA',
  'ALERTA PRAZO': '#FFA0A0',
  'NOTA TÉCNICA': '#FFA0A0',
  'AGU': '#FFA0A0',
  'PRORROGADO': '#87CEFA',
  'SIGAD': '#E6B464'
};
```

---

## 10. Checklist de Implementação

### Fase 1: Estrutura Base
- [ ] Criar estrutura de diretórios
- [ ] Configurar environments
- [ ] Criar guards (auth, login)
- [ ] Configurar interceptors (auth, error)
- [ ] Configurar rotas básicas

### Fase 2: Interfaces e Services
- [ ] Criar todas as interfaces TypeScript
- [ ] Implementar todos os services
- [ ] Testar chamadas HTTP com backend

### Fase 3: Componentes Core
- [ ] ShellLayoutComponent
- [ ] SideNavComponent
- [ ] HomeComponent

### Fase 4: Módulo Contratos - Páginas Principais
- [ ] UasgSearchComponent
- [ ] ContractsTableComponent
- [ ] DashboardComponent

### Fase 5: Detalhes do Contrato
- [ ] ContractDetailsComponent (container)
- [ ] ContractGeneralTabComponent
- [ ] ContractLinksTabComponent
- [ ] ContractFiscalTabComponent
- [ ] ContractStatusTabComponent
- [ ] ContractEmpenhosTabComponent
- [ ] ContractItensTabComponent
- [ ] ContractExtrasTabComponent

### Fase 6: Componentes Reutilizáveis
- [ ] StatusBadgeComponent
- [ ] PreviewTableComponent
- [ ] JsonViewerComponent
- [ ] LinkFieldComponent
- [ ] KpiCardComponent
- [ ] SearchBarComponent

### Fase 7: Funcionalidades Auxiliares
- [ ] MessageBuilderComponent
- [ ] SettingsComponent
- [ ] Dialogs (StatusOptions, TableOptions, ManualContract, RecordPopup)

### Fase 8: Integração e Testes
- [ ] Testar fluxo completo: buscar UASG → abrir contrato → atualizar status
- [ ] Testar geração de relatórios
- [ ] Testar import/export
- [ ] Validar compatibilidade com backend

---

## 11. Observações Importantes

### 11.1. Compatibilidade Backend

- **IDs são strings**: O backend usa `CharField` para `Contrato.id`, então sempre tratar como string
- **Datas em ISO**: Backend retorna datas no formato `YYYY-MM-DD` (ISO)
- **Valores monetários**: Backend retorna `DecimalField` como número (não string)
- **JSON Fields**: `raw_json` e `radio_options_json` são objetos JavaScript (não strings)

### 11.2. Paginação

O backend usa paginação padrão do DRF (100 itens por página). Services devem lidar com:
- `next` e `previous` URLs
- `count` total de resultados
- Carregamento lazy para grandes listas

### 11.3. Modo Online/Offline

A funcionalidade de modo offline do PyQt deve ser adaptada:
- **Online**: Todas as chamadas vão para a API Django
- **Offline**: Backend pode manter cache local, mas frontend sempre chama API

### 11.4. Sincronização

A sincronização com API ComprasNet deve ser feita via backend:
- Frontend chama `POST /api/contratos/sync/?uasg=787010`
- Backend processa e retorna status
- Frontend exibe progresso (pode usar WebSocket ou polling)

---

Este guia fornece todas as orientações necessárias para implementar o frontend Angular compatível com o backend Django já criado.

