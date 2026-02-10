import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as XLSX from 'xlsx';
import { ContractsService } from '../../services/contracts.service';
import { UasgService } from '../../services/uasg.service';
import { PreviewTableComponent } from '../../components/preview-table/preview-table.component';
import { RecordPopupComponent } from '../../components/record-popup/record-popup.component';
import { PageHeaderComponent } from '../../components/page-header/page-header.component';
import { Contrato } from '../../interfaces/contrato.interface';
import { Combobox } from '../../components/combobox/combobox';
import { FiltroBusca } from '../../components/filtro-busca/filtro-busca';
import { calcularDiasRestantes } from '../../utils/date.utils';
import { formatCurrency } from '../../utils/currency.utils';

@Component({
  selector: 'app-contratos',
  standalone: true,
  imports: [
    CommonModule,
    PreviewTableComponent,
    RecordPopupComponent,
    PageHeaderComponent,
    Combobox,
    FiltroBusca
  ],
  templateUrl: './contratos.component.html',
  styleUrl: './contratos.component.scss'
})
export class ContratosComponent implements OnInit {
  private readonly uasgFilterStorageKey = 'contratos.selectedUasgFilter';
  previewData = signal<Contrato[]>([]);
  filteredPreviewData = signal<Contrato[]>([]);
  searchTerm = signal('');
  selectedUasgFilter: string | null = null;
  uasgs = signal<any[]>([]);
  showRecordPopup = signal(false);
  selectedContratoId = signal<string>('');
  isDarkTheme = signal<boolean>(false); // Tema claro (branco) por padrão

  constructor(
    private contractsService: ContractsService,
    private uasgService: UasgService
  ) {}

  ngOnInit(): void {
    this.restoreUasgFilter();
    this.loadUasgs();
    this.loadPreviewData();
    
    // Observa mudanças no termo de busca e aplica filtro
    this.searchTerm.set('');
  }

  onUasgFilterChange(): void {
    this.persistUasgFilter();
    this.applyFilter();
  }

  onUasgFilterValueChange(value: string | null): void {
    this.selectedUasgFilter = value;
    this.onUasgFilterChange();
  }

  onSearchChange(searchValue: string): void {
    this.searchTerm.set(searchValue);
    this.applyFilter();
  }

  getUasgOptions(): Array<{ value: string; label: string }> {
    return this.uasgs()
      .map(uasg => {
        const code = (uasg.uasg_code ?? uasg.uasg ?? '').toString();
        const sigla = uasg.sigla_om || 'Sem sigla';
        return { value: code, label: `${code} - ${sigla}` };
      })
      .filter(option => option.value !== '');
  }

  getUasgOptionLabel = (option: { value: string; label: string }): string => option.label;

  exportarContratosXlsx(): void {
    const contratos = this.filteredPreviewData();
    if (contratos.length === 0) {
      return;
    }

    const data = contratos.map(contrato => ({
      UASG: contrato.uasg_sigla || contrato.uasg_nome || 'N/A',
      'Código UASG': contrato.uasg?.toString() || 'N/A',
      Dias: calcularDiasRestantes(contrato.vigencia_fim) ?? 'Sem Data',
      Contrato: contrato.numero || 'N/A',
      ID: contrato.id || 'N/A',
      'Número / Nup': contrato.licitacao_numero || 'N/A',
      Processo: contrato.processo || 'N/A',
      Fornecedor: contrato.fornecedor_nome || 'N/A',
      CNPJ: contrato.fornecedor_cnpj || 'N/A',
      Objeto: contrato.objeto || 'N/A',
      'Valor Global': formatCurrency(contrato.valor_global)
    }));

    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'contratos');
    XLSX.writeFile(wb, `Contratos_${new Date().toISOString().slice(0, 10)}.xlsx`);
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
            
            console.log('ContratosComponent: UASGs com contratos:', uasgsComContratos.length, uasgsComContratos);
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

  toggleTableTheme(): void {
    this.isDarkTheme.set(!this.isDarkTheme());
  }

  onThemeToggle(isDark: boolean): void {
    this.isDarkTheme.set(isDark);
  }

  private loadPreviewData(): void {
    // Buscar contratos ativos e próximos a vencer
    this.contractsService.getAtivos().subscribe({
      next: (contratos: Contrato[] | any) => {
        // Garante que seja sempre um array
        const contratosArray = Array.isArray(contratos) ? contratos : [];
        console.log('ContratosComponent: Contratos carregados:', contratosArray.length);
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

  private restoreUasgFilter(): void {
    const saved = localStorage.getItem(this.uasgFilterStorageKey);
    this.selectedUasgFilter = saved ? saved : null;
  }

  private persistUasgFilter(): void {
    if (!this.selectedUasgFilter) {
      localStorage.removeItem(this.uasgFilterStorageKey);
      return;
    }
    localStorage.setItem(this.uasgFilterStorageKey, this.selectedUasgFilter);
  }
}

