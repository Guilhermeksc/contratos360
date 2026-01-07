import { Component, Input, ContentChild, TemplateRef } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-standard-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './standard-table.component.html',
  styleUrl: './standard-table.component.scss'
})
export class StandardTableComponent {
  @Input() isDarkTheme: boolean = false; // Tema claro (branco) por padrão
  @Input() showBorder: boolean = true; // Mostra borda ao redor da tabela
}

