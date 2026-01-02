# FlashCards Service - Documentação Completa

## 📋 Visão Geral

O `FlashCardsService` é um serviço Angular completo para gerenciar flashcards, seguindo o mesmo padrão do `PerguntasService`. Ele fornece todas as funcionalidades CRUD, filtros avançados, busca, estatísticas e paginação.

## 🎯 Características

- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Filtros avançados (bibliografia, assunto, busca textual)
- ✅ Paginação integrada
- ✅ Cache com BehaviorSubjects
- ✅ Loading states
- ✅ Estatísticas e agrupamentos
- ✅ TypeScript com tipagem forte
- ✅ Integração completa com o backend Django

## 📁 Arquivos Envolvidos

### 1. Interface (`interfaces/perguntas.interface.ts`)

```typescript
// Interface principal do FlashCard
export interface FlashCards {
  id: number;
  bibliografia: number;
  bibliografia_titulo?: string;
  pergunta: string;
  resposta: string;
  assunto?: string;  // ✨ Novo campo
}

// Interface de filtros
export interface FlashCardsFilters {
  search?: string;
  bibliografia?: number;
  assunto?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

// Interface de estatísticas
export interface EstatisticasFlashCards {
  total_flashcards: number;
  flashcards_por_assunto: { [assunto: string]: number };
  flashcards_por_bibliografia: { [bibliografia: string]: number };
}

// Bibliografia atualizada
export interface Bibliografia {
  id: number;
  titulo: string;
  autor?: string;
  materia?: string;
  descricao?: string;
  perguntas_count?: number;
  flashcards_count?: number;  // ✨ Novo campo
}
```

### 2. Service (`services/flashcards.service.ts`)

```typescript
@Injectable({ providedIn: 'root' })
export class FlashCardsService {
  private readonly apiUrl = `${environment.apiUrl}/perguntas/api`;
  
  // BehaviorSubjects para cache
  private flashcards$ = new BehaviorSubject<FlashCards[]>([]);
  private loadingFlashCards$ = new BehaviorSubject<boolean>(false);

  // Métodos principais...
}
```

## 🔗 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/flashcards/` | Lista todos os flashcards (com filtros) |
| GET | `/api/flashcards/{id}/` | Busca um flashcard específico |
| POST | `/api/flashcards/` | Cria novo flashcard |
| PUT | `/api/flashcards/{id}/` | Atualiza flashcard (completo) |
| PATCH | `/api/flashcards/{id}/` | Atualiza flashcard (parcial) |
| DELETE | `/api/flashcards/{id}/` | Deleta flashcard |
| GET | `/api/bibliografias/{id}/flashcards/` | Lista flashcards de uma bibliografia |

## 📊 Métodos Disponíveis

### CRUD Básico

```typescript
getFlashCards(filters?: FlashCardsFilters): Observable<PaginatedResponse<FlashCards>>
getFlashCard(id: number): Observable<FlashCards>
createFlashCard(flashcard: Partial<FlashCards>): Observable<FlashCards>
updateFlashCard(id: number, flashcard: Partial<FlashCards>): Observable<FlashCards>
patchFlashCard(id: number, flashcard: Partial<FlashCards>): Observable<FlashCards>
deleteFlashCard(id: number): Observable<void>
```

### Métodos Especializados

```typescript
getFlashCardsByBibliografia(id: number): Observable<FlashCards[]>
getAllFlashCards(): Observable<FlashCards[]>
getFlashCardsByAssunto(assunto: string): Observable<FlashCards[]>
searchFlashCards(searchTerm: string): Observable<FlashCards[]>
getAssuntos(): Observable<string[]>
getEstatisticasFlashCards(): Observable<EstatisticasFlashCards>
```

### Observables de Estado

```typescript
get flashcards(): Observable<FlashCards[]>
get loadingFlashCards(): Observable<boolean>
```

## 🎨 Exemplos de Uso Rápido

### Listar FlashCards
```typescript
this.flashcardsService.getFlashCards().subscribe(response => {
  this.flashcards = response.results;
});
```

### Filtrar por Bibliografia
```typescript
this.flashcardsService.getFlashCards({ bibliografia: 1 }).subscribe(response => {
  this.flashcards = response.results;
});
```

### Filtrar por Assunto
```typescript
this.flashcardsService.getFlashCards({ assunto: 'Princípios' }).subscribe(response => {
  this.flashcards = response.results;
});
```

### Buscar por Texto
```typescript
this.flashcardsService.searchFlashCards('legalidade').subscribe(flashcards => {
  this.resultados = flashcards;
});
```

### Criar FlashCard
```typescript
const novo = {
  bibliografia: 1,
  pergunta: 'O que é X?',
  resposta: 'X é...',
  assunto: 'Conceitos'
};

this.flashcardsService.createFlashCard(novo).subscribe(created => {
  console.log('Criado:', created);
});
```

### Obter Estatísticas
```typescript
this.flashcardsService.getEstatisticasFlashCards().subscribe(stats => {
  console.log('Total:', stats.total_flashcards);
  console.log('Por assunto:', stats.flashcards_por_assunto);
});
```

## 🔍 Filtros Disponíveis

| Filtro | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `search` | string | Busca em pergunta, resposta, assunto | `{ search: 'legalidade' }` |
| `bibliografia` | number | Filtra por ID da bibliografia | `{ bibliografia: 1 }` |
| `assunto` | string | Filtra por assunto | `{ assunto: 'Princípios' }` |
| `ordering` | string | Ordena resultados | `{ ordering: 'assunto' }` |
| `page` | number | Número da página | `{ page: 2 }` |
| `page_size` | number | Itens por página | `{ page_size: 50 }` |

### Exemplos de Ordenação

```typescript
// Crescente
{ ordering: 'assunto' }
{ ordering: 'id' }
{ ordering: 'bibliografia__titulo' }

// Decrescente (adicionar -)
{ ordering: '-assunto' }
{ ordering: '-id' }
```

## 🎯 Casos de Uso Comuns

### 1. Sistema de Estudo com FlashCards

```typescript
export class EstudoComponent {
  currentIndex = 0;
  flashcards: FlashCards[] = [];
  showAnswer = false;

  ngOnInit() {
    this.flashcardsService
      .getFlashCardsByBibliografia(this.bibliografiaId)
      .subscribe(cards => {
        this.flashcards = this.shuffleArray(cards);
      });
  }

  nextCard() {
    this.showAnswer = false;
    this.currentIndex = (this.currentIndex + 1) % this.flashcards.length;
  }

  toggleAnswer() {
    this.showAnswer = !this.showAnswer;
  }
}
```

### 2. Lista com Filtros Múltiplos

```typescript
export class FlashcardsListComponent {
  flashcards: FlashCards[] = [];
  assuntos: string[] = [];
  selectedAssunto: string = '';
  searchTerm: string = '';

  ngOnInit() {
    this.loadAssuntos();
    this.loadFlashCards();
  }

  loadAssuntos() {
    this.flashcardsService.getAssuntos().subscribe(assuntos => {
      this.assuntos = assuntos;
    });
  }

  applyFilters() {
    const filters: FlashCardsFilters = {};
    
    if (this.selectedAssunto) {
      filters.assunto = this.selectedAssunto;
    }
    
    if (this.searchTerm) {
      filters.search = this.searchTerm;
    }

    this.flashcardsService.getFlashCards(filters).subscribe(response => {
      this.flashcards = response.results;
    });
  }
}
```

### 3. Dashboard de Estatísticas

```typescript
export class DashboardComponent {
  stats: EstatisticasFlashCards | null = null;

  ngOnInit() {
    this.flashcardsService.getEstatisticasFlashCards().subscribe(stats => {
      this.stats = stats;
      this.renderCharts(stats);
    });
  }

  renderCharts(stats: EstatisticasFlashCards) {
    // Renderizar gráficos com os dados
    console.log('Total:', stats.total_flashcards);
    
    Object.entries(stats.flashcards_por_assunto).forEach(([assunto, count]) => {
      console.log(`${assunto}: ${count} flashcards`);
    });
  }
}
```

## 🔄 Integração com Backend Django

O service está perfeitamente integrado com o backend Django:

- ✅ URLs corretas: `/perguntas/api/flashcards/`
- ✅ Serialização automática de dados
- ✅ Tratamento de paginação do Django REST Framework
- ✅ Suporte a todos os filtros do backend
- ✅ Validação de dados

## 📝 Notas Importantes

1. **Campo `assunto` é opcional** - Pode ser `null` ou `undefined`
2. **Paginação padrão** - O backend retorna 20 itens por página por padrão
3. **Cache local** - O service mantém cache dos flashcards em BehaviorSubject
4. **Loading states** - Use `loadingFlashCards$` para mostrar spinners
5. **Tipagem forte** - Todas as interfaces são fortemente tipadas

## 🚀 Próximos Passos

1. Criar componentes de UI para exibir flashcards
2. Implementar sistema de repetição espaçada
3. Adicionar sistema de marcação (favoritos, difíceis, etc)
4. Implementar modo de quiz/teste
5. Adicionar estatísticas de progresso do usuário

## 📚 Referências

- [Documentação de Exemplos](./FLASHCARDS_SERVICE_EXAMPLES.md)
- [Documentação do PerguntasService](./PERGUNTAS_SERVICE_EXAMPLES.md)
- Backend: `backend/django_licitacao360/apps/perguntas/`

