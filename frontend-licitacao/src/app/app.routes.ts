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
    path: '',
    loadComponent: () => import('./modules/core/shell-layout/shell-layout.component').then((m) => m.ShellLayoutComponent),
    canActivate: [authGuard],
    children: [
      {
        path: '',
        loadComponent: () => import('./modules/core/home/home.component').then((m) => m.HomeComponent),
        data: { breadcrumb: 'Home' }
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
      // Rotas antigas removidas - módulos não existem mais
    ]
  },
  { path: '**', redirectTo: '' }
];
