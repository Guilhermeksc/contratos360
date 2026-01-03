# Estilos Globais de Markdown

Este arquivo documenta o sistema de estilos globais para conteúdo markdown do projeto CEMOS 2028.

## Visão Geral

O arquivo `/src/assets/styles/markdown-content.scss` contém estilos padronizados para renderização de conteúdo markdown em todo o projeto, garantindo consistência visual e uma experiência de leitura aprimorada com o tema Dracula.

## Como Usar

### 1. Aplicação nos Templates HTML

Para aplicar os estilos globais a um elemento que renderiza conteúdo markdown via `[innerHTML]`:

```html
<div class="markdown-content" [innerHTML]="conteudoMarkdown"></div>
```

### 2. Importação nos Arquivos SCSS

Se você precisar personalizar ou estender os estilos em um componente específico:

```scss
@import '../../../../../assets/styles/markdown-content.scss';

.seu-componente {
  .conteudo-especial {
    @extend .markdown-content;
    // personalizações específicas aqui
  }
}
```

### 3. Uso com ContentService

Os estilos são otimizados para trabalhar com o `ContentService`:

```typescript
import { ContentService } from '../../../services/content.service';

@Component({
  // configuração do componente
})
export class SeuComponente {
  conteudoHtml = '';

  constructor(private contentService: ContentService) {}

  carregarConteudo() {
    this.contentService.loadMarkdownContent('caminho/arquivo.md').subscribe({
      next: (html) => {
        this.conteudoHtml = html;
      }
    });
  }
}
```

E no template:

```html
<div class="markdown-content" [innerHTML]="conteudoHtml"></div>
```

## Estilos Incluídos

### Tipografia
- **H1**: Gradiente roxo-rosa, centralizado, com sublinhado decorativo
- **H2**: Gradiente cyan-verde, com ícone de seta e fundo destacado
- **H3**: Gradiente verde-amarelo, com ponto pulsante
- **H4**: Amarelo com símbolo de diamante
- **H5**: Rosa com símbolo de losango
- **H6**: Laranja com ponto circular

### Elementos de Texto
- **Parágrafos**: Justificados com indentação
- **Negrito**: Gradiente laranja-rosa com fundo destacado
- **Itálico**: Rosa com aspas decorativas
- **Links**: Cyan com efeitos de hover animados

### Listas
- Marcadores customizados com cores do tema Dracula
- Efeitos de hover com animação de deslocamento
- Espaçamento otimizado para legibilidade

### Elementos Especiais
- **Citações**: Fundo gradiente com borda roxa e aspas decorativas
- **Código inline**: Fundo cyan translúcido
- **Blocos de código**: Fundo escuro com bordas arredondadas
- **Tabelas**: Estilo moderno com hover effects
- **Separadores**: Gradiente animado com símbolo central

### Caixas de Destaque
- `.highlight-box`: Caixa de destaque roxa com ícone de diamante
- `.info-box`: Caixa informativa cyan
- `.warning-box`: Caixa de aviso laranja

### Classes de Utilidade
- Cores de texto: `.text-purple`, `.text-cyan`, `.text-green`, etc.
- Backgrounds: `.bg-purple`, `.bg-cyan`, `.bg-green`, etc.

## Responsividade

Os estilos incluem breakpoints responsivos:
- **768px**: Ajustes para tablets
- **480px**: Ajustes para dispositivos móveis

## Animações

Inclui animações CSS para:
- Entrada de títulos (`slideIn`)
- Pulsação de elementos (`pulse`)
- Brilho de elementos (`glow`)
- Cintilação (`sparkle`)

## Tema Dracula

Todas as cores seguem a paleta do tema Dracula:
- **Background**: #282a36
- **Foreground**: #f8f8f2
- **Purple**: #bd93f9
- **Cyan**: #8be9fd
- **Green**: #50fa7b
- **Yellow**: #f1fa8c
- **Orange**: #ffb86c
- **Pink**: #ff79c6
- **Red**: #ff5555

## Componentes que Usam os Estilos

Atualmente implementado em:
- `app4-historia-bibliografia` (seção de bibliografia)
- `breve-historia` (conteúdo dos capítulos)

## Extensibilidade

Para adicionar novos estilos ou personalizar elementos específicos:

1. Crie uma variação dentro do `.markdown-content`
2. Use as variáveis CSS do tema Dracula
3. Mantenha consistência com animações e espaçamentos existentes
4. Teste a responsividade

## Exemplo Completo

```typescript
// componente.ts
export class MeuComponente {
  conteudo = '';
  
  constructor(private contentService: ContentService) {}
  
  ngOnInit() {
    this.contentService.loadMarkdownContent('meu-arquivo.md').subscribe({
      next: (html) => this.conteudo = html
    });
  }
}
```

```html
<!-- componente.html -->
<div class="container">
  <div class="markdown-content" [innerHTML]="conteudo"></div>
</div>
```

```scss
// componente.scss
@import '../../../assets/styles/markdown-content.scss';

.container {
  padding: 2rem;
  background: var(--dracula-background);
}
```

Este sistema garante que todo conteúdo markdown tenha uma aparência consistente e profissional em todo o projeto.