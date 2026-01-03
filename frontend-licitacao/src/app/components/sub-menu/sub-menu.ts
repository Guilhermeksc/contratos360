import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

export interface SubMenuItem {
  id: string;
  title: string;
  description?: string;
  isActive?: boolean;
}

@Component({
  selector: 'app-sub-menu',
  imports: [
    CommonModule,
    MatListModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './sub-menu.html',
  styleUrl: './sub-menu.scss'
})
export class SubMenu implements OnInit {
  @Input() title: string = '';
  @Input() secondtitle: string = '';
  @Input() subtitle: string = '';
  @Input() items: SubMenuItem[] = [];
  @Input() selectedItemId: string = '';
  @Input() showBackButton: boolean = false;
  @Input() backButtonLabel: string = 'Voltar à Bibliografia';
  @Input() isCollapsed: boolean = false;
  
  @Output() itemSelected = new EventEmitter<SubMenuItem>();
  @Output() backButtonClicked = new EventEmitter<void>();
  @Output() collapsedChanged = new EventEmitter<boolean>();

  ngOnInit() {
    // Se nenhum item está selecionado e há itens disponíveis, seleciona o primeiro
    if (!this.selectedItemId && this.items.length > 0) {
      this.selectItem(this.items[0]);
    }
  }

  selectItem(item: SubMenuItem) {
    // Remove seleção de todos os itens
    this.items.forEach(i => i.isActive = false);
    
    // Marca o item atual como ativo
    item.isActive = true;
    this.selectedItemId = item.id;
    
    // Emite o evento
    this.itemSelected.emit(item);
  }

  onBackButtonClick() {
    this.backButtonClicked.emit();
  }

  isSelected(item: SubMenuItem): boolean {
    return item.id === this.selectedItemId || item.isActive === true;
  }

  toggleCollapse() {
    this.isCollapsed = !this.isCollapsed;
    this.collapsedChanged.emit(this.isCollapsed);
  }
}
