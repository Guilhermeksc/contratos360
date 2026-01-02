# Layout Responsivo - Sistema de Navegação

## 📱 Visão Geral

O sistema de navegação foi completamente redesenhado para oferecer uma experiência otimizada em diferentes dispositivos:

- **Smartphone (< 768px)**: Menu lateral que desliza sobre o conteúdo
- **Tablet (768px - 1023px)**: Menu no topo que expande/colapsa verticalmente
- **Desktop (≥ 1024px)**: Menu lateral fixo sempre visível

---

## 🎨 Breakpoints

```scss
// Mobile
@media (max-width: 767px)

// Tablet
@media (min-width: 768px) and (max-width: 1023px)

// Desktop
@media (min-width: 1024px)
```

---

## 🏗️ Arquitetura

### 1. **Home Component** (`home.component.ts`)

O componente principal gerencia três tipos de dispositivos:

```typescript
type DeviceType = 'mobile' | 'tablet' | 'desktop';
```

#### Signals e Computed Values:

- `deviceType`: Signal que rastreia o tipo de dispositivo atual
- `isTopMenuExpanded`: Controla se o menu do tablet está expandido
- `drawerMode`: Calcula se o sidenav deve estar em modo 'over' ou 'side'
- `showSideMenu`: Determina quando mostrar o menu lateral (mobile/desktop)
- `showTopMenu`: Determina quando mostrar o menu superior (tablet)

#### Métodos Principais:

- `toggleDrawer()`: Alterna menu lateral no mobile
- `toggleTopMenu()`: Alterna menu superior no tablet
- `closeDrawerIfMobile()`: Fecha menu após seleção no mobile
- `closeTopMenu()`: Fecha menu após seleção no tablet

---

### 2. **Layout Tablet** (Menu no Topo)

#### Estrutura HTML:

```html
<div class="tablet-layout">
  <!-- Header fixo com botão toggle -->
  <header class="top-header">
    <button (click)="toggleTopMenu()">
      <mat-icon>menu/close</mat-icon>
    </button>
    <div class="top-header-title">CEMOS 2028</div>
  </header>

  <!-- Overlay escurecido (quando menu expandido) -->
  <div class="menu-overlay" (click)="closeTopMenu()"></div>

  <!-- Menu expansível -->
  <div class="top-menu-container" [@topMenuCollapse]>
    <app-side-menu [isTopMenuMode]="true"></app-side-menu>
  </div>

  <!-- Conteúdo principal -->
  <main class="tablet-content">
    <router-outlet></router-outlet>
  </main>
</div>
```

#### Características:

- **Header Fixo**: 64px de altura, background preto gradiente
- **Menu Expansível**: Animação suave de expansão/colapso
- **Overlay**: Fundo escurecido com blur quando menu está aberto
- **Auto-fechamento**: Clique no overlay ou seleção de item fecha o menu

---

### 3. **Layout Mobile/Desktop** (Menu Lateral)

#### Estrutura HTML:

```html
<mat-sidenav-container>
  <mat-sidenav #drawer [mode]="drawerMode()">
    <app-side-menu [isTopMenuMode]="false"></app-side-menu>
  </mat-sidenav>

  <mat-sidenav-content>
    <!-- Botão hamburguer (mobile) -->
    <button *ngIf="deviceType() === 'mobile'">
      <mat-icon>menu</mat-icon>
    </button>
    
    <router-outlet></router-outlet>
  </mat-sidenav-content>
</mat-sidenav-container>
```

#### Mobile:
- Sidenav em modo `over` (sobrepõe o conteúdo)
- Largura: 85vw (máx: 320px, mín: 260px)
- Botão hamburguer fixo no canto superior esquerdo
- Fecha automaticamente ao selecionar item

#### Desktop:
- Sidenav em modo `side` (sempre visível)
- Largura fixa: 280px
- Sem botão hamburguer
- Conteúdo com padding: 32px

---

### 4. **Side Menu Component**

#### Input Property:

```typescript
@Input() isTopMenuMode: boolean = false;
```

Permite que o componente se adapte ao modo tablet:
- **`false`**: Modo lateral (mobile/desktop) - mostra header CEMOS
- **`true`**: Modo topo (tablet) - esconde header (evita duplicação)

#### Estilo Condicional:

```html
<div class="header-container" [class.tablet-mode]="isTopMenuMode">
  <span class="header-title">CEMOS</span>
  <span class="header-subtitle">2028</span>
</div>
```

---

## 🎭 Animações

### Top Menu Collapse:

```typescript
trigger('topMenuCollapse', [
  state('collapsed', style({
    height: '0px',
    opacity: 0,
    overflow: 'hidden'
  })),
  state('expanded', style({
    height: '*',
    opacity: 1,
    overflow: 'visible'
  })),
  transition('collapsed <=> expanded', [
    animate('300ms ease-in-out')
  ])
])
```

---

## 🎨 Estilos Principais

### Variáveis CSS:

```scss
:root {
  --header-height: 64px;
  --sidebar-width: 280px;
  --mobile-header-height: 56px;
}
```

### Menu Overlay (Tablet):

```scss
.menu-overlay {
  position: fixed;
  top: var(--header-height);
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  z-index: 998;
}
```

### Botão Mobile:

```scss
.mobile-menu-button {
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 1000;
  background: #000000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
```

---

## 📱 Experiência do Usuário

### Mobile (Smartphone):
1. Botão hamburguer sempre visível no canto superior esquerdo
2. Toque no botão → Menu desliza da esquerda
3. Toque em item → Menu fecha automaticamente
4. Toque fora do menu → Menu fecha

### Tablet:
1. Header preto fixo no topo com título CEMOS 2028
2. Botão menu no header
3. Toque no botão → Menu expande para baixo
4. Overlay escurece o conteúdo
5. Toque em item ou overlay → Menu colapsa

### Desktop:
1. Menu lateral sempre visível (280px)
2. Navegação sem interrupções
3. Sem botões de toggle necessários

---

## 🔧 Manutenção

### Adicionar novo breakpoint:

1. Atualizar `home.component.ts`:
```typescript
this.breakpointObserver.observe([
  '(max-width: SEU_BREAKPOINT)',
  // ...
])
```

2. Adicionar lógica no subscribe
3. Criar estilos específicos em `home.component.scss`

### Modificar larguras/alturas:

Editar variáveis CSS em `home.component.scss`:
```scss
:root {
  --header-height: 64px;    // Altura do header tablet
  --sidebar-width: 280px;   // Largura do menu lateral
}
```

---

## ✨ Melhorias Implementadas

### Acessibilidade:
- `aria-expanded` nos botões de toggle
- `aria-label` em todos os botões
- Navegação por teclado funcional

### Performance:
- Uso de signals para reatividade eficiente
- Animações com CSS transforms (GPU acelerado)
- Lazy loading com `takeUntilDestroyed()`

### UX:
- Transições suaves (300ms)
- Feedback visual em hover/active
- Auto-fechamento inteligente
- Overlay para contexto visual

---

## 🐛 Solução de Problemas

### Menu não fecha automaticamente no mobile:
Verificar se `(itemClicked)` está emitindo evento:
```html
<app-side-menu (itemClicked)="closeDrawerIfMobile()"></app-side-menu>
```

### Breakpoints não funcionam:
Verificar import do `BreakpointObserver`:
```typescript
import { BreakpointObserver } from '@angular/cdk/layout';
```

### Header duplicado no tablet:
Verificar se `[isTopMenuMode]="true"` está sendo passado:
```html
<app-side-menu [isTopMenuMode]="true"></app-side-menu>
```

---

## 📝 Notas

- Sistema testado em Chrome, Firefox, Safari e Edge
- Compatível com iOS e Android
- Suporta orientação portrait e landscape
- Acessível via teclado (Tab + Enter)


