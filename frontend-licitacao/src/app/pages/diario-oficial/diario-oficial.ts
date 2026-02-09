import { Component, OnInit, AfterViewInit, signal, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule, MatDatepicker, MatDatepickerInput } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ImprensaNacionalService, InlabsArticleListResponse } from '../../services/imprensa-nacional.service';
import { InlabsArticle } from '../../interfaces/imprensa-nacional.interface';
import { PageHeaderComponent } from '../../components/page-header/page-header.component';
import { StandardTableComponent } from '../../components/standard-table/standard-table.component';

@Component({
  selector: 'app-diario-oficial',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatInputModule,
    MatIconModule,
    MatFormFieldModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    PageHeaderComponent,
    StandardTableComponent,
  ],
  templateUrl: './diario-oficial.html',
  styleUrl: './diario-oficial.scss',
})
export class DiarioOficialComponent implements OnInit, AfterViewInit {
  @ViewChild('picker') picker!: MatDatepicker<Date>;
  @ViewChild('dateInput', { read: MatDatepickerInput }) dateInput!: MatDatepickerInput<Date>;
  
  // Signals para estado
  loading = signal<boolean>(false);
  articles = signal<InlabsArticle[]>([]);
  totalCount = signal<number>(0);
  isDarkTheme = signal<boolean>(false);
  
  // Propriedades de paginação
  pageSize = 10;
  pageIndex = 0;
  pageSizeOptions = [10, 25, 50, 100];
  
  // Propriedades de filtros
  searchTerm = signal<string>('');
  selectedDate: Date | null = null;
  previousSelectedDate: Date | null = null;
  
  // Tabela
  displayedColumns: string[] = ['pub_date', 'uasg', 'art_type', 'objeto', 'pdf_page'];
  dataSource = new MatTableDataSource<InlabsArticle>([]);
  
  constructor(private imprensaNacionalService: ImprensaNacionalService) {}
  
  ngOnInit(): void {
    this.loadArticles();
    this.loadThemePreference();
  }
  
  ngAfterViewInit(): void {
    // Garante que o datepicker está configurado corretamente
    if (this.picker) {
      // O datepicker já está configurado através do template
    }
  }
  
  /**
   * Carrega os artigos da API com os filtros e paginação atuais
   */
  loadArticles(): void {
    this.loading.set(true);
    
    const params: any = {
      page: this.pageIndex + 1, // API usa página baseada em 1
      ordering: '-pub_date,article_id',
    };
    
    // Adiciona filtro de busca se houver
    if (this.searchTerm().trim()) {
      params.search = this.searchTerm().trim();
    }
    
    // Adiciona filtro de data se houver
    if (this.selectedDate) {
      params.pub_date = this.formatDateForApi(this.selectedDate);
    }
    
    this.imprensaNacionalService.list(params).subscribe({
      next: (response) => {
        let articles: InlabsArticle[] = [];
        let count = 0;
        
        // Verifica se a resposta é paginada ou um array direto
        if (this.isPaginatedResponse(response)) {
          const paginatedResponse = response as InlabsArticleListResponse;
          articles = paginatedResponse.results || [];
          count = paginatedResponse.count || 0;
        } else if (Array.isArray(response)) {
          articles = response;
          count = response.length;
        }
        
        this.articles.set(articles);
        this.totalCount.set(count);
        this.dataSource.data = articles;
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Erro ao carregar artigos:', error);
        this.articles.set([]);
        this.totalCount.set(0);
        this.dataSource.data = [];
        this.loading.set(false);
      }
    });
  }
  
  /**
   * Verifica se a resposta é paginada
   */
  private isPaginatedResponse(response: any): response is InlabsArticleListResponse {
    return response && typeof response === 'object' && 'results' in response && 'count' in response;
  }
  
  /**
   * Formata a data para o formato da API (YYYY-MM-DD)
   */
  private formatDateForApi(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  
  /**
   * Formata a data para exibição (DD/MM/YYYY)
   */
  formatDisplayDate(dateString: string | null): string {
    if (!dateString) return 'N/A';
    
    try {
      // Se já estiver no formato YYYY-MM-DD, converte para DD/MM/YYYY
      if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
        const [year, month, day] = dateString.split('-');
        return `${day}/${month}/${year}`;
      }
      
      // Se já estiver no formato DD/MM/YYYY, retorna como está
      if (dateString.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
        return dateString;
      }
      
      // Tenta parsear como Date
      const date = new Date(dateString);
      if (!isNaN(date.getTime())) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
      }
      
      return dateString;
    } catch (error) {
      return dateString;
    }
  }
  
  /**
   * Retorna o valor formatado para o input de data
   */
  dateInputValue(): string {
    if (!this.selectedDate) return '';
    return this.formatDisplayDate(this.formatDateForApi(this.selectedDate));
  }
  
  /**
   * Manipula mudanças no campo de busca
   */
  onSearchChange(): void {
    // Reseta para primeira página ao buscar
    this.pageIndex = 0;
    this.loadArticles();
  }
  
  /**
   * Manipula mudanças no datepicker
   */
  onDateChange(event: any): void {
    if (event && event.value) {
      const newDate = event.value instanceof Date ? event.value : new Date(event.value);
      this.selectedDate = newDate;
      // Reseta para primeira página ao filtrar por data
      this.pageIndex = 0;
      this.loadArticles();
    } else if (event && (event.value === null || event.value === undefined)) {
      // Se a data foi limpa
      this.selectedDate = null;
      this.pageIndex = 0;
      this.loadArticles();
    }
  }
  
  /**
   * Manipula eventos do input de data (disparado quando o valor muda)
   */
  onDateInput(event: any): void {
    if (event && event.value) {
      const newDate = event.value instanceof Date ? event.value : new Date(event.value);
      this.selectedDate = newDate;
      // Reseta para primeira página ao filtrar por data
      this.pageIndex = 0;
      this.loadArticles();
    } else if (event && (event.value === null || event.value === undefined)) {
      // Se a data foi limpa
      this.selectedDate = null;
      this.pageIndex = 0;
      this.loadArticles();
    }
  }
  
  /**
   * Manipula quando o datepicker é fechado
   */
  onDatepickerClosed(): void {
    // Verifica o valor do input quando o datepicker fecha
    // Isso é um fallback caso o evento dateChange não seja disparado
    setTimeout(() => {
      if (this.dateInput && this.dateInput.value) {
        const inputValue = this.dateInput.value;
        let newDate: Date | null = null;
        
        if (inputValue instanceof Date) {
          newDate = inputValue;
        }
        
        // Verifica se a data mudou
        if (newDate && (!this.selectedDate || newDate.getTime() !== this.selectedDate.getTime())) {
          this.selectedDate = newDate;
          this.pageIndex = 0;
          this.loadArticles();
        } else if (!newDate && this.selectedDate) {
          // Se o input foi limpo
          this.selectedDate = null;
          this.pageIndex = 0;
          this.loadArticles();
        }
      }
    }, 100); // Pequeno delay para garantir que o valor foi atualizado
  }
  
  /**
   * Manipula quando o datepicker é aberto
   */
  onDatepickerOpened(): void {
    // Não faz nada por enquanto
  }
  
  /**
   * Limpa todos os filtros
   */
  clearFilters(): void {
    this.searchTerm.set('');
    this.selectedDate = null;
    this.previousSelectedDate = null;
    this.pageIndex = 0;
    this.loadArticles();
  }
  
  /**
   * Manipula mudanças na paginação
   */
  onPageChange(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadArticles();
  }
  
  /**
   * Abre o PDF no portal da Imprensa Nacional
   */
  openPdf(pdfPage: string): void {
    if (pdfPage) {
      // Abre em nova aba
      window.open(pdfPage, '_blank');
    }
  }
  
  /**
   * Manipula o toggle do tema
   */
  onThemeToggle(isDark: boolean): void {
    this.isDarkTheme.set(isDark);
    this.saveThemePreference(isDark);
  }
  
  /**
   * Carrega a preferência de tema salva
   */
  private loadThemePreference(): void {
    const savedTheme = localStorage.getItem('diario-oficial-theme');
    if (savedTheme === 'dark') {
      this.isDarkTheme.set(true);
    } else if (savedTheme === 'light') {
      this.isDarkTheme.set(false);
    } else {
      // Usa preferência do sistema ou padrão claro
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.isDarkTheme.set(prefersDark);
    }
  }
  
  /**
   * Salva a preferência de tema
   */
  private saveThemePreference(isDark: boolean): void {
    localStorage.setItem('diario-oficial-theme', isDark ? 'dark' : 'light');
  }
}