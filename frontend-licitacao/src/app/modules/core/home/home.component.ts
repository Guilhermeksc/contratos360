import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  constructor(private dialog: MatDialog) {}

  openInfo(): void {
    // Abrir dialog de informações
    console.log('Abrir informações');
  }

  openBackup(): void {
    // Abrir dialog/página de backup
    console.log('Abrir backup');
  }

  openHelp(): void {
    // Abrir dialog de ajuda
    console.log('Abrir ajuda');
  }
}

