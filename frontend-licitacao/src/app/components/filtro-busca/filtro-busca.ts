import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-filtro-busca',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './filtro-busca.html',
  styleUrl: './filtro-busca.scss',
})
export class FiltroBusca implements OnChanges {
  @Input() label: string = '';
  @Input() placeholder: string = '';
  @Input() value: string = '';
  @Input() disabled: boolean = false;
  @Input() hint: string = '';
  @Input() showClearButton: boolean = true;
  @Input() options: any[] = [];
  @Input() displayFn: ((item: any) => string) | null = null;
  @Input() trackBy: string = '';
  @Input() maxOptions: number = 10;

  @Output() valueChange = new EventEmitter<string>();
  @Output() enterPressed = new EventEmitter<string>();
  @Output() optionSelected = new EventEmitter<any>();

  showDropdown: boolean = false;
  filteredOptions: any[] = [];
  highlightedIndex: number = -1;

  ngOnChanges(): void {
    this.filterOptions();
    // Se o dropdown estiver aberto, atualiza as opções filtradas
    if (this.showDropdown) {
      this.filterOptions();
    }
  }

  onInputChange(value: string): void {
    this.valueChange.emit(value);
    this.filterOptions();
    // Mantém o dropdown aberto se houver opções disponíveis
    this.showDropdown = this.filteredOptions.length > 0;
    this.highlightedIndex = -1;
  }

  onFocus(): void {
    // Mostra o dropdown quando o campo recebe foco, se houver opções disponíveis
    if (this.options && this.options.length > 0) {
      this.filterOptions(); // Atualiza as opções filtradas
      this.showDropdown = true;
    }
  }

  onBlur(): void {
    // Delay para permitir clique nas opções
    setTimeout(() => {
      this.showDropdown = false;
      this.highlightedIndex = -1;
    }, 200);
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      event.preventDefault();
      if (this.highlightedIndex >= 0 && this.filteredOptions[this.highlightedIndex]) {
        this.selectOption(this.filteredOptions[this.highlightedIndex]);
      } else {
        this.enterPressed.emit(this.value);
      }
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (this.showDropdown && this.filteredOptions.length > 0) {
        this.highlightedIndex = Math.min(this.highlightedIndex + 1, this.filteredOptions.length - 1);
        this.scrollToHighlighted();
      }
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (this.showDropdown && this.filteredOptions.length > 0) {
        this.highlightedIndex = Math.max(this.highlightedIndex - 1, -1);
        this.scrollToHighlighted();
      }
    } else if (event.key === 'Escape') {
      this.showDropdown = false;
      this.highlightedIndex = -1;
    }
  }

  filterOptions(): void {
    if (!this.options || this.options.length === 0) {
      this.filteredOptions = [];
      return;
    }

    // Se não houver valor digitado, mostra TODAS as opções (sem limite)
    if (!this.value || !this.value.trim()) {
      this.filteredOptions = this.options;
      return;
    }

    // Filtra as opções baseado no texto digitado (aqui aplica o limite)
    const filterLower = this.value.toLowerCase().trim();
    const filtered = this.options.filter(option => {
      const displayText = this.getDisplayText(option).toLowerCase();
      return displayText.includes(filterLower);
    });

    // Aplica limite apenas quando há filtro de texto
    this.filteredOptions = filtered.slice(0, this.maxOptions);
  }

  selectOption(option: any): void {
    const displayText = this.getDisplayText(option);
    this.valueChange.emit(displayText);
    this.optionSelected.emit(option);
    this.showDropdown = false;
    this.highlightedIndex = -1;
  }

  getDisplayText(option: any): string {
    if (this.displayFn) {
      return this.displayFn(option);
    }
    if (this.trackBy && option && typeof option === 'object') {
      return String(option[this.trackBy]);
    }
    return String(option);
  }

  getOptionValue(option: any): any {
    if (this.trackBy && option && typeof option === 'object') {
      return option[this.trackBy];
    }
    return option;
  }

  private scrollToHighlighted(): void {
    // Scroll será implementado via CSS se necessário
  }

  onClear(): void {
    this.valueChange.emit('');
    this.showDropdown = false;
    this.filteredOptions = [];
    this.highlightedIndex = -1;
  }
}
