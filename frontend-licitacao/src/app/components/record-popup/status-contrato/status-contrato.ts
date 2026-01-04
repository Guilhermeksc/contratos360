import { Component, Input, Output, EventEmitter, OnInit, OnChanges, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatRadioModule } from '@angular/material/radio';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { StatusService } from '../../../services/status.service';
import { StatusContrato } from '../../../interfaces/status.interface';
import { ContratoDetail } from '../../../interfaces/contrato.interface';

@Component({
  selector: 'app-status-contrato',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatRadioModule,
    MatSnackBarModule,
    ReactiveFormsModule
  ],
  templateUrl: './status-contrato.html',
  styleUrl: './status-contrato.scss'
})
export class StatusContratoComponent implements OnInit, OnChanges {
  @Input() contratoId: string = '';
  @Input() contract: ContratoDetail | null = null;
  @Output() statusSaved = new EventEmitter<StatusContrato>();
  @Output() unsavedChanges = new EventEmitter<boolean>();

  statusForm!: FormGroup;
  savingStatus = signal(false);
  statusLoaded = signal(false);
  hasUnsavedChanges = signal(false);
  initialFormValues: any = {};

  constructor(
    private statusService: StatusService,
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ) {
    this.initializeStatusForm();
  }

  ngOnInit(): void {
    if (this.contratoId && this.contract) {
      this.loadStatus();
    }
  }

  ngOnChanges(changes: any): void {
    if (changes.contratoId || changes.contract) {
      if (this.contratoId && this.contract) {
        this.loadStatus();
      }
    }
  }

  private initializeStatusForm(): void {
    this.statusForm = this.fb.group({
      objeto_editado: [''],
      pode_renovar: ['false'],
      custeio: ['false'],
      natureza_continuada: ['false'],
      tipo_contrato: [null]
    });
    
    this.statusForm.valueChanges.subscribe(() => {
      if (this.statusLoaded()) {
        this.checkForUnsavedChanges();
      }
    });
  }

  private checkForUnsavedChanges(): void {
    if (!this.statusLoaded()) {
      return;
    }
    
    const current = this.statusForm.value;
    const initial = this.initialFormValues || {};
    
    // Aplica trim() consistentemente no objeto_editado para comparação
    const currentObjeto = (current.objeto_editado || '').trim();
    const initialObjeto = (initial.objeto_editado || '').trim();
    
    // Compara cada campo individualmente para garantir detecção correta
    const hasChanges = 
      currentObjeto !== initialObjeto ||
      (current.pode_renovar || 'false') !== (initial.pode_renovar || 'false') ||
      (current.custeio || 'false') !== (initial.custeio || 'false') ||
      (current.natureza_continuada || 'false') !== (initial.natureza_continuada || 'false') ||
      (current.tipo_contrato || null) !== (initial.tipo_contrato || null);
    
    this.hasUnsavedChanges.set(hasChanges);
    this.unsavedChanges.emit(hasChanges);
  }

  private loadStatus(): void {
    if (!this.contratoId) return;

    // Se o contrato já tem status, usa ele diretamente
    if (this.contract?.status) {
      this.fillStatusForm(this.contract.status);
      this.statusLoaded.set(true);
    } else {
      // Se não tem status no contrato, carrega do servidor
      this.statusService.getStatus(this.contratoId, true).subscribe({
        next: (status: StatusContrato | null) => {
          this.fillStatusForm(status);
          this.statusLoaded.set(true);
        },
        error: (err: any) => {
          console.error('StatusContratoComponent: Erro ao carregar status:', err);
          this.fillStatusForm(null);
          this.statusLoaded.set(true);
        }
      });
    }
  }

  private fillStatusForm(status: StatusContrato | null): void {
    let formValues: any;
    
    if (status) {
      // Aplica trim() no objeto_editado para garantir consistência
      formValues = {
        objeto_editado: (status.objeto_editado || '').trim(),
        pode_renovar: status.pode_renovar ? 'true' : 'false',
        custeio: status.custeio ? 'true' : 'false',
        natureza_continuada: status.natureza_continuada ? 'true' : 'false',
        tipo_contrato: status.tipo_contrato || null
      };
    } else {
      formValues = {
        objeto_editado: '',
        pode_renovar: 'false',
        custeio: 'false',
        natureza_continuada: 'false',
        tipo_contrato: null
      };
    }
    
    this.statusForm.patchValue(formValues, { emitEvent: false });
    // Salva uma cópia profunda dos valores iniciais (já com trim aplicado)
    this.initialFormValues = {
      objeto_editado: formValues.objeto_editado || '',
      pode_renovar: formValues.pode_renovar || 'false',
      custeio: formValues.custeio || 'false',
      natureza_continuada: formValues.natureza_continuada || 'false',
      tipo_contrato: formValues.tipo_contrato || null
    };
    this.hasUnsavedChanges.set(false);
    this.unsavedChanges.emit(false);
  }

  saveStatus(): void {
    if (!this.contratoId) {
      console.error('StatusContratoComponent: contratoId não fornecido');
      return;
    }
    
    if (this.savingStatus()) {
      console.warn('StatusContratoComponent: Já está salvando, ignorando chamada');
      return;
    }
    
    // Não verifica statusForm.valid porque os campos são opcionais
    // e podem estar vazios/null sem problema

    this.savingStatus.set(true);
    const formValue = this.statusForm.value;
    
    // Converte valores de string para boolean
    const pode_renovar = formValue.pode_renovar === 'true' || formValue.pode_renovar === true;
    const custeio = formValue.custeio === 'true' || formValue.custeio === true;
    const natureza_continuada = formValue.natureza_continuada === 'true' || formValue.natureza_continuada === true;
    
    // Processa objeto_editado - sempre envia, mesmo se vazio
    const objeto_editado = formValue.objeto_editado ? formValue.objeto_editado.trim() : null;
    
    const statusData: Partial<StatusContrato> = {
      contrato: this.contratoId,
      status: this.contract?.status?.status || 'SEÇÃO CONTRATOS',
      pode_renovar: pode_renovar,
      custeio: custeio,
      natureza_continuada: natureza_continuada,
      objeto_editado: objeto_editado,
      tipo_contrato: formValue.tipo_contrato || null,
    };
    
    if (this.contract?.uasg) {
      statusData.uasg_code = this.contract.uasg;
    }
    
    // Preserva campos existentes do status atual
    const currentStatus = this.contract?.status;
    if (currentStatus) {
      if (currentStatus.portaria_edit) statusData.portaria_edit = currentStatus.portaria_edit;
      if (currentStatus.termo_aditivo_edit) statusData.termo_aditivo_edit = currentStatus.termo_aditivo_edit;
      if (currentStatus.data_registro) statusData.data_registro = currentStatus.data_registro;
    }
    
    this.statusService.createOrUpdateStatus(statusData).subscribe({
      next: (savedStatus: StatusContrato) => {
        // Recarrega o status do servidor
        this.statusService.getStatus(this.contratoId, true).subscribe({
          next: (reloadedStatus: StatusContrato | null) => {
            console.log('Status recarregado após salvar:', reloadedStatus);
            // Sempre emite o evento, mesmo se reloadedStatus for null (usa savedStatus como fallback)
            const statusToEmit = reloadedStatus || savedStatus;
            
            if (reloadedStatus) {
              // Preenche o formulário com os dados recarregados (isso atualiza os valores iniciais)
              this.fillStatusForm(reloadedStatus);
            } else {
              // Se não conseguiu recarregar, usa o status salvo
              this.fillStatusForm(savedStatus);
            }
            
            // Emite evento para o componente pai
            console.log('Emitindo evento statusSaved com:', statusToEmit);
            this.statusSaved.emit(statusToEmit);
            this.savingStatus.set(false);
            // fillStatusForm já atualiza hasUnsavedChanges e emite o evento
          },
          error: (err: any) => {
            console.error('Erro ao recarregar status após salvar:', err);
            this.fillStatusForm(savedStatus);
            this.statusSaved.emit(savedStatus);
            this.savingStatus.set(false);
          }
        });
      },
      error: (err: any) => {
        console.error('Erro ao salvar status:', err);
        this.savingStatus.set(false);
        
        let errorMessage = 'Erro ao salvar status';
        if (err.error) {
          if (err.error.non_field_errors) {
            errorMessage = err.error.non_field_errors.join(', ');
          } else if (err.error.detail) {
            errorMessage = err.error.detail;
          }
        }
        
        this.snackBar.open(`❌ Erro ao salvar: ${errorMessage}`, 'Fechar', {
          duration: 5000,
          horizontalPosition: 'end',
          verticalPosition: 'top',
          panelClass: ['error-snackbar']
        });
      }
    });
  }
}
