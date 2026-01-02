# Component BibliografiaCompleta

## Descrição
O component `BibliografiaCompleta` é um component reutilizável do Angular que fornece uma interface com 3 abas para exibir conteúdo bibliográfico: **Livro**, **Vídeo** e **Podcast/Perguntas**.

## Características
- ✅ 3 abas interativas: Livro, Vídeo, Podcast/Perguntas
- ✅ Interface responsiva com tema Dracula
- ✅ Suporte a capítulos de livros com navegação lateral
- ✅ Player de vídeo integrado (YouTube)
- ✅ Seção de podcasts com links externos
- ✅ Accordion de perguntas com níveis de dificuldade
- ✅ Totalmente tipado com TypeScript
- ✅ Reutilizável em qualquer módulo

## Como Usar

### 1. Importar o Component
```typescript
import { BibliografiaCompleta } from '../../../../components/bibliografia-completa/bibliografia-completa';
import { BibliografiaCompletaData } from '../../../../interfaces/bibliografia-completa.interface';

@Component({
  // ...
  imports: [
    // outros imports...
    BibliografiaCompleta
  ],
  // ...
})
```

### 2. Usar no Template
```html
<app-bibliografia-completa 
  [data]="bibliografiaData"
  [initialTab]="'livro'">
</app-bibliografia-completa>
```

### 3. Definir os Dados no Component
```typescript
export class SeuComponent {
  bibliografiaData: BibliografiaCompletaData = {
    livro: {
      titulo: 'Nome do Livro',
      autor: 'Nome do Autor',
      descricao: 'Descrição do livro...',
      imagemCapa: '/path/para/capa.jpg',
      linkCompra: 'https://link-para-compra.com',
      capitulos: [
        {
          id: 'cap1',
          titulo: 'Capítulo 1',
          paginas: 'Páginas 1-20',
          descricao: 'Descrição do capítulo',
          conteudo: '<p>Conteúdo HTML do capítulo...</p>'
        }
        // mais capítulos...
      ]
    },
    video: {
      titulo: 'Seção de Vídeos',
      descricao: 'Descrição da seção...',
      videos: [
        {
          id: 'video1',
          titulo: 'Nome do Vídeo',
          url: 'https://youtube.com/watch?v=exemplo',
          duracao: '45 min',
          descricao: 'Descrição do vídeo',
          thumbnail: '/path/para/thumb.jpg'
        }
        // mais vídeos...
      ]
    },
    podcastPerguntas: {
      titulo: 'Podcasts e Perguntas',
      descricao: 'Descrição da seção...',
      podcasts: [
        {
          id: 'podcast1',
          titulo: 'Nome do Podcast',
          url: 'https://spotify.com/episode/exemplo',
          duracao: '60 min',
          descricao: 'Descrição do podcast',
          data: '01/01/2024'
        }
        // mais podcasts...
      ],
      perguntas: [
        {
          id: 'pergunta1',
          pergunta: 'Qual é a pergunta?',
          resposta: '<p>Resposta em HTML...</p>',
          categoria: 'Categoria da Pergunta',
          dificuldade: 'facil' // 'facil', 'medio', 'dificil'
        }
        // mais perguntas...
      ]
    }
  };
}
```

## Propriedades de Entrada

### `data` (obrigatório)
- **Tipo**: `BibliografiaCompletaData`
- **Descrição**: Objeto contendo todos os dados das 3 abas

### `initialTab` (opcional)
- **Tipo**: `'livro' | 'video' | 'podcastPerguntas'`
- **Padrão**: `'livro'`
- **Descrição**: Define qual aba será exibida inicialmente

## Estrutura dos Dados

### Interface `BibliografiaCompletaData`
```typescript
export interface BibliografiaCompletaData {
  livro: {
    titulo: string;
    autor: string;
    descricao?: string;
    capitulos?: CapituloLivro[];
    imagemCapa?: string;
    linkCompra?: string;
  };
  video: {
    titulo: string;
    descricao?: string;
    videos?: VideoItem[];
  };
  podcastPerguntas: {
    titulo: string;
    descricao?: string;
    podcasts?: PodcastItem[];
    perguntas?: PerguntaItem[];
  };
}
```

### Outras Interfaces
- `CapituloLivro`: Define estrutura dos capítulos do livro
- `VideoItem`: Define estrutura dos vídeos
- `PodcastItem`: Define estrutura dos podcasts
- `PerguntaItem`: Define estrutura das perguntas

## Funcionalidades por Aba

### Aba Livro
- Exibição de informações do livro (título, autor, capa)
- Lista de capítulos navegável
- Visualização do conteúdo do capítulo selecionado
- Link para compra (se fornecido)

### Aba Vídeo
- Lista de vídeos com thumbnails
- Player integrado para YouTube
- Informações de duração e descrição
- Seleção interativa de vídeos

### Aba Podcast/Perguntas
- Grid de podcasts com links externos
- Accordion de perguntas com níveis de dificuldade
- Categorização das perguntas
- Respostas expandíveis

## Responsividade
O component é totalmente responsivo e se adapta a:
- Desktop: Layout de 2 colunas
- Tablet: Layout adaptativo
- Mobile: Layout de coluna única

## Tema Visual
Utiliza o tema Dracula consistente com o resto da aplicação:
- Cores escuras de fundo
- Destaque em roxo, cyan, verde, amarelo
- Animações suaves
- Hover effects
- Estados ativos visuais

## Exemplos de Uso
O component já está integrado em:
- `vinganca-geografia.html` e `vinganca-geografia.ts`
- `breve-historia.html` e `breve-historia.ts`

## Personalização
Para personalizar estilos, edite:
```scss
// /src/app/components/bibliografia-completa/bibliografia-completa.scss
```

## Dependências
- Angular Common Module
- Interfaces customizadas do projeto
- Estilos do tema Dracula (definidos em variáveis CSS)