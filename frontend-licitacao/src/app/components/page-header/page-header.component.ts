import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-page-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './page-header.component.html',
  styleUrl: './page-header.component.scss'
})
export class PageHeaderComponent {
  @Input() title: string = '';
  @Input() iconPath: string = ''; // Caminho para o ícone SVG
  @Input() showThemeToggle: boolean = true;
  @Input() isDarkTheme: boolean = false;
  
  @Output() themeToggle = new EventEmitter<boolean>();

  onThemeToggle(): void {
    this.isDarkTheme = !this.isDarkTheme;
    this.themeToggle.emit(this.isDarkTheme);
  }
}

