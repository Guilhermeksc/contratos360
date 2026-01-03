import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FeatureCardComponent } from '../../components/feature-card/feature-card.component';

interface FeatureCard {
  title: string;
  iconPath: string;
  route: string;
}

@Component({
  selector: 'app-home-landing',
  standalone: true,
  imports: [CommonModule, FeatureCardComponent],
  templateUrl: './home-landing.component.html',
  styleUrl: './home-landing.component.scss'
})
export class HomeLandingComponent {
  features: FeatureCard[] = [
    {
      title: 'Planejamento',
      iconPath: '/assets/img/svg/plan.svg',
      route: '/planejamento'
    },
    {
      title: 'Dispensa Eletrônica',
      iconPath: '/assets/img/svg/dispensa.svg',
      route: '/dispensa-eletronica'
    },    
    {
      title: 'Controle de Contratos',
      iconPath: '/assets/img/svg/contratos.svg',
      route: '/contratos'
    },
    {
      title: 'GerAta',
      iconPath: '/assets/img/svg/ata.svg',
      route: '/gerata'
    },
    {
      title: 'Jurisprudência',
      iconPath: '/assets/img/svg/juris.svg',
      route: '/jurisprudencia'
    },    
    {
      title: 'Nota Técnica',
      iconPath: '/assets/img/svg/nt.svg',
      route: '/nota-tecnica'
    },    
    {
      title: 'Empresas Sancionadas',
      iconPath: '/assets/img/svg/empresas.svg',
      route: '/empresas-sancionadas'
    },
    {
      title: 'Processo Sancionatório',
      iconPath: '/assets/img/svg/sansao.svg',
      route: '/processo-sancionatorio'
    },
    {
      title: 'Agentes Responsáveis',
      iconPath: '/assets/img/svg/agentes.svg',
      route: '/agentes-responsaveis'
    },      
    {
      title: 'Diário Oficial da União',
      iconPath: '/assets/img/svg/dou.svg',
      route: '/diario-oficial'
    },    
    {
      title: 'Conselho de Gestão',
      iconPath: '/assets/img/svg/conges.svg',
      route: '/conselho-de-gestao'
    },
    {
      title: 'Controle Interno',
      iconPath: '/assets/img/svg/controle.svg',
      route: '/controle-interno'
    }
  ];

  constructor(private router: Router) {}
}

