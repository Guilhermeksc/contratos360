import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatExpansionModule } from '@angular/material/expansion';
import { firstValueFrom } from 'rxjs';
import { PncpService } from '../../services/pncp.service';
import jsPDF from 'jspdf';
import {
  CompraDetalhada,
  CompraListagem,
  AnosUnidadesCombo,
  UnidadeComSigla,
  Modalidade
} from '../../interfaces/pncp.interface';
import { Combobox } from '../../components/combobox/combobox';
import { FiltroBusca } from '../../components/filtro-busca/filtro-busca';

@Component({
  selector: 'app-planejamento',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatTableModule,
    MatTabsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatExpansionModule,
    Combobox,
    FiltroBusca
  ],
  templateUrl: './planejamento.component.html',
  styleUrl: './planejamento.component.scss'
})
export class PlanejamentoComponent implements OnInit {
  // Estados de carregamento
  loading = signal<boolean>(false);
  loadingCombo = signal<boolean>(false);
  loadingDetalhada = signal<boolean>(false);
  loadingListagem = signal<boolean>(false);

  // Dados do combobox
  anosDisponiveis = signal<number[]>([]);
  unidadesPorAno = signal<{ [ano: string]: UnidadeComSigla[] }>({});
  anoSelecionado = signal<number | null>(null);
  codigoUnidadeSelecionado = signal<string | null>(null);
  unidadesDoAno = signal<UnidadeComSigla[]>([]);
  unidadesFiltradas = signal<UnidadeComSigla[]>([]);
  filtroUnidade = signal<string>('');

  // Dados de modalidades
  modalidadesDisponiveis = signal<Modalidade[]>([]);
  modalidadeSelecionada = signal<number | null>(null);

  // Dados de compras
  compraDetalhada = signal<CompraDetalhada | null>(null);
  comprasListagem = signal<CompraListagem[]>([]);
  comprasListagemFiltradas = signal<CompraListagem[]>([]);
  countCompras = signal<number>(0);
  
  // Estado de visualização
  visualizacaoAtual = signal<'listagem' | 'detalhada'>('listagem');
  compraSelecionadaParaDetalhes = signal<CompraListagem | null>(null);

  // Formulário para compra detalhada
  numeroCompra = signal<string>('');
  modalidadeId = signal<number | null>(null);

  // Colunas das tabelas
  displayedColumnsListagem: string[] = [
    'numero_compra',
    'sequencial_compra',
    'modalidade',
    'objeto_compra',
    'valor_total_estimado',
    'valor_total_homologado',
    'percentual_desconto',
    'acoes'
  ];

  displayedColumnsItens: string[] = [
    'numero_item',
    'descricao',
    'quantidade',
    'unidade_medida',
    'valor_total_estimado',
    'valor_total_homologado',
    'situacao'
  ];

  displayedColumnsResultados: string[] = [
    'fornecedor',
    'quantidade_homologada',
    'valor_unitario_homologado',
    'valor_total_homologado'
  ];

  // Chaves para localStorage
  private readonly STORAGE_KEY_ANO = 'planejamento_ano_selecionado';
  private readonly STORAGE_KEY_UASG = 'planejamento_uasg_selecionada';
  
  // Flag para controlar se estamos carregando do cache (evita limpar cache durante carregamento inicial)
  private carregandoDoCache: boolean = false;

  constructor(
    private pncpService: PncpService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.carregarAnosUnidades();
  }

  /**
   * Salva o ano selecionado no localStorage
   */
  private salvarAnoNoCache(ano: number | null): void {
    if (ano !== null) {
      localStorage.setItem(this.STORAGE_KEY_ANO, String(ano));
    } else {
      localStorage.removeItem(this.STORAGE_KEY_ANO);
    }
  }

  /**
   * Salva a UASG selecionada no localStorage
   */
  private salvarUasgNoCache(codigoUnidade: string | null): void {
    if (codigoUnidade) {
      localStorage.setItem(this.STORAGE_KEY_UASG, codigoUnidade);
    } else {
      localStorage.removeItem(this.STORAGE_KEY_UASG);
    }
  }

  /**
   * Carrega o ano salvo do localStorage
   */
  private carregarAnoDoCache(): number | null {
    const anoSalvo = localStorage.getItem(this.STORAGE_KEY_ANO);
    if (anoSalvo) {
      const ano = parseInt(anoSalvo, 10);
      return isNaN(ano) ? null : ano;
    }
    return null;
  }

  /**
   * Carrega a UASG salva do localStorage
   */
  private carregarUasgDoCache(): string | null {
    return localStorage.getItem(this.STORAGE_KEY_UASG);
  }

  /**
   * Carrega anos e unidades disponíveis para os comboboxes
   */
  async carregarAnosUnidades(): Promise<void> {
    this.loadingCombo.set(true);
    try {
      const dados = await firstValueFrom(this.pncpService.getAnosUnidadesCombo());
      this.anosDisponiveis.set(dados.anos);
      this.unidadesPorAno.set(dados.unidades_por_ano);
      
      if (dados.anos.length > 0) {
        // Tenta carregar do cache primeiro
        const anoCache = this.carregarAnoDoCache();
        let anoParaSelecionar: number;
        
        // Verifica se o ano do cache está disponível
        if (anoCache && dados.anos.includes(anoCache)) {
          anoParaSelecionar = anoCache;
          this.carregandoDoCache = true; // Marca que estamos carregando do cache
        } else {
          // Se não houver cache ou o ano do cache não estiver disponível,
          // seleciona o ano atual se disponível, caso contrário o maior ano disponível
          const anoAtual = new Date().getFullYear();
          if (dados.anos.includes(anoAtual)) {
            anoParaSelecionar = anoAtual;
          } else {
            anoParaSelecionar = dados.anos[0];
          }
          this.carregandoDoCache = false;
        }
        
        await this.onAnoChange(anoParaSelecionar);
        
        // Após carregar as unidades do ano, tenta carregar a UASG do cache
        if (this.carregandoDoCache) {
          const uasgCache = this.carregarUasgDoCache();
          if (uasgCache) {
            const unidades = this.unidadesDoAno();
            const unidadeEncontrada = unidades.find(u => u.codigo_unidade === uasgCache);
            
            if (unidadeEncontrada) {
              // A unidade do cache existe no ano selecionado, seleciona automaticamente
              await this.onUnidadeChange(unidadeEncontrada.codigo_unidade);
            } else {
              // A unidade do cache não existe mais no ano selecionado, remove do cache
              this.salvarUasgNoCache(null);
            }
          }
          this.carregandoDoCache = false; // Reseta a flag após carregar
        }
      } else {
        // Inicializa unidades filtradas vazias se não houver anos
        this.unidadesFiltradas.set([]);
      }
    } catch (error) {
      console.error('Erro ao carregar anos e unidades:', error);
      this.snackBar.open('Erro ao carregar anos e unidades disponíveis', 'Fechar', {
        duration: 5000
      });
      this.unidadesFiltradas.set([]);
    } finally {
      this.loadingCombo.set(false);
    }
  }

  /**
   * Quando o ano é alterado, atualiza as unidades disponíveis
   */
  async onAnoChange(ano: number): Promise<void> {
    this.anoSelecionado.set(ano);
    // Salva no cache
    this.salvarAnoNoCache(ano);
    
    const unidades = this.unidadesPorAno()[ano.toString()] || [];
    this.unidadesDoAno.set(unidades);
    
    // Aplica o filtro se houver
    this.aplicarFiltroUnidade();
    
    // Limpa seleções anteriores
    this.codigoUnidadeSelecionado.set(null);
    this.comprasListagem.set([]);
    this.comprasListagemFiltradas.set([]);
    this.compraDetalhada.set(null);
    this.modalidadeSelecionada.set(null);
    this.modalidadesDisponiveis.set([]);
    this.visualizacaoAtual.set('listagem');
    this.compraSelecionadaParaDetalhes.set(null);
    
    // Limpa a UASG do cache quando o ano muda manualmente (não durante carregamento inicial)
    if (!this.carregandoDoCache) {
      this.salvarUasgNoCache(null);
    }
  }

  /**
   * Quando o filtro de unidade é alterado
   */
  onFiltroUnidadeChange(filtro: string): void {
    this.filtroUnidade.set(filtro);
    this.aplicarFiltroUnidade();
    
    // Se a unidade selecionada não estiver mais na lista filtrada, limpa a seleção
    const codigoSelecionado = this.codigoUnidadeSelecionado();
    if (codigoSelecionado) {
      const aindaExiste = this.unidadesFiltradas().some(
        u => u.codigo_unidade === codigoSelecionado
      );
      if (!aindaExiste) {
        this.codigoUnidadeSelecionado.set(null);
        this.comprasListagem.set([]);
      }
    }
  }

  /**
   * Quando uma opção é selecionada no dropdown do filtro de busca
   */
  async onUnidadeSelected(unidade: UnidadeComSigla): Promise<void> {
    await this.onUnidadeChange(unidade.codigo_unidade);
    // Limpa o filtro após selecionar
    this.filtroUnidade.set('');
    this.aplicarFiltroUnidade();
  }

  /**
   * Quando Enter é pressionado no filtro de busca, tenta selecionar a unidade automaticamente
   */
  async onFiltroUnidadeEnter(filtro: string): Promise<void> {
    if (!filtro || !filtro.trim()) {
      return;
    }

    const filtroLower = filtro.toLowerCase().trim();
    const unidadesFiltradas = this.unidadesFiltradas();
    
    // Busca por correspondência exata primeiro (código ou sigla)
    let unidadeEncontrada = unidadesFiltradas.find(unidade => {
      const codigoMatch = unidade.codigo_unidade.toLowerCase() === filtroLower;
      const siglaMatch = unidade.sigla_om?.toLowerCase() === filtroLower;
      return codigoMatch || siglaMatch;
    });

    // Se não encontrou correspondência exata, busca por correspondência parcial única
    if (!unidadeEncontrada && unidadesFiltradas.length === 1) {
      unidadeEncontrada = unidadesFiltradas[0];
    }

    if (unidadeEncontrada) {
      // Seleciona a unidade encontrada
      await this.onUnidadeChange(unidadeEncontrada.codigo_unidade);
      // Limpa o filtro após selecionar
      this.filtroUnidade.set('');
      this.aplicarFiltroUnidade();
    } else if (unidadesFiltradas.length === 0) {
      this.snackBar.open('Nenhuma unidade encontrada para "' + filtro + '"', 'Fechar', {
        duration: 3000
      });
    } else if (unidadesFiltradas.length > 1) {
      this.snackBar.open(
        `Múltiplas unidades encontradas (${unidadesFiltradas.length}). Selecione uma no combobox.`,
        'Fechar',
        { duration: 4000 }
      );
    }
  }

  /**
   * Aplica o filtro de busca nas unidades
   */
  aplicarFiltroUnidade(): void {
    const filtro = this.filtroUnidade().toLowerCase().trim();
    const unidades = this.unidadesDoAno();
    
    if (!filtro) {
      this.unidadesFiltradas.set(unidades);
      return;
    }
    
    const filtradas = unidades.filter(unidade => {
      const codigoMatch = unidade.codigo_unidade.toLowerCase().includes(filtro);
      const siglaMatch = unidade.sigla_om?.toLowerCase().includes(filtro) || false;
      return codigoMatch || siglaMatch;
    });
    
    this.unidadesFiltradas.set(filtradas);
  }

  /**
   * Quando a unidade é alterada, carrega as compras do ano selecionado
   */
  async onUnidadeChange(codigoUnidade: string): Promise<void> {
    this.codigoUnidadeSelecionado.set(codigoUnidade);
    // Salva no cache
    this.salvarUasgNoCache(codigoUnidade);
    
    // Limpa a seleção de modalidade quando a unidade muda
    this.modalidadeSelecionada.set(null);
    
    const ano = this.anoSelecionado();
    
    if (!ano) {
      this.snackBar.open('Selecione um ano primeiro', 'Fechar', { duration: 3000 });
      return;
    }

    await this.carregarListagemCompras(codigoUnidade, ano);
  }

  /**
   * Carrega a listagem de compras por unidade e ano
   */
  async carregarListagemCompras(codigoUnidade: string, ano: number): Promise<void> {
    this.loadingListagem.set(true);
    try {
      const response = await firstValueFrom(
        this.pncpService.getComprasListagem(codigoUnidade, ano)
      );
      const compras = response.results || [];
      this.comprasListagem.set(compras);
      this.countCompras.set(response.count || 0);
      
      // Extrai modalidades únicas das compras carregadas
      this.extrairModalidades(compras);
      
      // Aplica filtro de modalidade se houver
      this.aplicarFiltroModalidade();
    } catch (error) {
      console.error('Erro ao carregar listagem de compras:', error);
      this.snackBar.open('Erro ao carregar compras', 'Fechar', { duration: 5000 });
      this.comprasListagem.set([]);
      this.comprasListagemFiltradas.set([]);
      this.countCompras.set(0);
      this.modalidadesDisponiveis.set([]);
    } finally {
      this.loadingListagem.set(false);
    }
  }

  /**
   * Extrai modalidades únicas das compras carregadas
   */
  private extrairModalidades(compras: CompraListagem[]): void {
    const modalidadesMap = new Map<number, Modalidade>();
    
    compras.forEach(compra => {
      if (compra.modalidade && compra.modalidade.id) {
        if (!modalidadesMap.has(compra.modalidade.id)) {
          modalidadesMap.set(compra.modalidade.id, compra.modalidade);
        }
      }
    });
    
    // Converte para array e ordena por nome
    const modalidades = Array.from(modalidadesMap.values()).sort((a, b) => 
      a.nome.localeCompare(b.nome)
    );
    
    this.modalidadesDisponiveis.set(modalidades);
  }

  /**
   * Aplica filtro de modalidade nas compras
   */
  private aplicarFiltroModalidade(): void {
    const modalidadeId = this.modalidadeSelecionada();
    const compras = this.comprasListagem();
    
    if (!modalidadeId) {
      // Se não houver modalidade selecionada, mostra todas as compras
      this.comprasListagemFiltradas.set(compras);
      this.countCompras.set(compras.length);
    } else {
      // Filtra compras pela modalidade selecionada
      const filtradas = compras.filter(compra => 
        compra.modalidade?.id === modalidadeId
      );
      this.comprasListagemFiltradas.set(filtradas);
      this.countCompras.set(filtradas.length);
    }
  }

  /**
   * Quando a modalidade é alterada, filtra as compras
   */
  onModalidadeChange(modalidadeId: number | null): void {
    this.modalidadeSelecionada.set(modalidadeId);
    this.aplicarFiltroModalidade();
  }

  /**
   * Abre os detalhes de uma compra da listagem
   */
  async abrirDetalhesCompra(compra: CompraListagem): Promise<void> {
    this.compraSelecionadaParaDetalhes.set(compra);
    await this.carregarCompraDetalhada(
      compra.codigo_unidade,
      compra.numero_compra,
      compra.ano_compra,
      compra.modalidade?.id || null
    );
    this.visualizacaoAtual.set('detalhada');
  }

  /**
   * Volta para a listagem de compras
   */
  voltarParaListagem(): void {
    this.visualizacaoAtual.set('listagem');
    this.compraDetalhada.set(null);
    this.compraSelecionadaParaDetalhes.set(null);
  }

  /**
   * Carrega compra detalhada
   */
  async carregarCompraDetalhada(
    codigoUnidade?: string,
    numeroCompra?: string,
    ano?: number,
    modalidadeId?: number | null
  ): Promise<void> {
    const codigoUnidadeParam = codigoUnidade || this.codigoUnidadeSelecionado();
    const numeroCompraParam = numeroCompra || this.numeroCompra();
    const anoParam = ano || this.anoSelecionado();
    const modalidadeParam = modalidadeId !== undefined ? modalidadeId : this.modalidadeId();

    if (!codigoUnidadeParam || !numeroCompraParam || !anoParam || !modalidadeParam) {
      this.snackBar.open('Dados insuficientes para carregar compra detalhada', 'Fechar', {
        duration: 3000
      });
      return;
    }

    this.loadingDetalhada.set(true);
    try {
      const compra = await firstValueFrom(
        this.pncpService.getCompraDetalhada(
          codigoUnidadeParam,
          numeroCompraParam,
          anoParam,
          modalidadeParam
        )
      );
      this.compraDetalhada.set(compra);
    } catch (error: any) {
      console.error('Erro ao carregar compra detalhada:', error);
      const mensagem = error?.error?.error || 'Erro ao carregar compra detalhada';
      this.snackBar.open(mensagem, 'Fechar', { duration: 5000 });
      this.compraDetalhada.set(null);
    } finally {
      this.loadingDetalhada.set(false);
    }
  }

  /**
   * Formata valor monetário
   */
  formatarValor(valor: string | null | undefined): string {
    if (!valor) return '-';
    const num = parseFloat(valor);
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(num);
  }

  /**
   * Formata percentual
   */
  formatarPercentual(valor: string | null | undefined): string {
    if (!valor) return '-';
    const num = parseFloat(valor);
    return `${num.toFixed(2)}%`;
  }

  /**
   * Formata data
   */
  formatarData(data: string | null | undefined): string {
    if (!data) return '-';
    try {
      const date = new Date(data);
      return date.toLocaleDateString('pt-BR');
    } catch {
      return data;
    }
  }

  /**
   * Obtém nome da modalidade ou exibe "N/A"
   */
  getNomeModalidade(compra: CompraListagem): string {
    return compra.modalidade?.nome || 'N/A';
  }

  /**
   * Obtém display text para unidade no combobox
   */
  getUnidadeDisplayText(unidade: UnidadeComSigla): string {
    if (unidade.sigla_om) {
      return `${unidade.codigo_unidade} - ${unidade.sigla_om}`;
    }
    return unidade.codigo_unidade;
  }

  /**
   * Obtém display text para modalidade no combobox
   */
  getModalidadeDisplayText(modalidade: Modalidade): string {
    return modalidade.nome;
  }

  /**
   * Obtém a unidade selecionada completa (com sigla)
   */
  getUnidadeSelecionada(): UnidadeComSigla | null {
    const codigoUnidade = this.codigoUnidadeSelecionado();
    if (!codigoUnidade) {
      return null;
    }
    
    const unidades = this.unidadesDoAno();
    return unidades.find(u => u.codigo_unidade === codigoUnidade) || null;
  }

  /**
   * Obtém o texto da UASG selecionada para exibição
   */
  getUasgSelecionadaTexto(): string {
    const unidade = this.getUnidadeSelecionada();
    if (!unidade) {
      return '';
    }
    
    if (unidade.sigla_om) {
      return `${unidade.codigo_unidade} - ${unidade.sigla_om}`;
    }
    return unidade.codigo_unidade;
  }

  /**
   * Gera relatório em PDF da compra detalhada
   * @param compraListagem Opcional: compra da listagem para gerar relatório diretamente
   */
  async gerarRelatorioPDF(compraListagem?: CompraListagem): Promise<void> {
    let compra: CompraDetalhada | null = null;
    let compraSelecionada: CompraListagem | null = null;

    // Se uma compra da listagem foi fornecida, carregar seus detalhes
    if (compraListagem) {
      compraSelecionada = compraListagem;
      
      // Verifica se a modalidade está disponível
      if (!compraListagem.modalidade?.id) {
        this.snackBar.open('Modalidade não disponível para esta compra', 'Fechar', {
          duration: 3000
        });
        return;
      }
      
      try {
        this.loadingDetalhada.set(true);
        compra = await firstValueFrom(
          this.pncpService.getCompraDetalhada(
            compraListagem.codigo_unidade,
            compraListagem.numero_compra,
            compraListagem.ano_compra,
            compraListagem.modalidade.id
          )
        );
      } catch (error) {
        this.snackBar.open('Erro ao carregar detalhes da compra para o relatório', 'Fechar', {
          duration: 3000
        });
        this.loadingDetalhada.set(false);
        return;
      } finally {
        this.loadingDetalhada.set(false);
      }
    } else {
      // Usar compra já carregada na visualização detalhada
      compra = this.compraDetalhada();
      compraSelecionada = this.compraSelecionadaParaDetalhes();
    }
    
    if (!compra || !compraSelecionada) {
      this.snackBar.open('Não há dados de compra para gerar o relatório', 'Fechar', {
        duration: 3000
      });
      return;
    }

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    const maxWidth = pageWidth - (margin * 2);
    let yPosition = margin;

    // Função para adicionar rodapé em cada página
    const addFooter = (pageNum: number, totalPages: number) => {
      const footerY = pageHeight - 15;
      const dataHora = new Date().toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      doc.setFontSize(9);
      doc.setTextColor(100, 100, 100);
      const footerText = `Relatório gerado pelo Sistema Licitação360 em ${dataHora}`;
      const footerWidth = doc.getTextWidth(footerText);
      doc.text(footerText, (pageWidth - footerWidth) / 2, footerY);
      
      // Número da página
      doc.text(`Página ${pageNum} de ${totalPages}`, pageWidth - margin - 20, footerY);
    };

    let currentPage = 1;
    let totalPages = 1;

    // Função para verificar se precisa de nova página
    const checkNewPage = (requiredSpace: number): boolean => {
      if (yPosition + requiredSpace > pageHeight - 30) {
        addFooter(currentPage, totalPages);
        doc.addPage();
        currentPage++;
        totalPages++;
        yPosition = margin;
        return true;
      }
      return false;
    };

    // Cabeçalho do relatório
    doc.setFillColor(245, 245, 245);
    doc.rect(0, 0, pageWidth, 50, 'F');
    
    doc.setFontSize(18);
    doc.setTextColor(33, 33, 33);
    doc.setFont('helvetica', 'bold');
    doc.text('Relatório de Contratação', margin, 25);
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100, 100, 100);
    doc.text(`UASG: ${this.getUasgSelecionadaTexto()}`, margin, 35);
    doc.text(`Ano: ${this.anoSelecionado()}`, margin + 80, 35);
    
    yPosition = 60;

    // Dados da Contratação
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(33, 33, 33);
    doc.text('Dados da Contratação', margin, yPosition);
    yPosition += 10;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const dadosContratacao = [
      ['Número da Compra:', compraSelecionada.numero_compra],
      ['Sequencial:', compra.sequencial_compra.toString()],
      ['Modalidade:', compraSelecionada.modalidade?.nome || 'N/A'],
      ['Objeto:', compra.objeto_compra],
      ['Amparo Legal:', compra.amparo_legal?.nome || 'N/A'],
      ['Modo de Disputa:', compra.modo_disputa?.nome || 'N/A'],
      ['Data Publicação PNCP:', this.formatarData(compra.data_publicacao_pncp)],
      ['Valor Total Estimado:', this.formatarValor(compra.valor_total_estimado)],
      ['Valor Total Homologado:', this.formatarValor(compra.valor_total_homologado)],
      ['Percentual de Desconto:', this.formatarPercentual(compra.percentual_desconto)]
    ];

    dadosContratacao.forEach(([label, value]) => {
      checkNewPage(8);
      doc.setFont('helvetica', 'bold');
      doc.text(label, margin, yPosition);
      doc.setFont('helvetica', 'normal');
      const lines = doc.splitTextToSize(String(value), maxWidth - 60);
      doc.text(lines, margin + 60, yPosition);
      yPosition += lines.length * 5 + 3;
    });

    yPosition += 5;

    // Itens da Compra
    if (compra.itens && compra.itens.length > 0) {
      checkNewPage(15);
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Itens da Compra', margin, yPosition);
      yPosition += 10;

      compra.itens.forEach((item, index) => {
        checkNewPage(40);
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text(`Item ${item.numero_item}`, margin, yPosition);
        yPosition += 7;

        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        const itemInfo = [
          ['Descrição:', item.descricao],
          ['Quantidade:', `${item.quantidade} ${item.unidade_medida}`],
          ['Valor Total Estimado:', this.formatarValor(item.valor_total_estimado)],
          ['Situação:', item.situacao_compra_item_nome]
        ];

        itemInfo.forEach(([label, value]) => {
          checkNewPage(8);
          doc.setFont('helvetica', 'bold');
          doc.text(label, margin + 5, yPosition);
          doc.setFont('helvetica', 'normal');
          const lines = doc.splitTextToSize(String(value), maxWidth - 70);
          doc.text(lines, margin + 45, yPosition);
          yPosition += lines.length * 5 + 3;
        });

        // Resultados do Item
        if (item.resultados && item.resultados.length > 0) {
          checkNewPage(20);
          yPosition += 3;
          doc.setFontSize(10);
          doc.setFont('helvetica', 'bold');
          doc.text('Resultados:', margin + 5, yPosition);
          yPosition += 7;

          item.resultados.forEach((resultado, resIndex) => {
            checkNewPage(25);
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            const resultadoInfo = [
              ['Fornecedor:', resultado.fornecedor_detalhes.razao_social],
              ['CNPJ:', resultado.fornecedor_detalhes.cnpj_fornecedor],
              ['Quantidade Homologada:', resultado.quantidade_homologada.toString()],
              ['Valor Unitário Homologado:', this.formatarValor(resultado.valor_unitario_homologado)],
              ['Valor Total Homologado:', this.formatarValor(resultado.valor_total_homologado)]
            ];

            resultadoInfo.forEach(([label, value]) => {
              checkNewPage(7);
              doc.setFont('helvetica', 'bold');
              doc.text(label, margin + 10, yPosition);
              doc.setFont('helvetica', 'normal');
              const lines = doc.splitTextToSize(String(value), maxWidth - 80);
              doc.text(lines, margin + 50, yPosition);
              yPosition += lines.length * 5 + 2;
            });

            if (item.resultados && item.resultados.length > 0 && resIndex < item.resultados.length - 1) {
              yPosition += 3;
              doc.setLineWidth(0.1);
              doc.line(margin + 10, yPosition, pageWidth - margin - 10, yPosition);
              yPosition += 5;
            }
          });
        }

        if (index < compra.itens.length - 1) {
          yPosition += 5;
          doc.setLineWidth(0.2);
          doc.line(margin, yPosition, pageWidth - margin, yPosition);
          yPosition += 8;
        }
      });
    }

    // Atualiza rodapé de todas as páginas com o número total correto
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      addFooter(i, totalPages);
    }

    // Salva o PDF
    const nomeArquivo = `Relatorio_Contratacao_${compraSelecionada.numero_compra.replace(/\//g, '_')}_${this.anoSelecionado()}.pdf`;
    doc.save(nomeArquivo);

    this.snackBar.open('Relatório PDF gerado com sucesso', 'Fechar', {
      duration: 3000
    });
  }
}
