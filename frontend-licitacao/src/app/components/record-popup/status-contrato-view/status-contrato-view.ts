import { Component, Input, Output, EventEmitter, OnInit, OnChanges, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FormsModule } from '@angular/forms';
import { StatusService } from '../../../services/status.service';
import { StatusContrato, RegistroStatus, RegistroMensagem } from '../../../interfaces/status.interface';

@Component({
  selector: 'app-status-contrato-view',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatSnackBarModule,
    FormsModule
  ],
  templateUrl: './status-contrato-view.html',
  styleUrl: './status-contrato-view.scss'
})
export class StatusContratoViewComponent implements OnInit, OnChanges {
  @Input() status: StatusContrato | null = null;
  @Input() registrosStatus: RegistroStatus[] = [];
  @Input() registrosMensagem: RegistroMensagem[] = [];
  @Input() contratoId: string = '';
  @Input() uasgCode: string = '';
  
  @Output() statusUpdated = new EventEmitter<StatusContrato>();
  @Output() registrosUpdated = new EventEmitter<void>();
  @Output() unsavedChanges = new EventEmitter<boolean>();

  // Opções de status disponíveis
  statusOptions = [
    'SEÇÃO CONTRATOS',
    'ALERTA PRAZO',
    'PORTARIA',
    'PRORROGADO',
    'SIGDEM',
    'ASSINADO',
    'PUBLICADO',
    'NOTA',
    'AGU',
    'SIGAD'
  ];

  selectedStatus: string = '';
  initialStatus: string = '';
  registrosStatusSignal = signal<RegistroStatus[]>([]);
  registrosMensagemSignal = signal<RegistroMensagem[]>([]);
  
  // Formulário para novo registro
  showAddRegistroForm = false;
  novoRegistroTexto = '';
  savingStatus = false;
  savingRegistro = false;
  deletingRegistro = signal<number | null>(null);
  hasUnsavedChanges = signal(false);

  constructor(
    private statusService: StatusService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.initializeComponent();
  }

  ngOnChanges(changes: any): void {
    if (changes.status || changes.registrosStatus || changes.registrosMensagem) {
      this.initializeComponent();
    }
  }

  private initializeComponent(): void {
    const currentStatus = this.status?.status || 'SEÇÃO CONTRATOS';
    this.selectedStatus = currentStatus;
    this.initialStatus = currentStatus;
    this.registrosStatusSignal.set(this.registrosStatus || []);
    this.registrosMensagemSignal.set(this.registrosMensagem || []);
    this.checkForUnsavedChanges();
  }

  onStatusChange(): void {
    // Apenas detecta alterações, não salva automaticamente
    this.checkForUnsavedChanges();
  }

  private checkForUnsavedChanges(): void {
    const hasChanges = this.selectedStatus !== this.initialStatus;
    this.hasUnsavedChanges.set(hasChanges);
    this.unsavedChanges.emit(hasChanges);
  }

  saveStatus(): void {
    if (!this.contratoId) {
      return;
    }

    if (this.selectedStatus === this.initialStatus) {
      return; // Sem mudanças
    }

    this.savingStatus = true;
    
    // Se não existe status, cria um novo com valores padrão
    const statusData: Partial<StatusContrato> = {
      contrato: this.contratoId,
      status: this.selectedStatus,
      uasg_code: this.uasgCode || this.status?.uasg_code || '',
      pode_renovar: this.status?.pode_renovar || false,
      custeio: this.status?.custeio || false,
      natureza_continuada: this.status?.natureza_continuada || false,
      tipo_contrato: this.status?.tipo_contrato || null,
      objeto_editado: this.status?.objeto_editado || null,
      portaria_edit: this.status?.portaria_edit || null,
      termo_aditivo_edit: this.status?.termo_aditivo_edit || null,
      data_registro: this.status?.data_registro || null
    };

    this.statusService.createOrUpdateStatus(statusData).subscribe({
      next: (updatedStatus: StatusContrato) => {
        this.savingStatus = false;
        this.initialStatus = updatedStatus.status || 'SEÇÃO CONTRATOS';
        this.selectedStatus = updatedStatus.status || 'SEÇÃO CONTRATOS';
        this.checkForUnsavedChanges();
        // Emite evento para atualizar o componente pai (importante quando status é criado pela primeira vez)
        this.statusUpdated.emit(updatedStatus);
        this.registrosUpdated.emit();
        
        // Não mostra snackbar aqui, será mostrado pelo componente pai
      },
      error: (err: any) => {
        console.error('Erro ao atualizar status:', err);
        this.savingStatus = false;
        this.selectedStatus = this.initialStatus; // Reverte
        this.checkForUnsavedChanges();
        
        let errorMessage = 'Erro ao atualizar status';
        if (err.error?.detail) {
          errorMessage = err.error.detail;
        }
        
        this.snackBar.open(`❌ ${errorMessage}`, 'Fechar', {
          duration: 5000,
          horizontalPosition: 'end',
          verticalPosition: 'top',
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  toggleAddRegistroForm(): void {
    this.showAddRegistroForm = !this.showAddRegistroForm;
    if (!this.showAddRegistroForm) {
      this.novoRegistroTexto = '';
    }
  }

  adicionarRegistro(): void {
    if (!this.contratoId || !this.novoRegistroTexto.trim()) {
      return;
    }

    this.savingRegistro = true;
    
    const registroData = {
      contrato: this.contratoId,
      uasg_code: this.uasgCode || this.status?.uasg_code || '',
      texto: this.novoRegistroTexto.trim()
    };

    this.statusService.createRegistroStatus(registroData).subscribe({
      next: (novoRegistro: RegistroStatus) => {
        this.savingRegistro = false;
        this.registrosStatusSignal.set([...this.registrosStatusSignal(), novoRegistro]);
        this.novoRegistroTexto = '';
        this.showAddRegistroForm = false;
        this.registrosUpdated.emit();
        
        this.snackBar.open('✅ Registro adicionado com sucesso!', 'Fechar', {
          duration: 3000,
          horizontalPosition: 'end',
          verticalPosition: 'top',
          panelClass: ['success-snackbar']
        });
      },
      error: (err: any) => {
        console.error('Erro ao adicionar registro:', err);
        this.savingRegistro = false;
        
        let errorMessage = 'Erro ao adicionar registro';
        if (err.error?.detail) {
          errorMessage = err.error.detail;
        } else if (err.error?.texto) {
          errorMessage = err.error.texto.join(', ');
        }
        
        this.snackBar.open(`❌ ${errorMessage}`, 'Fechar', {
          duration: 5000,
          horizontalPosition: 'end',
          verticalPosition: 'top',
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  excluirRegistro(registro: RegistroStatus): void {
    if (!registro.id) {
      return;
    }

    if (!confirm(`Deseja realmente excluir este registro?\n\n"${registro.texto}"`)) {
      return;
    }

    this.deletingRegistro.set(registro.id);
    
    this.statusService.deleteRegistroStatus(registro.id).subscribe({
      next: () => {
        this.registrosStatusSignal.set(
          this.registrosStatusSignal().filter(r => r.id !== registro.id)
        );
        this.deletingRegistro.set(null);
        this.registrosUpdated.emit();
        
        this.snackBar.open('✅ Registro excluído com sucesso!', 'Fechar', {
          duration: 3000,
          horizontalPosition: 'end',
          verticalPosition: 'top',
          panelClass: ['success-snackbar']
        });
      },
      error: (err: any) => {
        console.error('Erro ao excluir registro:', err);
        this.deletingRegistro.set(null);
        
        let errorMessage = 'Erro ao excluir registro';
        if (err.error?.detail) {
          errorMessage = err.error.detail;
        }
        
        this.snackBar.open(`❌ ${errorMessage}`, 'Fechar', {
          duration: 5000,
          horizontalPosition: 'end',
          verticalPosition: 'top',
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  copiarRegistro(texto: string): void {
    navigator.clipboard.writeText(texto).then(() => {
      this.snackBar.open('✅ Texto copiado!', 'Fechar', {
        duration: 2000,
        horizontalPosition: 'end',
        verticalPosition: 'top',
        panelClass: ['success-snackbar']
      });
    });
  }

  trackByRegistroId(index: number, registro: RegistroStatus): any {
    return registro.id || index;
  }

  trackByMensagemId(index: number, mensagem: RegistroMensagem): any {
    return mensagem.id || index;
  }
}
