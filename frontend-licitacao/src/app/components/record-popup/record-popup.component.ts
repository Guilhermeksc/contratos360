import { Component, Input, Output, EventEmitter, OnInit, OnChanges, signal, HostListener, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { StatusService } from '../../services/status.service';
import { ContractsService } from '../../services/contracts.service';
import { RegistroStatus, RegistroMensagem, StatusContrato } from '../../interfaces/status.interface';
import { ContratoDetail } from '../../interfaces/contrato.interface';
import { JanelaGenerica, BotaoJanela } from '../janela-generica/janela-generica';
import { ConfirmDialogComponent } from '../confirm-dialog/confirm-dialog.component';
import { formatCurrency } from '../../utils/currency.utils';
import { formatDate } from '../../utils/date.utils';
import { StatusContratoComponent } from './status-contrato/status-contrato';
import { FiscalizacaoContratoComponent } from './fiscalizacao-contrato/fiscalizacao-contrato';
import { EmpenhosContratoComponent } from './empenhos-contrato/empenhos-contrato';
import { ItensContratoComponent } from './itens-contrato/itens-contrato';
import { HistoricoContratoComponent } from './historico-contrato/historico-contrato';
import { StatusContratoViewComponent } from './status-contrato-view/status-contrato-view';

@Component({
  selector: 'app-record-popup',
  standalone: true,
  imports: [
    CommonModule,
    MatTabsModule,
    MatIconModule,
    MatButtonModule,
    MatSnackBarModule,
    MatDialogModule,
    JanelaGenerica,
    StatusContratoComponent,
    FiscalizacaoContratoComponent,
    EmpenhosContratoComponent,
    ItensContratoComponent,
    HistoricoContratoComponent,
    StatusContratoViewComponent
  ],
  templateUrl: './record-popup.component.html',
  styleUrl: './record-popup.component.scss'
})
export class RecordPopupComponent implements OnInit, OnChanges {
  @Input() contratoId: string = '';
  @Input() mostrar: boolean = false;
  @Output() fechar = new EventEmitter<void>();
  @Output() saved = new EventEmitter<void>();

  @ViewChild(StatusContratoViewComponent) statusViewComponent?: StatusContratoViewComponent;

  contract = signal<ContratoDetail | null>(null);
  registrosStatus: RegistroStatus[] = [];
  registrosMensagem: RegistroMensagem[] = [];
  loading = signal(false);
  botoes: BotaoJanela[] = [];
  hasUnsavedChanges = signal(false);
  hasUnsavedStatusChanges = signal(false);
  headerButton: BotaoJanela | null = null;
  private dialogOpen = false;

  formatCurrency = formatCurrency;
  formatDate = formatDate;

  constructor(
    private statusService: StatusService,
    private contractsService: ContractsService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {}

  get popupTitle(): string {
    const c = this.contract();
    if (!c) return `Registros do Contrato ${this.contratoId}`;
    
    const numero = c.numero || this.contratoId;
    // Tenta pegar uasg_nome do contrato, se não tiver, pega do status
    const uasgNome = c.uasg_nome || c.status?.uasg_nome || '';
    const uasg = c.uasg || '';
    const modalidade = c.modalidade || '';
    
    // Formato: Registro do contrato {numero} - {uasg nome}({uasg}) - {modalidade}
    let title = `Registro do contrato ${numero}`;
    if (uasgNome && uasg) {
      title += ` - ${uasgNome} (${uasg})`;
    } else if (uasgNome) {
      title += ` - ${uasgNome}`;
    } else if (uasg) {
      title += ` - (${uasg})`;
    }
    if (modalidade) {
      title += ` - ${modalidade}`;
    }
    
    return title;
  }

  onStatusUnsavedChanges(hasChanges: boolean): void {
    this.hasUnsavedChanges.set(hasChanges);
  }

  onStatusTabUnsavedChanges(hasChanges: boolean): void {
    this.hasUnsavedStatusChanges.set(hasChanges);
    this.updateHeaderButton();
  }

  updateHeaderButton(): void {
    if (this.hasUnsavedStatusChanges()) {
      this.headerButton = {
        texto: 'Salvar Status',
        tipo: 'primary',
        disabled: false,
        acao: () => this.saveStatusTab()
      };
    } else {
      this.headerButton = null;
    }
  }

  saveStatusTab(): void {
    if (this.statusViewComponent) {
      this.statusViewComponent.saveStatus();
    }
  }

  onStatusSaved(status: StatusContrato): void {
    // Atualiza o status no contrato local
    const currentContract = this.contract();
    if (currentContract) {
      currentContract.status = status;
      this.contract.set({ ...currentContract });
    }
    // Emite evento para atualizar a tabela
    this.saved.emit();
  }

  onStatusUpdated(status: StatusContrato): void {
    // Atualiza o status no contrato local quando atualizado na tab Status
    const currentContract = this.contract();
    if (currentContract) {
      currentContract.status = status;
      this.contract.set({ ...currentContract });
    }
    // Reseta o estado de alterações não salvas
    this.hasUnsavedStatusChanges.set(false);
    this.updateHeaderButton();
    // Emite evento para atualizar a tabela
    this.saved.emit();
    
    // Recarrega o contrato completo para garantir que todos os dados estão atualizados
    if (this.contratoId) {
      this.contractsService.getDetails(this.contratoId).subscribe({
        next: (updatedContract: ContratoDetail) => {
          this.contract.set(updatedContract);
        },
        error: (err: any) => {
          console.error('Erro ao recarregar contrato após atualizar status:', err);
        }
      });
    }
  }

  onRegistrosUpdated(): void {
    // Recarrega os registros de status e mensagens
    this.loadRegistros();
    // Emite evento para atualizar a tabela (registros podem afetar o status exibido)
    this.saved.emit();
  }

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
      this.loading.set(false);
      this.hasUnsavedChanges.set(false);
      this.hasUnsavedStatusChanges.set(false);
      this.headerButton = null;
      this.dialogOpen = false; // Reseta a flag ao fechar o popup
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


  private setupBotoes(): void {
    // Não há botões no footer, apenas o botão X superior direito
    this.botoes = [];
  }

  @HostListener('document:keydown.escape', ['$event'])
  handleEscapeKey(event: Event): void {
    // Se há um diálogo aberto, não processa o ESC aqui (deixa o diálogo processar)
    if (this.dialogOpen) {
      return;
    }
    
    if (this.mostrar) {
      const keyboardEvent = event as KeyboardEvent;
      keyboardEvent.preventDefault();
      this.tentarFecharPopup();
    }
  }

  tentarFecharPopup(): void {
    // Evita abrir múltiplos diálogos
    if (this.dialogOpen) {
      return;
    }
    
    // Verifica se há alterações não salvas (formulário de informações gerais ou status tab)
    if (this.hasUnsavedChanges() || this.hasUnsavedStatusChanges()) {
      // Marca que o diálogo está aberto
      this.dialogOpen = true;
      
      // Mostra diálogo de confirmação
      const dialogRef = this.dialog.open(ConfirmDialogComponent, {
        width: '450px',
        data: {
          title: 'Alterações não salvas',
          message: 'Você tem alterações não salvas. Deseja realmente fechar sem salvar?',
          confirmText: 'Fechar sem salvar',
          cancelText: 'Cancelar'
        }
      });

      dialogRef.afterClosed().subscribe(result => {
        // Marca que o diálogo foi fechado
        this.dialogOpen = false;
        
        if (result === true) {
          this.fecharPopup();
        }
      });
    } else {
      this.fecharPopup();
    }
  }

  fecharPopup(): void {
    this.mostrar = false;
    this.dialogOpen = false; // Reseta a flag ao fechar
    this.fechar.emit();
  }

}

