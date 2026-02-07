import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

interface NavigationCard {
  title: string;
  icon: string;
  route: string;
  description: string;
  color?: string;
}

@Component({
  selector: 'app-controle-interno',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatButtonModule],
  templateUrl: './controle-interno.component.html',
  styleUrl: './controle-interno.component.scss'
})
export class ControleInternoComponent {
  navigationCards: NavigationCard[] = [
    {
      title: 'PNCP',
      icon: 'public',
      route: '/controle-interno/pncp',
      description: 'Portal Nacional de Contratações Públicas - Acesse dados de compras públicas',
      color: '#1976d2'
    },
    {
      title: 'Atas',
      icon: 'description',
      route: '/controle-interno/ata',
      description: 'Gestão de Atas de Registro de Preços',
      color: '#388e3c'
    },
    {
      title: 'Contratos',
      icon: 'assignment',
      route: '/controle-interno/contratos',
      description: 'Controle e gestão de contratos',
      color: '#f57c00'
    },
    {
      title: 'Dashboard',
      icon: 'dashboard',
      route: '/controle-interno/dashboard',
      description: 'Painel de indicadores e métricas',
      color: '#7b1fa2'
    }
  ];

  constructor(private router: Router) {}

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }
}

