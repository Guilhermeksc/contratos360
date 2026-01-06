import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { CalendarioEvento } from '../../../interfaces/calendario.interface';

export interface EventoDialogData {
  data: string; // YYYY-MM-DD
  evento: CalendarioEvento | null;
}

@Component({
  selector: 'app-evento-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './evento-dialog.component.html',
  styleUrl: './evento-dialog.component.scss'
})
export class EventoDialogComponent implements OnInit {
  eventoForm: FormGroup;
  isEditMode: boolean;

  coresPadrao = [
    { nome: 'Azul', valor: '#3788d8' },
    { nome: 'Verde', valor: '#51cf66' },
    { nome: 'Vermelho', valor: '#ff6b6b' },
    { nome: 'Amarelo', valor: '#ffd93d' },
    { nome: 'Roxo', valor: '#9775fa' },
    { nome: 'Laranja', valor: '#ff922b' },
  ];

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<EventoDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EventoDialogData
  ) {
    this.isEditMode = !!data.evento;
    
    this.eventoForm = this.fb.group({
      nome: ['', [Validators.required, Validators.maxLength(255)]],
      data: [data.data, [Validators.required]],
      descricao: [''],
      cor: ['#3788d8', [Validators.required]]
    });
  }

  ngOnInit(): void {
    if (this.data.evento) {
      this.eventoForm.patchValue({
        nome: this.data.evento.nome,
        data: this.data.evento.data,
        descricao: this.data.evento.descricao || '',
        cor: this.data.evento.cor || '#3788d8'
      });
    }
  }

  onSave(): void {
    if (this.eventoForm.valid) {
      const formValue = this.eventoForm.value;
      
      // Converte Date para string YYYY-MM-DD se necessário
      let dataStr = formValue.data;
      if (dataStr instanceof Date) {
        const year = dataStr.getFullYear();
        const month = String(dataStr.getMonth() + 1).padStart(2, '0');
        const day = String(dataStr.getDate()).padStart(2, '0');
        dataStr = `${year}-${month}-${day}`;
      } else if (typeof dataStr === 'string' && dataStr.includes('T')) {
        // Se vier com hora, remove a parte da hora
        dataStr = dataStr.split('T')[0];
      }
      
      const eventoData = {
        nome: formValue.nome,
        data: dataStr,
        descricao: formValue.descricao || null,
        cor: formValue.cor
      };

      if (this.isEditMode) {
        this.dialogRef.close({ action: 'update', ...eventoData });
      } else {
        this.dialogRef.close(eventoData);
      }
    }
  }

  onDelete(): void {
    this.dialogRef.close({ action: 'delete' });
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}

