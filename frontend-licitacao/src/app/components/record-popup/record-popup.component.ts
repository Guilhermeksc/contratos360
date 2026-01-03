import { Component, Input, Output, EventEmitter, OnInit, OnChanges, signal, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { StatusService } from '../../services/status.service';
import { ContractsService } from '../../services/contracts.service';
import { EmpenhosService } from '../../services/empenhos.service';
import { ItensService } from '../../services/itens.service';
import { RegistroStatus, RegistroMensagem } from '../../interfaces/status.interface';
import { ContratoDetail } from '../../interfaces/contrato.interface';
import { Empenho, ItemContrato } from '../../interfaces/offline.interface';
import { JanelaGenerica, BotaoJanela } from '../janela-generica/janela-generica';
import { formatCurrency } from '../../utils/currency.utils';
import { formatDate } from '../../utils/date.utils';

@Component({
  selector: 'app-record-popup',
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
  templateUrl: './record-popup.component.html',
  styleUrl: './record-popup.component.scss'
})
export class RecordPopupComponent implements OnInit, OnChanges {
  @Input() contratoId: string = '';
  @Input() mostrar: boolean = false;
  @Output() fechar = new EventEmitter<void>();

  contract = signal<ContratoDetail | null>(null);
  registrosStatus: RegistroStatus[] = [];
  registrosMensagem: RegistroMensagem[] = [];
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
    private statusService: StatusService,
    private contractsService: ContractsService,
    private empenhosService: EmpenhosService,
    private itensService: ItensService
  ) {}

  ngOnInit(): void {
    // Carrega se já estiver visível na inicialização
    if (this.mostrar && this.contratoId) {
      this.loadContract();
    }
  }

  ngOnChanges(changes: any): void {
    // Recarrega sempre que mostrar mudar para true OU contratoId mudar
    const mostrarChanged = changes.mostrar && changes.mostrar.currentValue === true;
    const contratoIdChanged = changes.contratoId && changes.contratoId.currentValue !== changes.contratoId.previousValue;
    
    if (mostrarChanged || (this.mostrar && contratoIdChanged)) {
      if (this.mostrar && this.contratoId) {
        this.loadContract();
      }
    } else if (changes.mostrar && changes.mostrar.currentValue === false) {
      // Limpa dados quando o popup é fechado
      this.contract.set(null);
      this.registrosStatus = [];
      this.registrosMensagem = [];
      this.empenhos.set([]);
      this.itens.set([]);
      this.loading.set(false);
    }
  }

  private loadContract(): void {
    if (!this.contratoId) {
      console.warn('RecordPopupComponent: contratoId não fornecido');
      return;
    }

    this.loading.set(true);
    
    // Carrega detalhes completos do contrato
    this.contractsService.getDetails(this.contratoId).subscribe({
      next: (contract: ContratoDetail) => {
        // Garante que registros_status e registros_mensagem sejam arrays
        if (contract) {
          contract.registros_status = Array.isArray(contract.registros_status) ? contract.registros_status : [];
          contract.registros_mensagem = Array.isArray(contract.registros_mensagem) ? contract.registros_mensagem : [];
        }
        this.contract.set(contract);
        
        // Carrega registros de status e mensagens
        this.loadRegistros();
      },
      error: (err: any) => {
        console.error('RecordPopupComponent: Erro ao carregar contrato:', err);
        this.loading.set(false);
      }
    });
  }

  private loadRegistros(): void {
    if (!this.contratoId) return;

    // Carrega registros de status e mensagens em paralelo
    let statusLoaded = false;
    let mensagemLoaded = false;

    const checkComplete = () => {
      if (statusLoaded && mensagemLoaded) {
        this.loading.set(false);
        this.setupBotoes();
      }
    };

    this.statusService.listRegistrosStatus(this.contratoId).subscribe({
      next: (registros: RegistroStatus[] | any) => {
        this.registrosStatus = Array.isArray(registros) ? registros : [];
        statusLoaded = true;
        checkComplete();
      },
      error: (err: any) => {
        console.error('RecordPopupComponent: Erro ao carregar registros de status:', err);
        this.registrosStatus = [];
        statusLoaded = true;
        checkComplete();
      }
    });

    this.statusService.listRegistrosMensagem(this.contratoId).subscribe({
      next: (mensagens: RegistroMensagem[] | any) => {
        this.registrosMensagem = Array.isArray(mensagens) ? mensagens : [];
        mensagemLoaded = true;
        checkComplete();
      },
      error: (err: any) => {
        console.error('RecordPopupComponent: Erro ao carregar registros de mensagem:', err);
        this.registrosMensagem = [];
        mensagemLoaded = true;
        checkComplete();
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
        console.error('RecordPopupComponent: Erro ao carregar empenhos:', err);
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
        console.error('RecordPopupComponent: Erro ao carregar itens:', err);
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
    // Não há botões no footer, apenas o botão X superior direito
    this.botoes = [];
  }

  @HostListener('document:keydown.escape', ['$event'])
  handleEscapeKey(event: Event): void {
    if (this.mostrar) {
      const keyboardEvent = event as KeyboardEvent;
      keyboardEvent.preventDefault();
      this.fecharPopup();
    }
  }

  fecharPopup(): void {
    this.mostrar = false;
    this.fechar.emit();
  }

  copiarRegistro(texto: string): void {
    navigator.clipboard.writeText(texto).then(() => {
      // TODO: Mostrar notificação de sucesso
      console.log('Registro copiado:', texto);
    });
  }

  trackByRegistroId(index: number, registro: RegistroStatus): any {
    return registro.id || index;
  }

  trackByMensagemId(index: number, mensagem: RegistroMensagem): any {
    return mensagem.id || index;
  }
}

