import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { firstValueFrom } from 'rxjs';
import * as XLSX from 'xlsx';
import { PncpService } from '../../../services/pncp.service';
import { FiltroBusca } from '../../../components/filtro-busca/filtro-busca';
import { 
  Compra, 
  ItemResultadoMerge, 
  ModalidadeAgregada, 
  FornecedorAgregado,
  AnosUnidadesCombo,
  UnidadeComSigla
} from '../../../interfaces/pncp.interface';

@Component({
  selector: 'app-ccimar-pncp',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    FiltroBusca
  ],
  templateUrl: './ccimar-pncp.html',
  styleUrl: './ccimar-pncp.scss',
})
export class CcimarPncp implements OnInit {
  private _codigoUnidade = signal<string>('765701');
  filtroUnidade = signal<string>('765701');
  codigoUnidadeSelecionado = signal<string>('765701');
  unidadesDisponiveis = signal<UnidadeComSigla[]>([]);
  loading = signal<boolean>(false);
  loadingTab = signal<string | null>(null);
  
  // Dados
  compras = signal<Compra[]>([]);
  itensMerge = signal<ItemResultadoMerge[]>([]);
  modalidades = signal<ModalidadeAgregada[]>([]);
  fornecedores = signal<FornecedorAgregado[]>([]);
  
  // Estados de carregamento por aba
  loadingCompras = signal<boolean>(false);
  loadingItens = signal<boolean>(false);
  loadingModalidades = signal<boolean>(false);
  loadingFornecedores = signal<boolean>(false);
  
  // Tabelas
  displayedColumnsCompras: string[] = ['numero_compra', 'ano_compra', 'modalidade', 'objeto_compra', 'valor_total_estimado', 'valor_total_homologado'];
  displayedColumnsItens: string[] = ['numero_item', 'descricao', 'quantidade', 'valor_total_estimado', 'valor_total_homologado', 'percentual_desconto', 'razao_social'];
  displayedColumnsModalidades: string[] = ['ano_compra', 'modalidade', 'quantidade_compras', 'valor_total_homologado'];
  displayedColumnsFornecedores: string[] = ['cnpj_fornecedor', 'razao_social', 'valor_total_homologado'];

  constructor(
    private pncpService: PncpService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.carregarUnidadesDisponiveis();
    this.carregarDados();
  }

  carregarDados(): void {
    const codigo = this._codigoUnidade();
    if (!codigo) {
      this.snackBar.open('Informe o código da unidade', 'Fechar', { duration: 3000 });
      return;
    }
    this.codigoUnidadeSelecionado.set(codigo);

    this.loading.set(true);
    this.loadingCompras.set(true);
    this.loadingItens.set(true);
    this.loadingModalidades.set(true);
    this.loadingFornecedores.set(true);

    // Carrega todos os dados em paralelo
    Promise.all([
      firstValueFrom(this.pncpService.getComprasPorUnidade(codigo)),
      firstValueFrom(this.pncpService.getItensResultadoMerge(codigo)),
      firstValueFrom(this.pncpService.getModalidadesAgregadas(codigo)),
      firstValueFrom(this.pncpService.getFornecedoresAgregados(codigo))
    ]).then(([compras, itens, modalidades, fornecedores]) => {
      // Usa setTimeout para tornar a transição mais suave
      setTimeout(() => {
        this.compras.set(compras || []);
        this.loadingCompras.set(false);
      }, 100);
      
      setTimeout(() => {
        this.itensMerge.set(itens || []);
        this.loadingItens.set(false);
      }, 150);
      
      setTimeout(() => {
        this.modalidades.set(modalidades || []);
        this.loadingModalidades.set(false);
      }, 200);
      
      setTimeout(() => {
        this.fornecedores.set(fornecedores || []);
        this.loadingFornecedores.set(false);
        this.loading.set(false);
      }, 250);
    }).catch(error => {
      console.error('Erro ao carregar dados:', error);
      this.snackBar.open('Erro ao carregar dados. Verifique o código da unidade.', 'Fechar', { duration: 5000 });
      this.loading.set(false);
      this.loadingCompras.set(false);
      this.loadingItens.set(false);
      this.loadingModalidades.set(false);
      this.loadingFornecedores.set(false);
    });
  }

  onTabChange(index: number): void {
    // Adiciona um pequeno delay ao trocar de aba para melhorar a fluidez
    const tabNames = ['compras', 'itens', 'modalidades', 'fornecedores'];
    const tabName = tabNames[index];
    
    if (tabName) {
      this.loadingTab.set(tabName);
      // Remove o loading após um pequeno delay para permitir renderização suave
      setTimeout(() => {
        this.loadingTab.set(null);
      }, 200);
    }
  }

  async carregarUnidadesDisponiveis(): Promise<void> {
    try {
      const dados: AnosUnidadesCombo = await firstValueFrom(this.pncpService.getAnosUnidadesCombo());
      const unidades = Object.values(dados.unidades_por_ano).flat();
      const unidadesUnicas = Array.from(
        new Map(unidades.map((unidade) => [unidade.codigo_unidade, unidade])).values()
      );
      this.unidadesDisponiveis.set(unidadesUnicas);
    } catch (error) {
      console.error('Erro ao carregar unidades para busca:', error);
    }
  }

  onFiltroUnidadeChange(valor: string): void {
    this.filtroUnidade.set(valor);
  }

  onFiltroUnidadeEnter(valor: string): void {
    this.buscarPorTexto(valor);
  }

  onUnidadeSelected(unidade: UnidadeComSigla): void {
    this._codigoUnidade.set(unidade.codigo_unidade);
    this.filtroUnidade.set(this.getUnidadeDisplayText(unidade));
    this.codigoUnidadeSelecionado.set(unidade.codigo_unidade);
    this.carregarDados();
  }

  buscarPorFiltro(): void {
    this.buscarPorTexto(this.filtroUnidade());
  }

  getUnidadeDisplayText(unidade: UnidadeComSigla): string {
    const sigla = unidade.sigla_om ? ` - ${unidade.sigla_om}` : '';
    return `${unidade.codigo_unidade}${sigla}`;
  }

  getUasgSelecionadaTexto(): string {
    const codigo = this.codigoUnidadeSelecionado();
    const unidade = this.unidadesDisponiveis().find((item) => item.codigo_unidade === codigo);
    return unidade ? this.getUnidadeDisplayText(unidade) : codigo;
  }

  exportarXlsx(): void {
    const codigo = this._codigoUnidade();
    if (!codigo) {
      this.snackBar.open('Informe o código da unidade', 'Fechar', { duration: 3000 });
      return;
    }

    const compras = this.compras();
    const itensMerge = this.itensMerge();
    const modalidades = this.modalidades();
    const fornecedores = this.fornecedores();

    if (compras.length === 0 && itensMerge.length === 0) {
      this.snackBar.open('Não há dados para exportar. Carregue os dados primeiro.', 'Fechar', { duration: 3000 });
      return;
    }

    try {
      this.loading.set(true);
      
      // Criar workbook
      const wb = XLSX.utils.book_new();

      // Sheet 1: Compras
      if (compras.length > 0) {
        const comprasData = compras.map(c => ({
          compra_id: c.compra_id,
          ano_compra: c.ano_compra,
          sequencial_compra: c.sequencial_compra,
          numero_compra: c.numero_compra,
          codigo_unidade: c.codigo_unidade,
          objeto_compra: c.objeto_compra,
          modalidade_nome: c.modalidade?.nome || '',
          numero_processo: c.numero_processo,
          data_publicacao_pncp: c.data_publicacao_pncp || '',
          data_atualizacao: c.data_atualizacao || '',
          valor_total_estimado: this.converterParaNumero(c.valor_total_estimado),
          valor_total_homologado: this.converterParaNumero(c.valor_total_homologado),
          percentual_desconto: this.converterPercentual(c.percentual_desconto)
        }));
        const wsCompras = XLSX.utils.json_to_sheet(comprasData);
        this.aplicarFormatacaoCelulas(wsCompras, ['valor_total_estimado', 'valor_total_homologado'], ['percentual_desconto']);
        XLSX.utils.book_append_sheet(wb, wsCompras, 'compras');
      }

      // Sheet 2: Itens com Resultados
      if (itensMerge.length > 0) {
        const itensData = itensMerge.map(i => ({
          ano_compra: i.ano_compra,
          sequencial_compra: i.sequencial_compra,
          numero_item: i.numero_item,
          descricao: i.descricao,
          unidade_medida: i.unidade_medida,
          quantidade: this.converterParaNumero(i.quantidade),
          valor_unitario_estimado: this.converterParaNumero(i.valor_unitario_estimado),
          valor_total_estimado: this.converterParaNumero(i.valor_total_estimado),
          valor_unitario_homologado: this.converterParaNumero(i.valor_unitario_homologado),
          valor_total_homologado: this.converterParaNumero(i.valor_total_homologado),
          quantidade_homologada: i.quantidade_homologada,
          percentual_desconto: this.converterPercentual(i.percentual_desconto),
          situacao_compra_item_nome: i.situacao_compra_item_nome,
          cnpj_fornecedor: i.cnpj_fornecedor || '',
          razao_social: i.razao_social || ''
        }));
        const wsItens = XLSX.utils.json_to_sheet(itensData);
        this.aplicarFormatacaoCelulas(
          wsItens, 
          ['valor_unitario_estimado', 'valor_total_estimado', 'valor_unitario_homologado', 'valor_total_homologado'], 
          ['percentual_desconto']
        );
        XLSX.utils.book_append_sheet(wb, wsItens, 'itens_resultado_merge');
      }

      // Sheet 3: Modalidades Agregadas
      if (modalidades.length > 0) {
        const modalidadesData = modalidades.map(m => ({
          ano_compra: m.ano_compra,
          modalidade_nome: m.modalidade?.nome || '',
          quantidade_compras: m.quantidade_compras,
          valor_total_homologado: this.converterParaNumero(m.valor_total_homologado)
        }));
        const wsModalidades = XLSX.utils.json_to_sheet(modalidadesData);
        this.aplicarFormatacaoCelulas(wsModalidades, ['valor_total_homologado'], []);
        XLSX.utils.book_append_sheet(wb, wsModalidades, 'modalidades');
      }

      // Sheet 4: Fornecedores Agregados
      if (fornecedores.length > 0) {
        const fornecedoresData = fornecedores.map(f => ({
          cnpj_fornecedor: f.cnpj_fornecedor,
          razao_social: f.razao_social || '',
          valor_total_homologado: this.converterParaNumero(f.valor_total_homologado)
        }));
        const wsFornecedores = XLSX.utils.json_to_sheet(fornecedoresData);
        this.aplicarFormatacaoCelulas(wsFornecedores, ['valor_total_homologado'], []);
        XLSX.utils.book_append_sheet(wb, wsFornecedores, 'fornecedores');
      }

      // Sheet 5: Inexigibilidade (filtro dos itens)
      const inexigibilidadeData = itensMerge.filter(item => {
        const compra = compras.find(c => 
          c.ano_compra === item.ano_compra && 
          c.sequencial_compra === item.sequencial_compra
        );
        return compra?.modalidade?.nome === 'Inexigibilidade';
      });

      if (inexigibilidadeData.length > 0) {
        const inexData = inexigibilidadeData.map(i => ({
          ano_compra: i.ano_compra,
          sequencial_compra: i.sequencial_compra,
          numero_item: i.numero_item,
          cnpj_fornecedor: i.cnpj_fornecedor || '',
          razao_social: i.razao_social || '',
          descricao: i.descricao,
          quantidade: this.converterParaNumero(i.quantidade),
          valor_total_estimado: this.converterParaNumero(i.valor_total_estimado),
          valor_total_homologado: this.converterParaNumero(i.valor_total_homologado),
          percentual_desconto: this.converterPercentual(i.percentual_desconto)
        }));
        const wsInex = XLSX.utils.json_to_sheet(inexData);
        this.aplicarFormatacaoCelulas(wsInex, ['valor_total_estimado', 'valor_total_homologado'], ['percentual_desconto']);
        XLSX.utils.book_append_sheet(wb, wsInex, 'inexigibilidade');
      }

      // Sheets por modalidade (exceto Inexigibilidade)
      const modalidadesUnicas = [...new Set(
        compras
          .map(c => c.modalidade?.nome)
          .filter((nome): nome is string => !!nome)
      )];
      
      for (const modalidadeNome of modalidadesUnicas) {
        if (!modalidadeNome || modalidadeNome.toLowerCase() === 'inexigibilidade') {
          continue;
        }

        const modalidadeData = itensMerge.filter(item => {
          const compra = compras.find(c => 
            c.ano_compra === item.ano_compra && 
            c.sequencial_compra === item.sequencial_compra
          );
          return compra?.modalidade?.nome === modalidadeNome;
        });

        if (modalidadeData.length > 0) {
          const modData = modalidadeData.map(i => ({
            ano_compra: i.ano_compra,
            sequencial_compra: i.sequencial_compra,
            numero_item: i.numero_item,
            cnpj_fornecedor: i.cnpj_fornecedor || '',
            razao_social: i.razao_social || '',
            descricao: i.descricao,
            quantidade: this.converterParaNumero(i.quantidade),
            valor_total_estimado: this.converterParaNumero(i.valor_total_estimado),
            valor_total_homologado: this.converterParaNumero(i.valor_total_homologado),
            percentual_desconto: this.converterPercentual(i.percentual_desconto)
          }));
          
          // Limita o nome da sheet a 31 caracteres (limite do Excel)
          const sheetName = this.limitarNomeSheet(modalidadeNome);
          const wsMod = XLSX.utils.json_to_sheet(modData);
          this.aplicarFormatacaoCelulas(wsMod, ['valor_total_estimado', 'valor_total_homologado'], ['percentual_desconto']);
          XLSX.utils.book_append_sheet(wb, wsMod, sheetName);
        }
      }

      // Gerar arquivo e fazer download
      XLSX.writeFile(wb, `compras_${codigo}.xlsx`);
      
      this.loading.set(false);
      this.snackBar.open('Arquivo XLSX exportado com sucesso!', 'Fechar', { duration: 3000 });
    } catch (error) {
      console.error('Erro ao exportar XLSX:', error);
      this.snackBar.open('Erro ao exportar arquivo XLSX', 'Fechar', { duration: 5000 });
      this.loading.set(false);
    }
  }

  private limitarNomeSheet(nome: string): string {
    // Limita a 31 caracteres (limite do Excel) e remove caracteres inválidos
    return nome
      .replace(/[\\\/\?\*\[\]:]/g, '') // Remove caracteres inválidos
      .substring(0, 31);
  }

  /**
   * Converte string para número, retornando null se inválido
   */
  private converterParaNumero(valor: string | number | null | undefined): number | null {
    if (valor === null || valor === undefined || valor === '') return null;
    if (typeof valor === 'number') return valor;
    const num = parseFloat(String(valor).replace(',', '.'));
    return isNaN(num) ? null : num;
  }

  /**
   * Converte percentual para número decimal (ex: "5.5" -> 5.5 ou "5,5" -> 5.5)
   */
  private converterPercentual(valor: string | number | null | undefined): number | null {
    if (valor === null || valor === undefined || valor === '') return null;
    if (typeof valor === 'number') return valor;
    const num = parseFloat(String(valor).replace(',', '.'));
    return isNaN(num) ? null : num;
  }

  /**
   * Aplica formatação de células numéricas e percentuais no Excel
   * Nota: A biblioteca xlsx básica não suporta formatação completa, mas os valores
   * serão salvos como números, permitindo formatação manual no Excel
   */
  private aplicarFormatacaoCelulas(ws: XLSX.WorkSheet, colunasMonetarias: string[], colunasPercentuais: string[]): void {
    // Os valores já estão como números, o Excel detectará automaticamente
    // A formatação visual pode ser aplicada manualmente no Excel ou usando bibliotecas avançadas
    // Por enquanto, apenas garantimos que os valores sejam numéricos
  }

  formatarMoeda(valor: string | null): string {
    if (!valor) return '-';
    const num = parseFloat(valor);
    return new Intl.NumberFormat('pt-BR', { 
      style: 'currency', 
      currency: 'BRL' 
    }).format(num);
  }

  formatarPercentual(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') return '-';
    const num = typeof valor === 'string' ? parseFloat(valor) : valor;
    if (isNaN(num)) return '-';
    return `${num.toFixed(2)}%`;
  }

  abrirLinkPncp(ano: number, sequencial: number): void {
    const url = `https://pncp.gov.br/app/editais/00394502000144/${ano}/${sequencial}`;
    window.open(url, '_blank');
  }

  private buscarPorTexto(valor: string): void {
    const texto = valor.trim();
    if (!texto) {
      this.snackBar.open('Informe o código da unidade', 'Fechar', { duration: 3000 });
      return;
    }

    const textoNormalizado = texto.toLowerCase();
    const unidade = this.unidadesDisponiveis().find((item) => {
      const codigo = item.codigo_unidade.toLowerCase();
      const sigla = (item.sigla_om ?? '').toLowerCase();
      return codigo === textoNormalizado || sigla === textoNormalizado;
    });

    if (unidade) {
      this.onUnidadeSelected(unidade);
      return;
    }

    this._codigoUnidade.set(texto);
    this.filtroUnidade.set(texto);
    this.codigoUnidadeSelecionado.set(texto);
    this.carregarDados();
  }
}
