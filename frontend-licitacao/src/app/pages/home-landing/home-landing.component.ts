import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { FeatureCardComponent } from '../../components/feature-card/feature-card.component';
import { AuthService, User } from '../../services/auth.service';
import { Observable } from 'rxjs';

interface FeatureCard {
  title: string;
  iconPath: string;
  route: string;
}

@Component({
  selector: 'app-home-landing',
  standalone: true,
  imports: [CommonModule, FeatureCardComponent, MatButtonModule, MatIconModule],
  templateUrl: './home-landing.component.html',
  styleUrl: './home-landing.component.scss'
})
export class HomeLandingComponent implements OnInit {
  currentUser$: Observable<User | null>;
  
  features: FeatureCard[] = [
    {
      title: 'Consultar Contratações',
      iconPath: '/assets/img/svg/find.svg',
      route: '/planejamento'
    },
    // {
    //   title: 'Dispensa Eletrônica',
    //   iconPath: '/assets/img/svg/dispensa.svg',
    //   route: '/dispensa-eletronica'
    // },    
    {
      title: 'Controle de Contratos',
      iconPath: '/assets/img/svg/contratos.svg',
      route: '/contratos'
    },
    {
      title: 'Controle de Atas',
      iconPath: '/assets/img/svg/sign.svg',
      route: '/controle-atas'
    },    
    // {
    //   title: 'GerAta',
    //   iconPath: '/assets/img/svg/ata.svg',
    //   route: '/gerata'
    // },
    // {
    //   title: 'Calendário',
    //   iconPath: '/assets/img/svg/calendar.svg',
    //   route: '/calendario'
    // },    
    // {
    //   title: 'Nota Técnica',
    //   iconPath: '/assets/img/svg/juris.svg',
    //   route: '/nota-tecnica'
    // },    
    {
      title: 'Empresas Sancionadas',
      iconPath: '/assets/img/svg/empresas.svg',
      route: '/empresas-sancionadas'
    },
    // {
    //   title: 'Processo Sancionatório',
    //   iconPath: '/assets/img/svg/sansao.svg',
    //   route: '/processo-sancionatorio'
    // },
    // {
    //   title: 'Agentes Responsáveis',
    //   iconPath: '/assets/img/svg/agentes.svg',
    //   route: '/agentes-responsaveis'
    // },      
    {
      title: 'Diário Oficial da União',
      iconPath: '/assets/img/svg/dou.svg',
      route: '/diario-oficial'
    },    
    // {
    //   title: 'Conselho de Gestão',
    //   iconPath: '/assets/img/svg/conges.svg',
    //   route: '/conselho-de-gestao'
    // },
    {
      title: 'Controle Interno',
      iconPath: '/assets/img/svg/controle.svg',
      route: '/controle-interno'
    }
  ];

  constructor(
    private readonly router: Router,
    private readonly authService: AuthService
  ) {
    this.currentUser$ = this.authService.currentUser$;
  }

  ngOnInit(): void {}

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getUasgCentralizadora(user: User): string | null {
    if (user.uasg_centralizadora) {
      return `UASG Centralizadora: ${user.uasg_centralizadora.sigla} (${user.uasg_centralizadora.codigo})`;
    }
    return null;
  }

  getUasgCentralizada(user: User): string | null {
    if (user.uasg_centralizada) {
      return `UASG Centralizada: ${user.uasg_centralizada.sigla} (${user.uasg_centralizada.codigo})`;
    }
    return null;
  }

  isControleInterno(user: User): boolean {
    return !!user.controle_interno;
  }
}

