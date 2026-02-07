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
            loadComponent: () => import('./pages/contratos/contratos.component').then((m) => m.ContratosComponent),
            data: { breadcrumb: 'Contratos' }
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
        children: [
          {
            path: '',
            loadComponent: () => import('./pages/controle-interno/controle-interno.component').then((m) => m.ControleInternoComponent),
            data: { breadcrumb: 'Controle Interno' }
          },
          {
            path: 'pncp',
            loadComponent: () => import('./pages/controle-interno/ccimar-pncp/ccimar-pncp').then((m) => m.CcimarPncp),
            data: { breadcrumb: 'PNCP' }
          },
          {
            path: 'ata',
            loadComponent: () => import('./pages/controle-interno/ccimar-ata/ccimar-ata').then((m) => m.CcimarAta),
            data: { breadcrumb: 'Atas' }
          },
          {
            path: 'contratos',
            loadComponent: () => import('./pages/controle-interno/ccimar-contratos/ccimar-contratos').then((m) => m.CcimarContratos),
            data: { breadcrumb: 'Contratos' }
          },
          {
            path: 'dashboard',
            loadComponent: () => import('./pages/controle-interno/ccimar-dash/ccimar-dash').then((m) => m.CcimarDash),
            data: { breadcrumb: 'Dashboard' }
          }
        ]
      },
      {
        path: 'diario-oficial',
        loadComponent: () => import('./pages/diario-oficial/diario-oficial').then((m) => m.DiarioOficialComponent),
        data: { breadcrumb: 'Diário Oficial' }
      },
      {
        path: 'calendario',
        loadComponent: () => import('./pages/calendario/calendario').then((m) => m.CalendarioComponent),
        data: { breadcrumb: 'Calendário' }
      },
    ]
  },
  { path: '**', redirectTo: '/home' }
];
