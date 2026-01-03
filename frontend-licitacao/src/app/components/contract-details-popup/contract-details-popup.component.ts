import { Component, Input, Output, EventEmitter, OnInit, OnChanges, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { ContractsService } from '../../services/contracts.service';
import { EmpenhosService } from '../../services/empenhos.service';
import { ItensService } from '../../services/itens.service';
import { ContratoDetail } from '../../interfaces/contrato.interface';
import { Empenho, ItemContrato } from '../../interfaces/offline.interface';
import { JanelaGenerica, BotaoJanela } from '../janela-generica/janela-generica';
import { formatCurrency } from '../../utils/currency.utils';
import { formatDate } from '../../utils/date.utils';

@Component({
  selector: 'app-contract-details-popup',
  standalone: true,
  imports: [
    CommonModule,
    MatTabsModule,
    MatIconModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    FormsModule,
    JanelaGenerica
  ],
  templateUrl: './contract-details-popup.component.html',
  styleUrl: './contract-details-popup.component.scss'
})
export class ContractDetailsPopupComponent implements OnInit, OnChanges {
  @Input() contratoId: string = '';
  @Input() mostrar: boolean = false;
  @Output() fechar = new EventEmitter<void>();

  contract = signal<ContratoDetail | null>(null);
  loading = signal(false);
  loadingEmpenhos = signal(false);
  loadingItens = signal(false);
  botoes: BotaoJanela[] = [];

  empenhos = signal<Empenho[]>([]);
  itens = signal<ItemContrato[]>([]);
  selectedYear: string = 'Todos';
  availableYears: string[] = [];

  formatCurrency = formatCurrency;
  formatDate = formatDate;

  constructor(
    private contractsService: ContractsService,
    private empenhosService: EmpenhosService,
    private itensService: ItensService
  ) {}

  ngOnInit(): void {
    if (this.mostrar && this.contratoId) {
      this.loadContract();
    }
  }

  ngOnChanges(changes: any): void {
    const mostrarChanged = changes.mostrar && changes.mostrar.currentValue === true;
    const contratoIdChanged = changes.contratoId && changes.contratoId.currentValue !== changes.contratoId.previousValue;
    
    if (mostrarChanged || (this.mostrar && contratoIdChanged)) {
      if (this.mostrar && this.contratoId) {
        this.loadContract();
      }
    } else if (changes.mostrar && changes.mostrar.currentValue === false) {
      this.contract.set(null);
      this.loading.set(false);
    }
  }

  private loadContract(): void {
    if (!this.contratoId) {
      console.warn('ContractDetailsPopupComponent: contratoId não fornecido');
      return;
    }

    this.loading.set(true);
    this.contractsService.getDetails(this.contratoId).subscribe({
      next: (contract: ContratoDetail) => {
        // Garante que registros_status e registros_mensagem sejam arrays
        if (contract) {
          contract.registros_status = Array.isArray(contract.registros_status) ? contract.registros_status : [];
          contract.registros_mensagem = Array.isArray(contract.registros_mensagem) ? contract.registros_mensagem : [];
        }
        this.contract.set(contract);
        this.loading.set(false);
        this.setupBotoes();
      },
      error: (err: any) => {
        console.error('Erro ao carregar contrato:', err);
        this.loading.set(false);
      }
    });
  }

  loadEmpenhos(): void {
    if (!this.contratoId || this.empenhos().length > 0) return;
    
    this.loadingEmpenhos.set(true);
    this.empenhosService.list(this.contratoId).subscribe({
      next: (empenhos: Empenho[]) => {
        this.empenhos.set(Array.isArray(empenhos) ? empenhos : []);
        // Extrai anos únicos das datas de emissão
        const years = new Set<string>();
        empenhos.forEach(e => {
          if (e.data_emissao) {
            const year = e.data_emissao.substring(0, 4);
            if (year) years.add(year);
          }
        });
        this.availableYears = Array.from(years).sort().reverse();
        this.loadingEmpenhos.set(false);
      },
      error: (err: any) => {
        console.error('Erro ao carregar empenhos:', err);
        this.empenhos.set([]);
        this.loadingEmpenhos.set(false);
      }
    });
  }

  loadItens(): void {
    if (!this.contratoId || this.itens().length > 0) return;
    
    this.loadingItens.set(true);
    this.itensService.list(this.contratoId).subscribe({
      next: (itens: ItemContrato[]) => {
        this.itens.set(Array.isArray(itens) ? itens : []);
        this.loadingItens.set(false);
      },
      error: (err: any) => {
        console.error('Erro ao carregar itens:', err);
        this.itens.set([]);
        this.loadingItens.set(false);
      }
    });
  }

  getFilteredEmpenhos(): Empenho[] {
    if (this.selectedYear === 'Todos') {
      return this.empenhos();
    }
    return this.empenhos().filter(e => 
      e.data_emissao && e.data_emissao.startsWith(this.selectedYear)
    );
  }

  private setupBotoes(): void {
    this.botoes = [
      {
        texto: 'Fechar',
        tipo: 'secondary',
        acao: () => this.fecharPopup()
      }
    ];
  }

  fecharPopup(): void {
    this.mostrar = false;
    this.fechar.emit();
  }
}

