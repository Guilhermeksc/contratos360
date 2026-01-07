import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EmpresasSancionadasService } from '../../services/empresas-sancionadas.service';
import { EmpresaSancionada } from '../../interfaces/empresas-sancionadas.interface';
import { PageHeaderComponent } from '../../components/page-header/page-header.component';
import { StandardTableComponent } from '../../components/standard-table/standard-table.component';

@Component({
  selector: 'app-empresas-sancionadas',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    PageHeaderComponent,
    StandardTableComponent
  ],
  templateUrl: './empresas-sancionadas.component.html',
  styleUrl: './empresas-sancionadas.component.scss'
})
export class EmpresasSancionadasComponent implements OnInit {
  empresasData = signal<EmpresaSancionada[]>([]);
  filteredData = signal<EmpresaSancionada[]>([]);
  searchTerm = signal('');
  selectedTipoPessoa: 'F' | 'J' | null = null;
  selectedCategoria: string | null = null;
  selectedEsfera: string | null = null;
  selectedUf: string | null = null;
  isDarkTheme = signal<boolean>(false);

  // Opções para filtros
  categorias = signal<string[]>([]);
  esferas = signal<string[]>([]);
  ufs = signal<string[]>([]);

  constructor(
    private empresasSancionadasService: EmpresasSancionadasService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  onSearchChange(searchValue: string): void {
    this.searchTerm.set(searchValue);
    this.applyFilter();
  }

  onTipoPessoaChange(): void {
    this.applyFilter();
  }

  onCategoriaChange(): void {
    this.applyFilter();
  }

  onEsferaChange(): void {
    this.applyFilter();
  }

  onUfChange(): void {
    this.applyFilter();
  }

  applyFilter(): void {
    const term = this.searchTerm().toLowerCase().trim();
    const data = this.empresasData();
    
    let filtered = data;
    
    // Filtro por tipo de pessoa
    if (this.selectedTipoPessoa) {
      filtered = filtered.filter(empresa => empresa.tipo_pessoa === this.selectedTipoPessoa);
    }
    
    // Filtro por categoria
    if (this.selectedCategoria) {
      filtered = filtered.filter(empresa => empresa.categoria_sancao === this.selectedCategoria);
    }
    
    // Filtro por esfera
    if (this.selectedEsfera) {
      filtered = filtered.filter(empresa => empresa.esfera_orgao_sancionador === this.selectedEsfera);
    }
    
    // Filtro por UF
    if (this.selectedUf) {
      filtered = filtered.filter(empresa => empresa.uf_orgao_sancionador === this.selectedUf);
    }
    
    // Filtro de busca de texto
    if (term) {
      filtered = filtered.filter(empresa => {
        const searchFields = [
          empresa.nome_sancionado?.toLowerCase() || '',
          empresa.cpf_cnpj?.toLowerCase() || '',
          empresa.razao_social?.toLowerCase() || '',
          empresa.nome_fantasia?.toLowerCase() || '',
          empresa.numero_processo?.toLowerCase() || '',
          empresa.orgao_sancionador?.toLowerCase() || '',
          empresa.categoria_sancao?.toLowerCase() || '',
          empresa.codigo_sancao?.toLowerCase() || ''
        ];
        
        return searchFields.some(field => field.includes(term));
      });
    }
    
    this.filteredData.set(filtered);
  }

  onThemeToggle(isDark: boolean): void {
    this.isDarkTheme.set(isDark);
  }

  formatDate(date: string | null): string {
    if (!date) return 'N/A';
    try {
      const d = new Date(date);
      return d.toLocaleDateString('pt-BR');
    } catch {
      return date;
    }
  }

  formatCpfCnpj(value: string): string {
    if (!value) return 'N/A';
    // Remove caracteres não numéricos
    const numbers = value.replace(/\D/g, '');
    if (numbers.length === 11) {
      // CPF: 000.000.000-00
      return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    } else if (numbers.length === 14) {
      // CNPJ: 00.000.000/0000-00
      return numbers.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    return value;
  }

  truncateText(text: string | null, maxLength: number): string {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  private loadData(): void {
    this.empresasSancionadasService.list({ ordering: '-data_inicio_sancao' }).subscribe({
      next: (response: any) => {
        let empresas: EmpresaSancionada[] = [];
        
        if (Array.isArray(response)) {
          empresas = response;
        } else if (response && Array.isArray(response.results)) {
          empresas = response.results;
        }
        
        console.log('EmpresasSancionadasComponent: Empresas carregadas:', empresas.length);
        this.empresasData.set(empresas);
        
        // Extrai valores únicos para filtros
        this.extractFilterOptions(empresas);
        
        this.applyFilter();
      },
      error: (err: any) => {
        console.error('Erro ao carregar empresas sancionadas:', err);
        this.empresasData.set([]);
        this.filteredData.set([]);
      }
    });
  }

  private extractFilterOptions(empresas: EmpresaSancionada[]): void {
    const categoriasSet = new Set<string>();
    const esferasSet = new Set<string>();
    const ufsSet = new Set<string>();
    
    empresas.forEach(empresa => {
      if (empresa.categoria_sancao) {
        categoriasSet.add(empresa.categoria_sancao);
      }
      if (empresa.esfera_orgao_sancionador) {
        esferasSet.add(empresa.esfera_orgao_sancionador);
      }
      if (empresa.uf_orgao_sancionador) {
        ufsSet.add(empresa.uf_orgao_sancionador);
      }
    });
    
    this.categorias.set(Array.from(categoriasSet).sort());
    this.esferas.set(Array.from(esferasSet).sort());
    this.ufs.set(Array.from(ufsSet).sort());
  }
}

