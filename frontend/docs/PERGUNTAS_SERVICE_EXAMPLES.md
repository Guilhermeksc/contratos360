# Como usar o PerguntasService

## Exemplo de uso em um componente Angular

```typescript
import { Component, OnInit } from '@angular/core';
import { PerguntasService } from '../services/perguntas.service';
import { 
  Bibliografia, 
  PerguntaMultipla, 
  PerguntaVF, 
  PerguntaCorrelacao,
  BibliografiaCreateUpdate,
  PerguntaMultiplaCreateUpdate,
  PerguntaVFCreateUpdate,
  PerguntaCorrelacaoCreateUpdate,
  EstatisticasGerais
} from '../interfaces/perguntas';

@Component({
  selector: 'app-perguntas',
  templateUrl: './perguntas.component.html'
})
export class PerguntasComponent implements OnInit {
  bibliografias: Bibliografia[] = [];
  perguntasMultipla: PerguntaMultipla[] = [];
  perguntasVF: PerguntaVF[] = [];
  perguntasCorrelacao: PerguntaCorrelacao[] = [];
  estatisticas?: EstatisticasGerais;
  loading = false;

  constructor(private perguntasService: PerguntasService) {}

  ngOnInit() {
    this.loadData();
  }

  // ==================== CARREGAMENTO DE DADOS ====================

  loadData() {
    this.loading = true;
    
    // Carregar bibliografias
    this.perguntasService.getBibliografias({ page_size: 50 }).subscribe({
      next: (response) => {
        this.bibliografias = response.results;
        console.log('Bibliografias carregadas:', this.bibliografias.length);
      },
      error: (error) => console.error('Erro ao carregar bibliografias:', error)
    });

    // Carregar perguntas múltipla escolha
    this.perguntasService.getPerguntasMultipla({ page_size: 50 }).subscribe({
      next: (response) => {
        this.perguntasMultipla = response.results;
        console.log('Perguntas múltipla escolha:', this.perguntasMultipla.length);
      },
      error: (error) => console.error('Erro ao carregar perguntas múltipla:', error)
    });

    // Carregar estatísticas
    this.perguntasService.getEstatisticasGerais().subscribe({
      next: (stats) => {
        this.estatisticas = stats;
        console.log('Estatísticas:', stats);
        this.loading = false;
      },
      error: (error) => {
        console.error('Erro ao carregar estatísticas:', error);
        this.loading = false;
      }
    });
  }

  // ==================== OPERAÇÕES COM BIBLIOGRAFIAS ====================

  createBibliografia() {
    const novaBibliografia: BibliografiaCreateUpdate = {
      titulo: 'Manual de Licitações 2024',
      autor: 'João Silva',
      descricao: 'Manual atualizado com as novas regras de licitação'
    };

    this.perguntasService.createBibliografia(novaBibliografia).subscribe({
      next: (bibliografia) => {
        console.log('Bibliografia criada:', bibliografia);
        this.loadData(); // Recarregar dados
      },
      error: (error) => console.error('Erro ao criar bibliografia:', error)
    });
  }

  updateBibliografia(id: number) {
    const updates = {
      titulo: 'Manual de Licitações 2024 - Atualizado',
      descricao: 'Manual atualizado com correções importantes'
    };

    this.perguntasService.updateBibliografia(id, updates).subscribe({
      next: (bibliografia) => {
        console.log('Bibliografia atualizada:', bibliografia);
        this.loadData();
      },
      error: (error) => console.error('Erro ao atualizar bibliografia:', error)
    });
  }

  deleteBibliografia(id: number) {
    if (confirm('Tem certeza que deseja excluir esta bibliografia?')) {
      this.perguntasService.deleteBibliografia(id).subscribe({
        next: () => {
          console.log('Bibliografia excluída');
          this.loadData();
        },
        error: (error) => console.error('Erro ao excluir bibliografia:', error)
      });
    }
  }

  // ==================== OPERAÇÕES COM PERGUNTAS MÚLTIPLA ESCOLHA ====================

  createPerguntaMultipla(bibliografiaId: number) {
    const novaPergunta: PerguntaMultiplaCreateUpdate = {
      bibliografia: bibliografiaId,
      caiu_em_prova: true,
      ano_prova: 2023,
      pergunta: 'Qual o prazo mínimo para publicação de edital de concorrência?',
      alternativa_a: '15 dias',
      alternativa_b: '30 dias',
      alternativa_c: '45 dias',
      alternativa_d: '60 dias',
      resposta_correta: 'b',
      justificativa_resposta_certa: 'Conforme art. 21, §2º, I da Lei 8.666/93, o prazo mínimo é de 30 dias.'
    };

    // Validar antes de enviar
    const errors = this.perguntasService.validatePerguntaMultipla(novaPergunta);
    if (errors.length > 0) {
      console.error('Erros de validação:', errors);
      return;
    }

    this.perguntasService.createPerguntaMultipla(novaPergunta).subscribe({
      next: (pergunta) => {
        console.log('Pergunta múltipla criada:', pergunta);
        this.loadData();
      },
      error: (error) => console.error('Erro ao criar pergunta:', error)
    });
  }

  // ==================== OPERAÇÕES COM PERGUNTAS V/F ====================

  createPerguntaVF(bibliografiaId: number) {
    const novaPergunta: PerguntaVFCreateUpdate = {
      bibliografia: bibliografiaId,
      caiu_em_prova: false,
      pergunta: 'Analise a afirmação sobre dispensa de licitação:',
      afirmacao: 'A dispensa de licitação pode ocorrer para valores até R$ 17.600,00 para compras e serviços.',
      resposta_correta: true,
      justificativa_resposta_certa: 'Correto conforme art. 24, II da Lei 8.666/93 (valor atualizado).'
    };

    const errors = this.perguntasService.validatePerguntaVF(novaPergunta);
    if (errors.length > 0) {
      console.error('Erros de validação:', errors);
      return;
    }

    this.perguntasService.createPerguntaVF(novaPergunta).subscribe({
      next: (pergunta) => {
        console.log('Pergunta V/F criada:', pergunta);
        this.loadData();
      },
      error: (error) => console.error('Erro ao criar pergunta V/F:', error)
    });
  }

  // ==================== OPERAÇÕES COM PERGUNTAS DE CORRELAÇÃO ====================

  createPerguntaCorrelacao(bibliografiaId: number) {
    const novaPergunta: PerguntaCorrelacaoCreateUpdate = {
      bibliografia: bibliografiaId,
      caiu_em_prova: true,
      ano_prova: 2022,
      pergunta: 'Correlacione as modalidades de licitação com suas características:',
      coluna_a: ['Convite', 'Tomada de Preços', 'Concorrência'],
      coluna_b: [
        'Obras e serviços até R$ 330.000,00',
        'Cadastro prévio obrigatório',
        'Qualquer valor, ampla publicidade'
      ],
      resposta_correta: {
        '0': '0', // Convite -> Obras e serviços até R$ 330.000,00
        '1': '1', // Tomada de Preços -> Cadastro prévio obrigatório
        '2': '2'  // Concorrência -> Qualquer valor, ampla publicidade
      },
      justificativa_resposta_certa: 'Correlação baseada nos artigos 22 e 23 da Lei 8.666/93.'
    };

    const errors = this.perguntasService.validatePerguntaCorrelacao(novaPergunta);
    if (errors.length > 0) {
      console.error('Erros de validação:', errors);
      return;
    }

    this.perguntasService.createPerguntaCorrelacao(novaPergunta).subscribe({
      next: (pergunta) => {
        console.log('Pergunta de correlação criada:', pergunta);
        this.loadData();
      },
      error: (error) => console.error('Erro ao criar pergunta de correlação:', error)
    });
  }

  // ==================== FILTROS E BUSCAS ====================

  searchBibliografias(termo: string) {
    this.perguntasService.getBibliografias({ 
      search: termo,
      ordering: '-created_at'
    }).subscribe({
      next: (response) => {
        this.bibliografias = response.results;
        console.log(`Encontradas ${response.count} bibliografias`);
      },
      error: (error) => console.error('Erro na busca:', error)
    });
  }

  filterPerguntasByAno(ano: number) {
    this.perguntasService.getPerguntasMultipla({
      ano_prova: ano,
      caiu_em_prova: true
    }).subscribe({
      next: (response) => {
        console.log(`Perguntas de ${ano}:`, response.results);
      },
      error: (error) => console.error('Erro no filtro:', error)
    });
  }

  // ==================== ESTATÍSTICAS E RELATÓRIOS ====================

  loadEstatisticasBibliografia(id: number) {
    this.perguntasService.getEstatisticasBibliografia(id).subscribe({
      next: (stats) => {
        console.log('Estatísticas da bibliografia:', stats);
      },
      error: (error) => console.error('Erro ao carregar estatísticas:', error)
    });
  }

  loadPerguntasByBibliografia(id: number) {
    this.perguntasService.getPerguntasByBibliografia(id).subscribe({
      next: (perguntas) => {
        console.log('Perguntas da bibliografia:', perguntas);
      },
      error: (error) => console.error('Erro ao carregar perguntas:', error)
    });
  }

  // ==================== OBSERVABLES PARA LOADING ====================

  subscribeToLoading() {
    this.perguntasService.loadingBibliografias.subscribe(loading => {
      console.log('Loading bibliografias:', loading);
    });

    this.perguntasService.loadingPerguntas.subscribe(loading => {
      console.log('Loading perguntas:', loading);
    });
  }
}
```

## Exemplo de Template HTML

```html
<div class="perguntas-container">
  <!-- Loading -->
  <div *ngIf="loading" class="loading">
    Carregando dados...
  </div>

  <!-- Estatísticas -->
  <div *ngIf="estatisticas" class="estatisticas">
    <h3>Estatísticas Gerais</h3>
    <p>Total de bibliografias: {{ estatisticas.total_bibliografias }}</p>
    <p>Total de perguntas: {{ estatisticas.total_perguntas }}</p>
    <p>Perguntas múltipla escolha: {{ estatisticas.perguntas_por_tipo.multipla }}</p>
    <p>Perguntas V/F: {{ estatisticas.perguntas_por_tipo.vf }}</p>
    <p>Perguntas correlação: {{ estatisticas.perguntas_por_tipo.correlacao }}</p>
    <p>Perguntas que caíram em prova: {{ estatisticas.perguntas_que_cairam_prova }}</p>
  </div>

  <!-- Lista de Bibliografias -->
  <div class="bibliografias">
    <h3>Bibliografias</h3>
    <button (click)="createBibliografia()">Nova Bibliografia</button>
    
    <div *ngFor="let bib of bibliografias" class="bibliografia-item">
      <h4>{{ bib.titulo }}</h4>
      <p>Autor: {{ bib.autor || 'Não informado' }}</p>
      <p>Total de perguntas: {{ bib.perguntas_count || 0 }}</p>
      
      <button (click)="updateBibliografia(bib.id)">Editar</button>
      <button (click)="deleteBibliografia(bib.id)">Excluir</button>
      <button (click)="loadPerguntasByBibliografia(bib.id)">Ver Perguntas</button>
      <button (click)="createPerguntaMultipla(bib.id)">Nova Pergunta Múltipla</button>
      <button (click)="createPerguntaVF(bib.id)">Nova Pergunta V/F</button>
      <button (click)="createPerguntaCorrelacao(bib.id)">Nova Pergunta Correlação</button>
    </div>
  </div>

  <!-- Lista de Perguntas Múltipla Escolha -->
  <div class="perguntas-multipla">
    <h3>Perguntas Múltipla Escolha</h3>
    <div *ngFor="let pergunta of perguntasMultipla" class="pergunta-item">
      <h4>{{ pergunta.pergunta }}</h4>
      <p>Bibliografia: {{ pergunta.bibliografia_titulo }}</p>
      <p>Resposta correta: {{ pergunta.resposta_correta_display }}</p>
      <p *ngIf="pergunta.caiu_em_prova">Caiu em prova: {{ pergunta.ano_prova }}</p>
      
      <div class="alternativas">
        <p>A) {{ pergunta.alternativa_a }}</p>
        <p>B) {{ pergunta.alternativa_b }}</p>
        <p>C) {{ pergunta.alternativa_c }}</p>
        <p>D) {{ pergunta.alternativa_d }}</p>
      </div>
    </div>
  </div>
</div>
```

## Exemplo de uso com formulários reativos

```typescript
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

export class PerguntaFormComponent implements OnInit {
  perguntaForm: FormGroup;
  bibliografias: Bibliografia[] = [];

  constructor(
    private fb: FormBuilder,
    private perguntasService: PerguntasService
  ) {
    this.perguntaForm = this.fb.group({
      bibliografia: ['', Validators.required],
      pergunta: ['', Validators.required],
      alternativa_a: ['', Validators.required],
      alternativa_b: ['', Validators.required],
      alternativa_c: ['', Validators.required],
      alternativa_d: ['', Validators.required],
      resposta_correta: ['', Validators.required],
      justificativa_resposta_certa: ['', Validators.required],
      caiu_em_prova: [false],
      ano_prova: ['']
    });
  }

  ngOnInit() {
    this.loadBibliografias();
  }

  loadBibliografias() {
    this.perguntasService.getBibliografias().subscribe({
      next: (response) => this.bibliografias = response.results,
      error: (error) => console.error('Erro ao carregar bibliografias:', error)
    });
  }

  onSubmit() {
    if (this.perguntaForm.valid) {
      const perguntaData = this.perguntaForm.value as PerguntaMultiplaCreateUpdate;
      
      // Validar com o service
      const errors = this.perguntasService.validatePerguntaMultipla(perguntaData);
      if (errors.length > 0) {
        console.error('Erros de validação:', errors);
        return;
      }

      this.perguntasService.createPerguntaMultipla(perguntaData).subscribe({
        next: (pergunta) => {
          console.log('Pergunta criada com sucesso:', pergunta);
          this.perguntaForm.reset();
        },
        error: (error) => console.error('Erro ao criar pergunta:', error)
      });
    }
  }
}
```