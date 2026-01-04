import { Component, Inject, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
}

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule],
  template: `
    <div class="confirm-dialog">
      <div class="dialog-header">
        <img src="/assets/img/svg/alert.svg" alt="Alerta" class="alert-icon" />
        <h2>{{ data.title }}</h2>
      </div>
      <div mat-dialog-content>
        <p>{{ data.message }}</p>
      </div>
      <div mat-dialog-actions align="end">
        <button mat-button class="cancel-button" (click)="onCancel()">
          {{ data.cancelText || 'Cancelar' }}
        </button>
        <button mat-raised-button class="confirm-button danger-button" (click)="onConfirm()">
          {{ data.confirmText || 'Confirmar' }}
        </button>
      </div>
    </div>
  `,
  styleUrl: './confirm-dialog.component.scss'
})
export class ConfirmDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmDialogData
  ) {}

  @HostListener('document:keydown.escape', ['$event'])
  handleEscapeKey(event: Event): void {
    const keyboardEvent = event as KeyboardEvent;
    keyboardEvent.preventDefault();
    keyboardEvent.stopPropagation();
    this.onCancel();
  }

  @HostListener('document:keydown.enter', ['$event'])
  handleEnterKey(event: Event): void {
    const keyboardEvent = event as KeyboardEvent;
    // Só processa Enter se não estiver em um input ou textarea
    const target = keyboardEvent.target as HTMLElement;
    if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA' && target.tagName !== 'BUTTON') {
      keyboardEvent.preventDefault();
      keyboardEvent.stopPropagation();
      this.onConfirm();
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  onConfirm(): void {
    this.dialogRef.close(true);
  }
}

