import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { loginGuard } from './guards/login.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then((m) => m.LoginComponent),
    canActivate: [loginGuard]
  },
  {
    path: 'home',
    loadComponent: () => import('./pages/home-landing/home-landing.component').then((m) => m.HomeLandingComponent),
    canActivate: [authGuard],
    data: { breadcrumb: 'Home' }
  },
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: '',
    loadComponent: () => import('./modules/core/shell-layout/shell-layout.component').then((m) => m.ShellLayoutComponent),
    canActivate: [authGuard],
    children: [
      {
        path: 'planejamento',
        loadComponent: () => import('./pages/planejamento/planejamento.component').then((m) => m.PlanejamentoComponent),
        data: { breadcrumb: 'Planejamento' }
      },
      {
        path: 'contratos',
        children: [
          {
            path: '',
            loadComponent: () => import('./modules/features/contratos/pages/uasg-search/uasg-search.component').then((m) => m.UasgSearchComponent),
            data: { breadcrumb: 'Buscar UASG' }
          },
          {
            path: 'lista',
            loadComponent: () => import('./modules/features/contratos/pages/contracts-table/contracts-table.component').then((m) => m.ContractsTableComponent),
            data: { breadcrumb: 'Visualizar Tabelas' }
          },
          {
            path: ':id',
            loadComponent: () => import('./modules/features/contratos/pages/contract-details/contract-details.component').then((m) => m.ContractDetailsComponent),
            data: { breadcrumb: 'Detalhes do Contrato' }
          },
          {
            path: 'mensagens',
            loadComponent: () => import('./modules/features/contratos/pages/message-builder/message-builder.component').then((m) => m.MessageBuilderComponent),
            data: { breadcrumb: 'Mensagens' }
          },
          {
            path: 'configuracoes',
            loadComponent: () => import('./modules/features/contratos/pages/settings/settings.component').then((m) => m.SettingsComponent),
            data: { breadcrumb: 'Configurações' }
          }
        ]
      },
      {
        path: 'gerata',
        loadComponent: () => import('./pages/gerata/gerata.component').then((m) => m.GerataComponent),
        data: { breadcrumb: 'GerAta' }
      },
      {
        path: 'empresas-sancionadas',
        loadComponent: () => import('./pages/empresas-sancionadas/empresas-sancionadas.component').then((m) => m.EmpresasSancionadasComponent),
        data: { breadcrumb: 'Empresas Sancionadas' }
      },
      {
        path: 'processo-sancionatorio',
        loadComponent: () => import('./pages/processo-sancionatorio/processo-sancionatorio.component').then((m) => m.ProcessoSancionatorioComponent),
        data: { breadcrumb: 'Processo Sancionatório' }
      },
      {
        path: 'controle-interno',
        loadComponent: () => import('./pages/controle-interno/controle-interno.component').then((m) => m.ControleInternoComponent),
        data: { breadcrumb: 'Controle Interno' }
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./modules/features/contratos/pages/dashboard/dashboard.component').then((m) => m.DashboardComponent),
        data: { breadcrumb: 'Dashboard' }
      },
      {
        path: 'atas',
        // Placeholder para módulo de atas
        loadComponent: () => import('./modules/core/home/home.component').then((m) => m.HomeComponent),
        data: { breadcrumb: 'Atas' }
      }
    ]
  },
  { path: '**', redirectTo: '/home' }
];
