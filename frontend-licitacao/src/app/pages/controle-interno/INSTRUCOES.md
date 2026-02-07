# Módulo Controle Interno - Instruções de Implementação

Este documento descreve como implementar o módulo **Controle Interno** no frontend Angular.

## 📋 Visão Geral

O módulo Controle Interno é uma área centralizada que fornece acesso rápido a diferentes funcionalidades do sistema através de cards de navegação.

## 🎯 Estrutura de Navegação

O módulo deve ter **4 links principais**:

1. **PNCP** - Portal Nacional de Contratações Públicas
2. **Atas** - Gestão de Atas de Registro de Preços
3. **Contratos** - Controle de Contratos
4. **Dashboard** - Painel de indicadores e métricas

## 📁 Arquivos Envolvidos

### 1. Side Navigation (`side-nav.component.ts`)

**Localização:** `frontend-licitacao/src/app/modules/core/side-nav/side-nav.component.ts`

**Alteração necessária:** Atualizar a configuração de navegação do módulo `controle-interno`:

```typescript
// Opções específicas para Controle Interno
'controle-interno': [
  { icon: 'public', label: 'PNCP', route: '/controle-interno/pncp', tooltip: 'Portal Nacional de Contratações Públicas' },
  { icon: 'description', label: 'Atas', route: '/controle-interno/atas', tooltip: 'Gestão de Atas' },
  { icon: 'assignment', label: 'Contratos', route: '/controle-interno/contratos', tooltip: 'Controle de Contratos' },
  { icon: 'dashboard', label: 'Dashboard', route: '/controle-interno/dashboard', tooltip: 'Dashboard de Indicadores' }
]
```

### 2. Componente Principal (`controle-interno.component.*`)

**Localização:** `frontend-licitacao/src/app/pages/controle-interno/`

#### 2.1 TypeScript (`controle-interno.component.ts`)

```typescript
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
      route: '/controle-interno/atas',
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
```

#### 2.2 Template HTML (`controle-interno.component.html`)

```html
<div class="controle-interno-container">
  <div class="header">
    <h1>Controle Interno</h1>
    <p class="subtitle">Acesso centralizado às funcionalidades do sistema</p>
  </div>

  <div class="cards-grid">
    <mat-card 
      *ngFor="let card of navigationCards" 
      class="navigation-card"
      [style.border-top-color]="card.color"
      (click)="navigateTo(card.route)">
      <mat-card-content>
        <div class="card-icon" [style.color]="card.color">
          <mat-icon>{{ card.icon }}</mat-icon>
        </div>
        <h2 class="card-title">{{ card.title }}</h2>
        <p class="card-description">{{ card.description }}</p>
      </mat-card-content>
      <mat-card-actions>
        <button mat-button [style.color]="card.color">
          Acessar
          <mat-icon>arrow_forward</mat-icon>
        </button>
      </mat-card-actions>
    </mat-card>
  </div>
</div>
```

#### 2.3 Estilos SCSS (`controle-interno.component.scss`)

```scss
@use '../../styles/variables' as *;

.controle-interno-container {
  padding: $spacing-xxl;
  min-height: 100vh;
  background: var(--background-color, #f5f5f5);
  
  .header {
    margin-bottom: $spacing-xxl;
    text-align: center;
    
    h1 {
      color: $text-primary;
      margin-bottom: $spacing-md;
      font-size: 2.5rem;
      font-weight: 600;
    }
    
    .subtitle {
      color: $text-secondary;
      font-size: 1.1rem;
    }
  }
  
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: $spacing-xl;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .navigation-card {
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-top: 4px solid;
    border-radius: 8px;
    height: 100%;
    display: flex;
    flex-direction: column;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    
    mat-card-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: $spacing-xl;
      
      .card-icon {
        margin-bottom: $spacing-lg;
        
        mat-icon {
          font-size: 64px;
          width: 64px;
          height: 64px;
        }
      }
      
      .card-title {
        color: $text-primary;
        margin-bottom: $spacing-md;
        font-size: 1.5rem;
        font-weight: 600;
      }
      
      .card-description {
        color: $text-secondary;
        font-size: 0.95rem;
        line-height: 1.5;
      }
    }
    
    mat-card-actions {
      padding: $spacing-md $spacing-lg;
      display: flex;
      justify-content: center;
      
      button {
        font-weight: 500;
        
        mat-icon {
          margin-left: $spacing-xs;
        }
      }
    }
  }
}

// Responsividade
@media (max-width: 768px) {
  .controle-interno-container {
    padding: $spacing-lg;
    
    .cards-grid {
      grid-template-columns: 1fr;
    }
  }
}
```

### 3. Rotas (`app.routes.ts`)

**Localização:** `frontend-licitacao/src/app/app.routes.ts`

**Adicionar rotas filhas para o módulo Controle Interno:**

```typescript
{
  path: 'controle-interno',
  loadComponent: () => import('./pages/controle-interno/controle-interno.component').then((m) => m.ControleInternoComponent),
  data: { breadcrumb: 'Controle Interno' },
  children: [
    {
      path: 'pncp',
      loadComponent: () => import('./pages/controle-interno/pncp/pncp.component').then((m) => m.PncpComponent),
      data: { breadcrumb: 'PNCP' }
    },
    {
      path: 'atas',
      loadComponent: () => import('./pages/controle-interno/atas/atas.component').then((m) => m.AtasComponent),
      data: { breadcrumb: 'Atas' }
    },
    {
      path: 'contratos',
      loadComponent: () => import('./pages/controle-interno/contratos/contratos.component').then((m) => m.ContratosComponent),
      data: { breadcrumb: 'Contratos' }
    },
    {
      path: 'dashboard',
      loadComponent: () => import('./pages/controle-interno/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      data: { breadcrumb: 'Dashboard' }
    }
  ]
}
```

**Nota:** Se preferir manter a estrutura atual sem rotas filhas, os links podem apontar diretamente para rotas existentes:
- `/controle-interno/pncp` → Componente PNCP
- `/gerata` → Componente de Atas (já existe)
- `/contratos` → Componente de Contratos (já existe)
- `/controle-interno/dashboard` → Componente Dashboard

## 🎨 Ícones Material Design

Os ícones utilizados são do Material Icons:
- `public` - PNCP (globo/mundo)
- `description` - Atas (documento)
- `assignment` - Contratos (atribuição/contrato)
- `dashboard` - Dashboard (painel)

## 🔗 Integração com Backend

### Endpoints PNCP

O módulo PNCP deve consumir os seguintes endpoints:

- `GET /api/pncp/compras/por-unidade/{codigo_unidade}/` - Listar compras
- `GET /api/pncp/compras/modalidades-agregadas/{codigo_unidade}/` - Estatísticas por modalidade
- `GET /api/pncp/compras/itens-resultado-merge/{codigo_unidade}/` - Itens com resultados
- `GET /api/pncp/compras/fornecedores-agregados/{codigo_unidade}/` - Fornecedores agregados
- `GET /api/pncp/compras/export-xlsx/{codigo_unidade}/` - Exportar XLSX

**Documentação completa:** Ver `backend/django_licitacao360/apps/pncp/ENDPOINTS.md`

## 📝 Checklist de Implementação

### Fase 1: Estrutura Base
- [ ] Atualizar `side-nav.component.ts` com os 4 links
- [ ] Criar componente `controle-interno.component.ts` com cards de navegação
- [ ] Criar template HTML com grid de cards
- [ ] Adicionar estilos SCSS responsivos
- [ ] Testar navegação entre cards

### Fase 2: Componentes Filhos
- [ ] Criar componente PNCP (`pncp.component.*`)
- [ ] Criar componente Dashboard (`dashboard.component.*`)
- [ ] Integrar componente Atas existente (`/gerata`)
- [ ] Integrar componente Contratos existente (`/contratos`)

### Fase 3: Integração Backend
- [ ] Criar serviço PNCP (`pncp.service.ts`)
- [ ] Implementar chamadas aos endpoints
- [ ] Criar interfaces TypeScript para os dados
- [ ] Implementar tratamento de erros

### Fase 4: Funcionalidades
- [ ] Implementar busca/filtro por código de unidade (PNCP)
- [ ] Implementar visualização de dados em tabelas
- [ ] Implementar exportação XLSX
- [ ] Implementar gráficos no Dashboard

## 🚀 Exemplo de Uso

### Navegação

1. Usuário acessa `/controle-interno`
2. Vê 4 cards: PNCP, Atas, Contratos, Dashboard
3. Clica em um card para navegar para a funcionalidade específica
4. Side navigation mostra os links do módulo ativo

### Side Navigation

Quando o usuário está em qualquer rota `/controle-interno/*`, o side navigation mostra:
- Home (sempre visível)
- PNCP
- Atas
- Contratos
- Dashboard

## 🔍 Estrutura de Diretórios Recomendada

```
frontend-licitacao/src/app/pages/controle-interno/
├── controle-interno.component.ts
├── controle-interno.component.html
├── controle-interno.component.scss
├── INSTRUCOES.md (este arquivo)
├── pncp/
│   ├── pncp.component.ts
│   ├── pncp.component.html
│   └── pncp.component.scss
├── dashboard/
│   ├── dashboard.component.ts
│   ├── dashboard.component.html
│   └── dashboard.component.scss
└── services/
    └── pncp.service.ts
```

## 📚 Referências

- **Material Design Icons:** https://fonts.google.com/icons
- **Angular Router:** https://angular.io/guide/router
- **Material Card:** https://material.angular.io/components/card
- **Backend PNCP Endpoints:** `backend/django_licitacao360/apps/pncp/ENDPOINTS.md`

## ⚠️ Notas Importantes

1. **Rotas Existentes:** Os componentes de Atas (`/gerata`) e Contratos (`/contratos`) já existem. Os links podem apontar diretamente para eles ou criar versões específicas do Controle Interno.

2. **Permissões:** Verificar se há necessidade de controle de acesso específico para o módulo Controle Interno.

3. **Responsividade:** O grid de cards deve ser responsivo, adaptando-se a diferentes tamanhos de tela.

4. **Tema:** Os estilos devem respeitar o tema claro/escuro do sistema.

5. **Acessibilidade:** Adicionar atributos ARIA e suporte a navegação por teclado.
