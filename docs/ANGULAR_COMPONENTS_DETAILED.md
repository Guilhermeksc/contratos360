# Guia Detalhado de Componentes Angular

Este documento complementa o guia principal com detalhes de implementação de cada componente.

## 📋 Componentes Detalhados

### 1. UASG Search Component

**Arquivo:** `modules/features/contratos/pages/uasg-search/uasg-search.component.ts`

```typescript
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContractsService } from '../../../../services/contracts.service';
import { SettingsService } from '../../../../services/settings.service';
import { UasgService } from '../../../../services/uasg.service';
import { PreviewTableComponent } from '../../../../components/preview-table/preview-table.component';
import { StatusOptionsDialogComponent } from '../../components/status-options-dialog/status-options-dialog.component';
import { TableOptionsDialogComponent } from '../../components/table-options-dialog/table-options-dialog.component';
import { ManualContractDialogComponent } from '../../components/manual-contract-dialog/manual-contract-dialog.component';

@Component({
  selector: 'app-uasg-search',
  standalone: true,
  imports: [CommonModule, FormsModule, PreviewTableComponent],
  template: `
    <div class="uasg-search-container">
      <!-- Painel Esquerdo -->
      <div class="left-panel">
        <button (click)="openSettings()" class="settings-button">
          <mat-icon>settings</mat-icon>
        </button>
        
        <label>Digite o número do UASG:</label>
        <input 
          type="text" 
          [(ngModel)]="uasgCode" 
          placeholder="Ex: 787010"
          (keyup.enter)="syncUasg()"
        />
        
        <button (click)="syncUasg()" [disabled]="syncing">
          <mat-icon>api</mat-icon>
          Criação ou atualização da tabela
        </button>
        
        <button (click)="deleteUasg()" [disabled]="!uasgCode">
          <mat-icon>delete</mat-icon>
          Deletar Arquivo e Banco de Dados
        </button>
        
        <button (click)="openStatusOptions()">
          <mat-icon>status</mat-icon>
          Status
        </button>
        
        <button (click)="openTableOptions()">
          <mat-icon>table</mat-icon>
          Tabelas
        </button>
        
        <button (click)="openManualContract()">
          <mat-icon>add</mat-icon>
          Contrato Manual
        </button>
        
        <!-- Badge de Status -->
        <div class="status-badge">
          <mat-icon [class]="mode() === 'Online' ? 'online' : 'offline'">
            {{ mode() === 'Online' ? 'link' : 'database' }}
          </mat-icon>
          <span>{{ mode() }}</span>
        </div>
      </div>
      
      <!-- Painel Direito - Preview -->
      <div class="right-panel">
        <h3>Contratos em andamento</h3>
        <div class="preview-actions">
          <button (click)="refreshPreview()">
            <mat-icon>refresh</mat-icon>
            Atualizar Pré-visualização
          </button>
          <button (click)="adjustColumns()">
            <mat-icon>view_column</mat-icon>
            Ajustar Colunas
          </button>
        </div>
        <app-preview-table 
          [data]="previewData()"
          (rowClick)="showRecordPopup($event)"
        ></app-preview-table>
      </div>
    </div>
  `
})
export class UasgSearchComponent implements OnInit {
  uasgCode = '';
  syncing = false;
  mode = signal<'Online' | 'Offline'>('Online');
  previewData = signal<any[]>([]);

  constructor(
    private contractsService: ContractsService,
    private settingsService: SettingsService,
    private uasgService: UasgService
  ) {}

  ngOnInit(): void {
    this.settingsService.mode$.subscribe(mode => this.mode.set(mode));
    this.loadPreviewData();
  }

  syncUasg(): void {
    if (!this.uasgCode) return;
    
    this.syncing = true;
    this.contractsService.syncUasg(this.uasgCode).subscribe({
      next: () => {
        this.loadPreviewData();
        this.syncing = false;
      },
      error: (err) => {
        console.error('Erro ao sincronizar:', err);
        this.syncing = false;
      }
    });
  }

  deleteUasg(): void {
    // Implementar confirmação e chamada ao endpoint
  }

  openStatusOptions(): void {
    // Abrir dialog StatusOptionsDialogComponent
  }

  openTableOptions(): void {
    // Abrir dialog TableOptionsDialogComponent
  }

  openManualContract(): void {
    // Abrir dialog ManualContractDialogComponent
  }

  refreshPreview(): void {
    this.loadPreviewData();
  }

  adjustColumns(): void {
    // Ajustar colunas da tabela preview
  }

  showRecordPopup(contratoId: string): void {
    // Abrir RecordPopupComponent com registros do contrato
  }

  private loadPreviewData(): void {
    // Buscar contratos ativos e próximos a vencer
    this.contractsService.getAtivos().subscribe(contratos => {
      this.previewData.set(contratos);
    });
  }
}
```

### 2. Contracts Table Component

**Arquivo:** `modules/features/contratos/pages/contracts-table/contracts-table.component.ts`

```typescript
import { Component, OnInit, ViewChild, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { ContractsService, ContratoFilters } from '../../../../services/contracts.service';
import { UasgService } from '../../../../services/uasg.service';
import { Contrato } from '../../../../interfaces/contrato.interface';

@Component({
  selector: 'app-contracts-table',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatMenuModule,
    MatButtonModule,
    MatInputModule,
    MatIconModule
  ],
  template: `
    <div class="contracts-table-container">
      <!-- Toolbar -->
      <div class="toolbar">
        <button mat-button [matMenuTriggerFor]="uasgMenu">
          <mat-icon>data-server</mat-icon>
          UASG
        </button>
        <mat-menu #uasgMenu="matMenu">
          <button mat-menu-item *ngFor="let uasg of uasgs()" (click)="filterByUasg(uasg.uasg_code)">
            {{ uasg.uasg_code }} - {{ uasg.nome_resumido }}
          </button>
        </mat-menu>
        
        <button mat-button (click)="openMessages()">
          <mat-icon>message</mat-icon>
          Mensagens
        </button>
        
        <button mat-icon-button (click)="clearTable()" [matTooltip]="mode() === 'Online' ? 'Limpar Tabela (Modo Online)' : 'Limpar Tabela (Modo Offline)'">
          <mat-icon>{{ mode() === 'Online' ? 'link' : 'database' }}</mat-icon>
        </button>
        
        <span class="spacer"></span>
        
        <label class="uasg-info">UASG: {{ currentUasg() || '-' }}</label>
      </div>
      
      <!-- Barra de Busca -->
      <mat-form-field appearance="outline" class="search-bar">
        <mat-label>Buscar</mat-label>
        <input matInput [(ngModel)]="searchTerm" (input)="applyFilter()" placeholder="Número, processo, fornecedor, objeto...">
        <mat-icon matPrefix>search</mat-icon>
      </mat-form-field>
      
      <!-- Tabela -->
      <table mat-table [dataSource]="dataSource" matSort class="contracts-table">
        <ng-container matColumnDef="uasg">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>UASG</th>
          <td mat-cell *matCellDef="let row">{{ row.uasg }}</td>
        </ng-container>
        
        <ng-container matColumnDef="numero">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Número</th>
          <td mat-cell *matCellDef="let row">{{ row.numero }}</td>
        </ng-container>
        
        <ng-container matColumnDef="processo">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Processo</th>
          <td mat-cell *matCellDef="let row">{{ row.processo }}</td>
        </ng-container>
        
        <ng-container matColumnDef="fornecedor_nome">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Fornecedor</th>
          <td mat-cell *matCellDef="let row">{{ row.fornecedor_nome }}</td>
        </ng-container>
        
        <ng-container matColumnDef="valor_global">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Valor</th>
          <td mat-cell *matCellDef="let row">{{ formatCurrency(row.valor_global) }}</td>
        </ng-container>
        
        <ng-container matColumnDef="vigencia_fim">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Vigência Fim</th>
          <td mat-cell *matCellDef="let row">{{ formatDate(row.vigencia_fim) }}</td>
        </ng-container>
        
        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>Status</th>
          <td mat-cell *matCellDef="let row">
            <app-status-badge [status]="row.status_atual || 'SEÇÃO CONTRATOS'"></app-status-badge>
          </td>
        </ng-container>
        
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>Ações</th>
          <td mat-cell *matCellDef="let row">
            <button mat-icon-button [matMenuTriggerFor]="menu">
              <mat-icon>more_vert</mat-icon>
            </button>
            <mat-menu #menu="matMenu">
              <button mat-menu-item (click)="openDetails(row.id)">
                <mat-icon>visibility</mat-icon>
                Ver Detalhes
              </button>
              <button mat-menu-item (click)="generateReport(row.id)">
                <mat-icon>description</mat-icon>
                Gerar Relatório
              </button>
              <button mat-menu-item (click)="deleteContract(row.id)">
                <mat-icon>delete</mat-icon>
                Deletar
              </button>
            </mat-menu>
          </td>
        </ng-container>
        
        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns" (contextmenu)="showContextMenu($event, row)"></tr>
      </table>
      
      <!-- Paginação -->
      <mat-paginator [pageSizeOptions]="[25, 50, 100]" showFirstLastButtons></mat-paginator>
    </div>
  `
})
export class ContractsTableComponent implements OnInit {
  displayedColumns: string[] = ['uasg', 'numero', 'processo', 'fornecedor_nome', 'valor_global', 'vigencia_fim', 'status', 'actions'];
  dataSource = new MatTableDataSource<Contrato>([]);
  searchTerm = '';
  uasgs = signal<any[]>([]);
  currentUasg = signal<string | null>(null);
  mode = signal<'Online' | 'Offline'>('Online');

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private contractsService: ContractsService,
    private uasgService: UasgService,
    private router: Router,
    private settingsService: SettingsService
  ) {}

  ngOnInit(): void {
    this.loadUasgs();
    this.loadContracts();
    this.settingsService.mode$.subscribe(mode => this.mode.set(mode));
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  filterByUasg(uasgCode: string): void {
    this.currentUasg.set(uasgCode);
    this.loadContracts({ uasg: uasgCode });
  }

  applyFilter(): void {
    this.dataSource.filter = this.searchTerm.trim().toLowerCase();
  }

  openDetails(contratoId: string): void {
    this.router.navigate(['/contratos', contratoId]);
  }

  clearTable(): void {
    this.dataSource.data = [];
    this.currentUasg.set(null);
  }

  private loadUasgs(): void {
    this.uasgService.list().subscribe(uasgs => {
      this.uasgs.set(uasgs);
    });
  }

  private loadContracts(filters?: ContratoFilters): void {
    this.contractsService.list(filters).subscribe(response => {
      this.dataSource.data = response.results;
    });
  }
}
```

### 3. Contract Details Component

**Arquivo:** `modules/features/contratos/pages/contract-details/contract-details.component.ts`

```typescript
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { ContractsService } from '../../../../services/contracts.service';
import { ContratoDetail } from '../../../../interfaces/contrato.interface';

@Component({
  selector: 'app-contract-details',
  standalone: true,
  imports: [CommonModule, MatTabsModule],
  template: `
    <div class="contract-details-container">
      <div class="header">
        <button mat-icon-button (click)="goBack()">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Detalhes do Contrato {{ contract()?.numero }}</h1>
      </div>
      
      <mat-tab-group>
        <mat-tab label="Geral">
          <app-contract-general-tab [contract]="contract()"></app-contract-general-tab>
        </mat-tab>
        
        <mat-tab label="Links">
          <app-contract-links-tab [contract]="contract()"></app-contract-links-tab>
        </mat-tab>
        
        <mat-tab label="Fiscalização">
          <app-contract-fiscal-tab [contract]="contract()"></app-contract-fiscal-tab>
        </mat-tab>
        
        <mat-tab label="Status">
          <app-contract-status-tab [contract]="contract()"></app-contract-status-tab>
        </mat-tab>
        
        <mat-tab label="Empenhos">
          <app-contract-empenhos-tab [contract]="contract()"></app-contract-empenhos-tab>
        </mat-tab>
        
        <mat-tab label="Itens">
          <app-contract-itens-tab [contract]="contract()"></app-contract-itens-tab>
        </mat-tab>
        
        <mat-tab label="Extras">
          <app-contract-extras-tab [contract]="contract()"></app-contract-extras-tab>
        </mat-tab>
        
        <!-- Tabs para contratos manuais (condicional) -->
        <mat-tab *ngIf="contract()?.manual" label="Manual - Geral">
          <app-contract-manual-general-tab [contract]="contract()"></app-contract-manual-general-tab>
        </mat-tab>
        
        <mat-tab *ngIf="contract()?.manual" label="Manual - Links">
          <app-contract-manual-links-tab [contract]="contract()"></app-contract-manual-links-tab>
        </mat-tab>
      </mat-tab-group>
    </div>
  `
})
export class ContractDetailsComponent implements OnInit {
  contract = signal<ContratoDetail | null>(null);
  loading = signal(true);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contractsService: ContractsService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadContract(id);
    }
  }

  loadContract(id: string): void {
    this.loading.set(true);
    this.contractsService.getDetails(id).subscribe({
      next: (contract) => {
        this.contract.set(contract);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Erro ao carregar contrato:', err);
        this.loading.set(false);
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/contratos/lista']);
  }
}
```

### 4. Contract Status Tab Component

**Arquivo:** `modules/features/contratos/components/contract-status-tab/contract-status-tab.component.ts`

```typescript
import { Component, Input, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatDialog } from '@angular/material/dialog';
import { StatusService } from '../../../../services/status.service';
import { ContratoDetail } from '../../../../interfaces/contrato.interface';
import { AddRegistroDialogComponent } from '../add-registro-dialog/add-registro-dialog.component';

const STATUS_OPTIONS = [
  'SEÇÃO CONTRATOS',
  'EMPRESA',
  'SIGDEM',
  'SIGAD',
  'ASSINADO',
  'PUBLICADO',
  'PORTARIA',
  'ALERTA PRAZO',
  'NOTA TÉCNICA',
  'AGU',
  'PRORROGADO'
];

@Component({
  selector: 'app-contract-status-tab',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSelectModule, MatButtonModule, MatListModule],
  template: `
    <div class="status-tab-container">
      <!-- Dropdown de Status -->
      <div class="status-selector">
        <label>Status:</label>
        <select [(ngModel)]="selectedStatus" (change)="updateStatus()">
          <option *ngFor="let status of statusOptions" [value]="status">
            {{ status }}
          </option>
        </select>
      </div>
      
      <!-- Lista de Registros -->
      <div class="registros-section">
        <h3>Registros</h3>
        <mat-list>
          <mat-list-item *ngFor="let registro of registros()">
            {{ registro }}
            <button mat-icon-button (click)="deleteRegistro(registro)">
              <mat-icon>delete</mat-icon>
            </button>
            <button mat-icon-button (click)="copyRegistro(registro)">
              <mat-icon>content_copy</mat-icon>
            </button>
          </mat-list-item>
        </mat-list>
        
        <div class="registro-actions">
          <button mat-raised-button (click)="addRegistro()">
            <mat-icon>add</mat-icon>
            Adicionar Registro
          </button>
          <button mat-raised-button (click)="deleteSelectedRegistros()" [disabled]="selectedRegistros().length === 0">
            <mat-icon>delete</mat-icon>
            Excluir Selecionados
          </button>
          <button mat-raised-button (click)="copyAllRegistros()">
            <mat-icon>content_copy</mat-icon>
            Copiar Todos
          </button>
        </div>
      </div>
    </div>
  `
})
export class ContractStatusTabComponent implements OnInit {
  @Input() contract: ContratoDetail | null = null;
  
  statusOptions = STATUS_OPTIONS;
  selectedStatus = signal<string>('SEÇÃO CONTRATOS');
  registros = signal<string[]>([]);
  selectedRegistros = signal<string[]>([]);

  constructor(
    private statusService: StatusService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    if (this.contract) {
      this.selectedStatus.set(this.contract.status?.status || 'SEÇÃO CONTRATOS');
      this.registros.set(this.contract.registros_status || []);
    }
  }

  updateStatus(): void {
    if (!this.contract) return;
    
    this.statusService.updateStatus(this.contract.id, {
      status: this.selectedStatus()
    }).subscribe(() => {
      // Atualizar localmente
    });
  }

  addRegistro(): void {
    const dialogRef = this.dialog.open(AddRegistroDialogComponent, {
      width: '500px',
      data: { contratoId: this.contract?.id }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Formato: "DD/MM/AAAA - mensagem - STATUS"
        const registroTexto = `${this.formatDate(new Date())} - ${result.mensagem} - ${result.status}`;
        
        this.statusService.createRegistroStatus({
          contrato: this.contract!.id,
          uasg_code: this.contract!.uasg,
          texto: registroTexto
        }).subscribe(() => {
          this.loadRegistros();
        });
      }
    });
  }

  deleteRegistro(texto: string): void {
    // Buscar ID do registro e deletar
    this.statusService.listRegistrosStatus(this.contract!.id).subscribe(registros => {
      const registro = registros.find(r => r.texto === texto);
      if (registro) {
        this.statusService.deleteRegistroStatus(registro.id).subscribe(() => {
          this.loadRegistros();
        });
      }
    });
  }

  private loadRegistros(): void {
    if (!this.contract) return;
    
    this.statusService.listRegistrosStatus(this.contract.id).subscribe(registros => {
      this.registros.set(registros.map(r => r.texto));
    });
  }

  private formatDate(date: Date): string {
    return date.toLocaleDateString('pt-BR');
  }
}
```

---

## 📝 Notas de Compatibilidade

### Campos que Precisam de Conversão

1. **Datas**: Backend retorna `YYYY-MM-DD`, frontend deve formatar para `DD/MM/YYYY` na exibição
2. **Valores Monetários**: Backend retorna número, frontend deve formatar como `R$ 1.234,56`
3. **Radio Options**: Backend retorna JSON, frontend deve parsear e bindar aos radio buttons
4. **Registros de Status**: Backend retorna array de strings, frontend deve exibir em lista

### Endpoints que Precisam ser Criados no Backend

Consulte a seção 8 do guia principal para lista completa de endpoints a criar.

---

Este documento complementa o guia principal com exemplos práticos de implementação.

