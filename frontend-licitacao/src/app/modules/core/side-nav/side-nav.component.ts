import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../../services/auth.service';

interface NavItem {
  icon?: string;
  imagePath?: string;
  label: string;
  route: string;
  tooltip: string;
}

interface ModuleNavConfig {
  [key: string]: NavItem[];
}

@Component({
  selector: 'app-side-nav',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatButtonModule],
  templateUrl: './side-nav.component.html',
  styleUrl: './side-nav.component.scss'
})
export class SideNavComponent implements OnInit {
  activeRoute = signal<string>('');

  // Home sempre visível
  homeNavItem: NavItem = { imagePath: 'assets/img/svg/licitacao360.svg', label: 'Home', route: '/home', tooltip: 'Home' };

  // Configuração de navegação para cada módulo
  moduleNavConfig: ModuleNavConfig = {
    // Opções específicas para Contratos
    contratos: [
      { icon: 'description', label: 'Contratos', route: '/contratos', tooltip: 'Contratos' },
      { icon: 'table_chart', label: 'Lista', route: '/contratos/lista', tooltip: 'Visualizar Tabelas' },
      { icon: 'message', label: 'Mensagens', route: '/contratos/mensagens', tooltip: 'Mensagens' },
      { icon: 'settings', label: 'Configurações', route: '/contratos/configuracoes', tooltip: 'Configurações' }
    ],
    // Opções específicas para Planejamento
    planejamento: [
      { icon: 'calendar_today', label: 'Cronograma', route: '/planejamento/cronograma', tooltip: 'Cronograma' },
      { icon: 'assessment', label: 'Relatórios', route: '/planejamento/relatorios', tooltip: 'Relatórios' },
      { icon: 'analytics', label: 'Análises', route: '/planejamento/analises', tooltip: 'Análises' }
    ],
    // Opções específicas para GerAta
    gerata: [
      { icon: 'add', label: 'Nova Ata', route: '/gerata/nova', tooltip: 'Criar Nova Ata' },
      { icon: 'list', label: 'Listar Atas', route: '/gerata/lista', tooltip: 'Listar Atas' },
      { icon: 'history', label: 'Histórico', route: '/gerata/historico', tooltip: 'Histórico de Atas' }
    ],
    // Opções específicas para Empresas Sancionadas
    'empresas-sancionadas': [
      { icon: 'search', label: 'Buscar Empresa', route: '/empresas-sancionadas/buscar', tooltip: 'Buscar Empresa' },
      { icon: 'list', label: 'Lista de Empresas', route: '/empresas-sancionadas/lista', tooltip: 'Lista de Empresas' },
      { icon: 'warning', label: 'Alertas', route: '/empresas-sancionadas/alertas', tooltip: 'Alertas' }
    ],
    // Opções específicas para Processo Sancionatório
    'processo-sancionatorio': [
      { icon: 'gavel', label: 'Processos', route: '/processo-sancionatorio/processos', tooltip: 'Processos Sancionatórios' },
      { icon: 'timeline', label: 'Acompanhamento', route: '/processo-sancionatorio/acompanhamento', tooltip: 'Acompanhamento' },
      { icon: 'description', label: 'Documentos', route: '/processo-sancionatorio/documentos', tooltip: 'Documentos' }
    ],
    // Opções específicas para Controle Interno
    'controle-interno': [
      { icon: 'verified', label: 'Auditorias', route: '/controle-interno/auditorias', tooltip: 'Auditorias' },
      { icon: 'check_circle', label: 'Conformidade', route: '/controle-interno/conformidade', tooltip: 'Conformidade' },
      { icon: 'report', label: 'Relatórios', route: '/controle-interno/relatorios', tooltip: 'Relatórios' }
    ]
  };

  // Computa os itens de navegação baseado na rota atual
  navItems = computed<NavItem[]>(() => {
    const route = this.activeRoute();
    
    // Home sempre visível
    const items: NavItem[] = [this.homeNavItem];
    
    // Se está na página inicial, mostra apenas Home
    if (route === '/home') {
      return items;
    }

    // Detecta o módulo atual
    const module = this.getCurrentModule(route);
    
    // Adiciona opções específicas do módulo se existirem
    if (module && this.moduleNavConfig[module]) {
      items.push(...this.moduleNavConfig[module]);
    }

    return items;
  });

  // Computa o índice onde começa a navegação específica do módulo
  moduleNavStartIndex = computed<number>(() => {
    const route = this.activeRoute();
    if (route === '/home') {
      return -1; // Não há navegação específica
    }
    
    const module = this.getCurrentModule(route);
    
    
    // Para outros módulos, começa após Home
    return 1;
  });

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.router.events.subscribe(() => {
      this.activeRoute.set(this.router.url.split('?')[0]);
    });
    this.activeRoute.set(this.router.url.split('?')[0]);
  }

  /**
   * Detecta o módulo atual baseado na rota
   */
  private getCurrentModule(route: string): string | null {
    if (route.startsWith('/contratos')) {
      return 'contratos';
    }
    if (route.startsWith('/planejamento')) {
      return 'planejamento';
    }
    if (route.startsWith('/gerata')) {
      return 'gerata';
    }
    if (route.startsWith('/empresas-sancionadas')) {
      return 'empresas-sancionadas';
    }
    if (route.startsWith('/processo-sancionatorio')) {
      return 'processo-sancionatorio';
    }
    if (route.startsWith('/controle-interno')) {
      return 'controle-interno';
    }
    return null;
  }

  navigate(route: string): void {
    this.router.navigate([route]);
  }

  isActive(route: string): boolean {
    const currentRoute = this.activeRoute();
    
    if (route === '/home') {
      return currentRoute === '/home';
    }
    
    // Para rotas específicas, verifica se a rota atual começa com a rota do item
    if (currentRoute.startsWith(route)) {
      // Se é exatamente a rota ou se é uma sub-rota
      return currentRoute === route || currentRoute.startsWith(route + '/');
    }
    
    return false;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}

