# Componente Genérico de Bibliografia

Este documento explica como usar o componente `GenericBibliografia` que foi criado para reutilizar a estrutura comum entre os diferentes módulos de bibliografia.

## Estrutura dos Arquivos

```
src/app/
├── components/
│   └── generic-bibliografia/
│       ├── generic-bibliografia.ts
│       ├── generic-bibliografia.html
│       └── generic-bibliografia.scss
└── interfaces/
    └── bibliografia-topic.interface.ts
```

## Como Usar

### 1. Importe o componente

```typescript
import { GenericBibliografia } from '../../../components/generic-bibliografia/generic-bibliografia';
import { BibliografiaConfig } from '../../../interfaces/bibliografia-topic.interface';
```

### 2. Configure os dados do módulo

```typescript
export class SeuModuloBibliografia implements OnInit {
  bibliografiaConfig: BibliografiaConfig = {
    moduleRoute: 'seu-modulo', // Nome da rota do módulo
    bibliografiaServiceMethod: 'loadSuaBibliografia', // Método do ContentService (opcional)
    topics: [
      {
        id: 'topico-1',
        title: 'Título do Tópico',
        description: 'Descrição do tópico',
        imageUrl: '/assets/content/caminho/para/imagem.jpg',
        routePath: 'rota-do-topico'
      }
      // ... mais tópicos
    ]
  };
}
```

### 3. Use no template

```html
<app-generic-bibliografia [config]="bibliografiaConfig"></app-generic-bibliografia>
```

## Interface BibliografiaConfig

```typescript
export interface BibliografiaConfig {
  moduleRoute: string;                    // Rota base do módulo
  topics: BibliografiaTopic[];           // Array de tópicos
  bibliografiaServiceMethod?: string;     // Método opcional do ContentService
}

export interface BibliografiaTopic {
  id: string;         // ID único do tópico
  title: string;      // Título exibido no card
  description: string; // Descrição do tópico
  imageUrl: string;   // Caminho da imagem
  routePath: string;  // Rota para navegação
}
```

## Adicionando Método de Bibliografia no ContentService

Se o seu módulo tem uma bibliografia específica, adicione um método no `ContentService`:

```typescript
// No content.service.ts
loadSuaBibliografia(): Observable<string> {
  return this.loadMarkdownContent('seu-modulo/Bibliografia.md');
}
```

Depois, referencie esse método na configuração:

```typescript
bibliografiaConfig: BibliografiaConfig = {
  // ...
  bibliografiaServiceMethod: 'loadSuaBibliografia'
  // ...
};
```

## Estilos

O componente genérico usa o tema Dracula e estilos consistentes. Se precisar de customizações específicas do módulo, adicione no arquivo SCSS do seu componente:

```scss
app-generic-bibliografia {
  // Customizações específicas do módulo
}
```

## Benefícios

1. **Reutilização**: Evita duplicação de código entre módulos
2. **Consistência**: Mantém aparência e comportamento uniformes
3. **Manutenibilidade**: Mudanças são feitas em um só lugar
4. **Flexibilidade**: Configuração por input permite adaptação a diferentes módulos

## Módulos que já usam este componente

- ✅ App4 História
- ✅ App6 Geopolítica e Relações Internacionais

## Próximos passos

Para aplicar este componente em outros módulos:

1. Identifique módulos com estrutura similar de bibliografia
2. Crie a configuração `BibliografiaConfig` específica
3. Substitua o template pelo componente genérico
4. Adicione método no ContentService se necessário
5. Limpe os estilos duplicados