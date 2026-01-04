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
    const currentValues = JSON.stringify(this.statusForm.value);
    const initialValues = JSON.stringify(this.initialFormValues);
    const hasChanges = currentValues !== initialValues;
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
      formValues = {
        objeto_editado: status.objeto_editado || '',
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
    this.initialFormValues = JSON.parse(JSON.stringify(formValues));
    this.hasUnsavedChanges.set(false);
  }

  saveStatus(): void {
    if (!this.contratoId || !this.statusForm.valid || this.savingStatus()) {
      return;
    }

    this.savingStatus.set(true);
    const formValue = this.statusForm.value;
    
    const statusData: Partial<StatusContrato> = {
      contrato: this.contratoId,
      status: this.contract?.status?.status || 'SEÇÃO CONTRATOS',
      pode_renovar: formValue.pode_renovar === 'true' || formValue.pode_renovar === true,
      custeio: formValue.custeio === 'true' || formValue.custeio === true,
      natureza_continuada: formValue.natureza_continuada === 'true' || formValue.natureza_continuada === true,
    };
    
    if (this.contract?.uasg) {
      statusData.uasg_code = this.contract.uasg;
    }
    
    if (formValue.objeto_editado && formValue.objeto_editado.trim()) {
      statusData.objeto_editado = formValue.objeto_editado.trim();
    }
    
    if (formValue.tipo_contrato) {
      statusData.tipo_contrato = formValue.tipo_contrato;
    }
    
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
            if (reloadedStatus) {
              this.fillStatusForm(reloadedStatus);
              this.statusSaved.emit(reloadedStatus);
            }
            this.savingStatus.set(false);
            this.hasUnsavedChanges.set(false);
            this.snackBar.open('✅ Alterações salvas com sucesso!', 'Fechar', {
              duration: 3000,
              horizontalPosition: 'end',
              verticalPosition: 'top',
              panelClass: ['success-snackbar']
            });
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
