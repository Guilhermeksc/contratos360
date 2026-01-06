import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ContractsService } from '../../../../../services/contracts.service';
import { UasgService } from '../../../../../services/uasg.service';
import { PreviewTableComponent } from '../../../../../components/preview-table/preview-table.component';
import { RecordPopupComponent } from '../../../../../components/record-popup/record-popup.component';
import { Contrato } from '../../../../../interfaces/contrato.interface';

@Component({
  selector: 'app-uasg-search',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    PreviewTableComponent,
    RecordPopupComponent
  ],
  templateUrl: './uasg-search.component.html',
  styleUrl: './uasg-search.component.scss'
})
export class UasgSearchComponent implements OnInit {
  uasgCode = '';
  syncing = signal(false);
  previewData = signal<Contrato[]>([]);
  filteredPreviewData = signal<Contrato[]>([]);
  searchTerm = signal('');
  selectedUasgFilter: string | null = null;
  uasgs = signal<any[]>([]);
  showRecordPopup = signal(false);
  selectedContratoId = signal<string>('');

  constructor(
    private contractsService: ContractsService,
    private uasgService: UasgService
  ) {}

  ngOnInit(): void {
    this.loadUasgs();
    this.loadPreviewData();
    
    // Observa mudanças no termo de busca e aplica filtro
    this.searchTerm.set('');
  }

  onUasgFilterChange(): void {
    this.applyFilter();
  }

  onSearchChange(searchValue: string): void {
    this.searchTerm.set(searchValue);
    this.applyFilter();
  }

  applyFilter(): void {
    const term = this.searchTerm().toLowerCase().trim();
    const uasgFilter = this.selectedUasgFilter;
    const data = this.previewData();
    
    let filtered = data;
    
    // Aplica filtro de UASG primeiro
    if (uasgFilter) {
      filtered = filtered.filter(contrato => {
        const contratoUasg = contrato.uasg?.toString() || '';
        const filterUasg = uasgFilter?.toString() || '';
        return contratoUasg === filterUasg;
      });
    }
    
    // Aplica filtro de busca de texto
    if (term) {
      filtered = filtered.filter(contrato => {
        // Busca em múltiplos campos
        const searchFields = [
          contrato.processo?.toLowerCase() || '',
          contrato.fornecedor_nome?.toLowerCase() || '',
          contrato.fornecedor_cnpj?.toLowerCase() || '',
          contrato.objeto?.toLowerCase() || '',
          contrato.numero?.toLowerCase() || '',
          contrato.id?.toLowerCase() || '',
          contrato.uasg_nome?.toLowerCase() || '',
          contrato.uasg?.toString().toLowerCase() || ''
        ];
        
        return searchFields.some(field => field.includes(term));
      });
    }
    
    this.filteredPreviewData.set(filtered);
  }

  private loadUasgs(): void {
    // Carrega apenas UASGs que têm contratos associados
    this.contractsService.getAtivos().subscribe({
      next: (contratos: Contrato[]) => {
        // Extrai códigos UASG únicos dos contratos
        const uasgCodes = new Set<string>();
        contratos.forEach(contrato => {
          if (contrato.uasg) {
            uasgCodes.add(contrato.uasg.toString());
          }
        });
        
        // Busca informações das UASGs que têm contratos
        this.uasgService.list().subscribe({
          next: (todasUasgs: any[] | any) => {
            const todasUasgsArray = Array.isArray(todasUasgs) ? todasUasgs : [];
            // Filtra apenas UASGs que têm contratos
            const uasgsComContratos = todasUasgsArray.filter((uasg: any) => {
              const uasgCode = uasg.uasg_code || uasg.uasg?.toString();
              return uasgCode && uasgCodes.has(uasgCode.toString());
            });
            
            // Ordena por código UASG
            uasgsComContratos.sort((a: any, b: any) => {
              const codeA = (a.uasg_code || a.uasg || '').toString();
              const codeB = (b.uasg_code || b.uasg || '').toString();
              return codeA.localeCompare(codeB);
            });
            
            console.log('UasgSearchComponent: UASGs com contratos:', uasgsComContratos.length, uasgsComContratos);
            this.uasgs.set(uasgsComContratos);
          },
          error: (err: any) => {
            console.error('Erro ao carregar UASGs:', err);
            this.uasgs.set([]);
          }
        });
      },
      error: (err: any) => {
        console.error('Erro ao carregar contratos para filtrar UASGs:', err);
        // Em caso de erro, tenta carregar todas as UASGs como fallback
        this.uasgService.list().subscribe({
          next: (uasgs: any[] | any) => {
            const uasgsArray = Array.isArray(uasgs) ? uasgs : [];
            this.uasgs.set(uasgsArray);
          },
          error: (err2: any) => {
            console.error('Erro ao carregar UASGs (fallback):', err2);
            this.uasgs.set([]);
          }
        });
      }
    });
  }

  syncUasg(): void {
    if (!this.uasgCode.trim()) return;
    
    this.syncing.set(true);
    this.contractsService.syncUasg(this.uasgCode).subscribe({
      next: () => {
        this.loadPreviewData();
        this.loadUasgs(); // Recarrega UASGs após sincronização
        this.syncing.set(false);
      },
      error: (err: any) => {
        console.error('Erro ao sincronizar:', err);
        this.syncing.set(false);
      }
    });
  }


  showRecordPopupHandler(contratoId: string): void {
    this.selectedContratoId.set(contratoId);
    this.showRecordPopup.set(true);
  }

  closeRecordPopup(): void {
    this.showRecordPopup.set(false);
    this.selectedContratoId.set('');
  }

  onRecordSaved(): void {
    // Recarrega os dados da tabela quando houver salvamento no popup
    this.loadPreviewData();
    this.loadUasgs(); // Recarrega UASGs caso tenha mudado
  }

  private loadPreviewData(): void {
    // Buscar contratos ativos e próximos a vencer
    this.contractsService.getAtivos().subscribe({
      next: (contratos: Contrato[] | any) => {
        // Garante que seja sempre um array
        const contratosArray = Array.isArray(contratos) ? contratos : [];
        console.log('UasgSearchComponent: Contratos carregados:', contratosArray.length);
        this.previewData.set(contratosArray);
        this.applyFilter(); // Aplica o filtro após carregar os dados
      },
      error: (err: any) => {
        console.error('Erro ao carregar preview:', err);
        this.previewData.set([]);
        this.filteredPreviewData.set([]);
      }
    });
  }
}

