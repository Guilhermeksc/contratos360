import { Component, Input, Output, EventEmitter, OnChanges, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-combobox',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './combobox.html',
  styleUrl: './combobox.scss',
})
export class Combobox implements OnChanges, AfterViewInit {
  @Input() label: string = '';
  @Input() value: any = null;
  @Input() options: any[] = [];
  @Input() disabled: boolean = false;
  @Input() placeholder: string = 'Selecione uma opção';
  @Input() hint: string = '';
  @Input() trackBy: string = '';
  @Input() displayFn: ((item: any) => string) | null = null;
  @Input() emptyMessage: string = '';

  @Output() valueChange = new EventEmitter<any>();

  @ViewChild('selectElement', { static: false }) selectElement?: ElementRef<HTMLSelectElement>;

  private originalValueType: 'number' | 'string' | 'other' = 'other';

  ngOnChanges(): void {
    // Detecta o tipo do valor original para converter corretamente
    if (this.value !== null && this.value !== undefined) {
      if (typeof this.value === 'number') {
        this.originalValueType = 'number';
      } else if (typeof this.value === 'string') {
        this.originalValueType = 'string';
      }
    } else if (this.options.length > 0) {
      // Tenta inferir o tipo pela primeira opção
      const firstOption = this.options[0];
      const firstValue = this.getOptionValue(firstOption);
      if (!isNaN(Number(firstValue)) && firstValue !== '') {
        this.originalValueType = 'number';
      } else {
        this.originalValueType = 'string';
      }
    }

    // Atualiza o valor do select quando as opções ou valor mudarem
    if (this.selectElement?.nativeElement) {
      setTimeout(() => {
        this.updateSelectValue();
      }, 0);
    }
  }

  ngAfterViewInit(): void {
    // Garante que o valor seja definido após a view ser inicializada
    setTimeout(() => {
      this.updateSelectValue();
    }, 0);
  }

  private updateSelectValue(): void {
    if (this.selectElement?.nativeElement) {
      const selectValue = this.getSelectValue();
      if (this.selectElement.nativeElement.value !== selectValue) {
        this.selectElement.nativeElement.value = selectValue;
      }
    }
  }

  onSelectionChange(value: string): void {
    if (value === '' || value === null || value === undefined) {
      this.valueChange.emit(null);
      return;
    }

    // Converte para o tipo original
    if (this.originalValueType === 'number') {
      const numValue = Number(value);
      this.valueChange.emit(isNaN(numValue) ? value : numValue);
    } else {
      this.valueChange.emit(value);
    }
  }

  getDisplayText(option: any): string {
    if (this.displayFn) {
      return this.displayFn(option);
    }
    return String(option);
  }

  getOptionValue(option: any): string {
    if (this.trackBy && option && typeof option === 'object') {
      return String(option[this.trackBy]);
    }
    return String(option);
  }

  getSelectValue(): string {
    if (this.value === null || this.value === undefined) {
      return '';
    }
    return String(this.value);
  }
}
