import { Component, OnInit, ViewChild, signal, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { ContractsService, ContratoFilters } from '../../../../../services/contracts.service';
import { UasgService } from '../../../../../services/uasg.service';
import { SettingsService } from '../../../../../services/settings.service';
import { Contrato } from '../../../../../interfaces/contrato.interface';
import { Uasg } from '../../../../../interfaces/uasg.interface';
import { StatusBadgeComponent } from '../../../../../components/status-badge/status-badge.component';
import { ContractDetailsPopupComponent } from '../../../../../components/contract-details-popup/contract-details-popup.component';
import { formatCurrency } from '../../../../../utils/currency.utils';
import { formatDate } from '../../../../../utils/date.utils';

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
    MatIconModule,
    MatFormFieldModule,
    MatPaginatorModule,
    MatSortModule,
    MatTooltipModule,
    StatusBadgeComponent,
    ContractDetailsPopupComponent
  ],
  templateUrl: './contracts-table.component.html',
  styleUrl: './contracts-table.component.scss'
})
export class ContractsTableComponent implements OnInit, AfterViewInit {
  displayedColumns: string[] = ['uasg', 'numero', 'processo', 'fornecedor_nome', 'valor_global', 'vigencia_fim', 'status', 'actions'];
  dataSource = new MatTableDataSource<Contrato>([]);
  searchTerm = '';
  uasgs = signal<Uasg[]>([]);
  currentUasg = signal<string | null>(null);
  mode = signal<'Online' | 'Offline'>('Online');
  loading = signal(false);
  showDetailsPopup = signal(false);
  selectedContratoId = signal<string>('');

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  formatCurrency = formatCurrency;
  formatDate = formatDate;

  constructor(
    private contractsService: ContractsService,
    private uasgService: UasgService,
    private router: Router,
    private settingsService: SettingsService
  ) {}

  ngOnInit(): void {
    this.loadUasgs();
    this.loadContracts();
    this.settingsService.mode$.subscribe((mode: 'Online' | 'Offline') => this.mode.set(mode));
  }

  ngAfterViewInit(): void {
    // Configura paginator e sort após a view estar inicializada
    if (this.paginator) {
      this.dataSource.paginator = this.paginator;
    }
    if (this.sort) {
      this.dataSource.sort = this.sort;
    }
  }

  filterByUasg(uasgCode: string): void {
    this.currentUasg.set(uasgCode);
    this.loadContracts({ uasg: uasgCode });
  }

  applyFilter(): void {
    this.dataSource.filter = this.searchTerm.trim().toLowerCase();
  }

  openDetails(contratoId: string): void {
    this.selectedContratoId.set(contratoId);
    this.showDetailsPopup.set(true);
  }

  closeDetailsPopup(): void {
    this.showDetailsPopup.set(false);
    this.selectedContratoId.set('');
  }

  openMessages(): void {
    this.router.navigate(['/contratos/mensagens']);
  }

  clearTable(): void {
    this.dataSource.data = [];
    this.currentUasg.set(null);
  }

  generateReport(contratoId: string): void {
    // TODO: Implementar geração de relatório
    console.log('Gerar relatório para:', contratoId);
  }

  deleteContract(contratoId: string): void {
    // TODO: Implementar confirmação e delete
    console.log('Deletar contrato:', contratoId);
  }

  showContextMenu(event: MouseEvent, row: Contrato): void {
    event.preventDefault();
    // Context menu será implementado com MatMenu
  }

  private loadUasgs(): void {
    this.uasgService.list().subscribe({
      next: (uasgs: Uasg[] | any) => {
        // Garante que seja sempre um array
        const uasgsArray = Array.isArray(uasgs) ? uasgs : [];
        console.log('ContractsTableComponent: UASGs carregadas:', uasgsArray.length);
        this.uasgs.set(uasgsArray);
      },
      error: (err: any) => {
        console.error('Erro ao carregar UASGs:', err);
        this.uasgs.set([]);
      }
    });
  }

  private loadContracts(filters?: ContratoFilters): void {
    this.loading.set(true);
    this.contractsService.list(filters).subscribe({
      next: (response: { count: number; results: Contrato[]; next: string | null; previous: string | null } | any) => {
        // Garante que response.results seja um array
        const contratos = Array.isArray(response?.results) ? response.results : [];
        console.log('ContractsTableComponent: Contratos carregados:', contratos.length, 'de', response?.count || '?');
        this.dataSource.data = contratos;
        
        // Reconfigura paginator e sort após atualizar os dados
        if (this.paginator) {
          this.dataSource.paginator = this.paginator;
        }
        if (this.sort) {
          this.dataSource.sort = this.sort;
        }
        
        this.loading.set(false);
      },
      error: (err: any) => {
        console.error('Erro ao carregar contratos:', err);
        this.dataSource.data = [];
        this.loading.set(false);
      }
    });
  }
}

