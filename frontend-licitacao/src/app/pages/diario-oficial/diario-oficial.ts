import { Component, OnInit, signal, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule, MatDatepicker } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ImprensaNacionalService } from '../../services/imprensa-nacional.service';
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
export class DiarioOficialComponent implements OnInit {
  @ViewChild('picker') picker!: MatDatepicker<Date>;
  
  displayedColumns: string[] = ['edition_date', 'uasg', 'pub_name', 'art_type', 'objeto', 'pdf_page'];
  dataSource = new MatTableDataSource<InlabsArticle>([]);
  
  articles = signal<InlabsArticle[]>([]);
  loading = signal(false);
  searchTerm = '';
  selectedDate: Date | null = null;
  dateInputValue = signal<string>('');
  isDarkTheme = signal<boolean>(false); // Tema claro (branco) por padrão
  
  // Paginação
  pageSize = 10;
  pageIndex = 0;
  totalCount = signal(0);
  pageSizeOptions = [10, 25, 50, 100];

  constructor(private imprensaNacionalService: ImprensaNacionalService) {}
  
  onThemeToggle(isDark: boolean): void {
    this.isDarkTheme.set(isDark);
  }

  ngOnInit(): void {
    this.loadArticles();
  }

  loadArticles(): void {
    this.loading.set(true);
    
    const params: any = {
      ordering: '-edition_date,article_id',
    };

    if (this.selectedDate) {
      params.edition_date = this.formatDate(this.selectedDate);
    }

    if (this.searchTerm.trim()) {
      params.search = this.searchTerm.trim();
    }

    this.imprensaNacionalService.list(params).subscribe({
      next: (response: any) => {
        let articlesList: InlabsArticle[] = [];
        
        if (Array.isArray(response)) {
          articlesList = response;
          this.totalCount.set(response.length);
        } else if (response && Array.isArray(response.results)) {
          articlesList = response.results;
          this.totalCount.set(response.count || response.results.length);
        }

        this.articles.set(articlesList);
        this.updateDataSource();
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Erro ao carregar artigos:', error);
        this.loading.set(false);
      }
    });
  }

  updateDataSource(): void {
    const startIndex = this.pageIndex * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    const paginatedArticles = this.articles().slice(startIndex, endIndex);
    this.dataSource.data = paginatedArticles;
  }

  onSearchChange(): void {
    this.pageIndex = 0;
    this.loadArticles();
  }

  onDateChange(event?: any): void {
    if (event && event.value) {
      this.selectedDate = event.value;
      this.dateInputValue.set(this.formatDateForInput(event.value));
    } else {
      this.selectedDate = null;
      this.dateInputValue.set('');
    }
    this.pageIndex = 0;
    this.loadArticles();
  }

  onPageChange(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.updateDataSource();
  }

  formatDate(date: Date): string {
    // Usar diretamente os métodos locais do objeto Date para evitar problemas de timezone
    // O Material Datepicker já retorna a data no timezone local
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
  }

  formatDateForInput(date: Date | null): string {
    if (!date) return '';
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  }

  formatDisplayDate(dateString: string): string {
    if (!dateString) return '';
    
    // Se a string já está no formato YYYY-MM-DD (sem hora), usar diretamente
    // Isso evita problemas de timezone quando o backend retorna apenas a data
    // O backend retorna no formato "2026-01-05" (sem hora)
    const dateMatch = dateString.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (dateMatch) {
      const [, year, month, day] = dateMatch;
      return `${day}/${month}/${year}`;
    }
    
    // Se tem hora/timezone, criar data usando componentes locais para evitar timezone
    // Criar a data no timezone local usando os componentes da string
    const date = new Date(dateString);
    // Usar métodos locais para garantir que não haja conversão de timezone
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  }

  openPdf(pdfPage: string): void {
    if (pdfPage) {
      window.open(pdfPage, '_blank');
    }
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedDate = null;
    this.dateInputValue.set('');
    this.pageIndex = 0;
    this.loadArticles();
  }
}
