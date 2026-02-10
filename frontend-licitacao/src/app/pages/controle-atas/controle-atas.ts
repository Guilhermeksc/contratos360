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
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { firstValueFrom } from 'rxjs';
import * as XLSX from 'xlsx';
import { AtaService } from '../../services/ata.service';
import {
  Ata,
  AnosUnidadesComboAta,
  UnidadeComSiglaAta,
  AtasPorUnidadeAnoResponse
} from '../../interfaces/ata.interface';
import { Combobox } from '../../components/combobox/combobox';
import { FiltroBusca } from '../../components/filtro-busca/filtro-busca';
import { PageHeaderComponent } from '../../components/page-header/page-header.component';

@Component({
  selector: 'app-controle-atas',
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
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTooltipModule,
    Combobox,
    FiltroBusca,
    PageHeaderComponent
  ],
  templateUrl: './controle-atas.html',
  styleUrl: './controle-atas.scss',
})
export class ControleAtas implements OnInit {
  // Estados de carregamento
  loading = signal<boolean>(false);
  loadingCombo = signal<boolean>(false);
  loadingListagem = signal<boolean>(false);

  // Dados do combobox
  anosDisponiveis = signal<number[]>([]);
  unidadesPorAno = signal<{ [ano: string]: UnidadeComSiglaAta[] }>({});
  anoSelecionado = signal<number | null>(null);
  codigoUnidadeSelecionado = signal<string | null>(null);
  unidadesDoAno = signal<UnidadeComSiglaAta[]>([]);
  unidadesFiltradas = signal<UnidadeComSiglaAta[]>([]);
  filtroUnidade = signal<string>('');

  // Dados de atas
  atasListagem = signal<Ata[]>([]);
  atasListagemFiltradas = signal<Ata[]>([]);
  countAtas = signal<number>(0);

  // Colunas da tabela
  displayedColumns: string[] = [
    'codigo_unidade_orgao',
    'numero_ata_registro_preco',
    'numero_compra',
    'ano',
    'sequencial',
    'objeto_contratacao',
    'vigencia_inicio',
    'vigencia_fim',
    'acoes'
  ];

  // Chaves para localStorage
  private readonly STORAGE_KEY_ANO = 'controle_atas_ano_selecionado';
  private readonly STORAGE_KEY_UASG = 'controle_atas_uasg_selecionada';
  
  // Flag para controlar se estamos carregando do cache
  private carregandoDoCache: boolean = false;

  constructor(
    private ataService: AtaService,
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
      const dados = await firstValueFrom(this.ataService.getAnosUnidadesCombo());
      this.anosDisponiveis.set(dados.anos);
      // Garante que todas as unidades tenham sigla_om
      const unidadesPorAnoProcessadas: { [ano: string]: UnidadeComSiglaAta[] } = {};
      Object.keys(dados.unidades_por_ano).forEach(ano => {
        unidadesPorAnoProcessadas[ano] = dados.unidades_por_ano[ano].map(u => ({
          codigo_unidade_orgao: u.codigo_unidade_orgao,
          sigla_om: u.sigla_om ?? null
        }));
      });
      this.unidadesPorAno.set(unidadesPorAnoProcessadas);
      
      if (dados.anos.length > 0) {
        // Tenta carregar do cache primeiro
        const anoCache = this.carregarAnoDoCache();
        const uasgCache = this.carregarUasgDoCache();
        let anoParaSelecionar: number;
        
        // Verifica se o ano do cache está disponível
        if (anoCache && dados.anos.includes(anoCache)) {
          anoParaSelecionar = anoCache;
          this.carregandoDoCache = true;
        } else {
          // Seleciona o ano atual se disponível, caso contrário o maior ano disponível
          const anoAtual = new Date().getFullYear();
          if (dados.anos.includes(anoAtual)) {
            anoParaSelecionar = anoAtual;
          } else {
            anoParaSelecionar = dados.anos[0];
          }
          this.carregandoDoCache = false;
        }
        
        // Carrega o ano (isso já preserva a unidade se ela existir no novo ano)
        await this.onAnoChange(anoParaSelecionar);
        
        // Após carregar as unidades do ano, sempre tenta carregar a UASG do cache
        // Isso garante que mesmo se o ano não veio do cache, ainda tenta carregar a unidade
        if (uasgCache) {
          const unidades = this.unidadesDoAno();
          const unidadeEncontrada = unidades.find(u => u.codigo_unidade_orgao === uasgCache);
          const codigoAtual = this.codigoUnidadeSelecionado();
          
          if (unidadeEncontrada && codigoAtual !== uasgCache) {
            // Se encontrou a unidade no ano selecionado e não é a mesma já selecionada, seleciona automaticamente
            await this.onUnidadeChange(unidadeEncontrada.codigo_unidade_orgao);
          } else if (!unidadeEncontrada) {
            // Se a unidade não existe no ano selecionado, limpa o cache apenas se não estava carregando do cache
            if (!this.carregandoDoCache) {
              this.salvarUasgNoCache(null);
            }
          }
        }
        
        this.carregandoDoCache = false;
      } else {
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
  async onAnoChange(ano: number | null): Promise<void> {
    // Valida se o ano é válido
    if (ano === null || ano === undefined || isNaN(Number(ano))) {
      return;
    }
    
    const codigoAnterior = this.codigoUnidadeSelecionado();
    this.anoSelecionado.set(ano);
    this.salvarAnoNoCache(ano);
    
    const unidades = this.unidadesPorAno()[ano.toString()] || [];
    // Garante que todas as unidades tenham sigla_om (mesmo que null)
    const unidadesComSigla = unidades.map(u => ({
      codigo_unidade_orgao: u.codigo_unidade_orgao,
      sigla_om: u.sigla_om ?? null
    }));
    this.unidadesDoAno.set(unidadesComSigla);
    
    // Limpa seleções anteriores de atas
    this.atasListagem.set([]);
    this.atasListagemFiltradas.set([]);

    // Verifica se o código anterior existe no novo ano
    const unidadeAindaExiste = !!codigoAnterior && unidadesComSigla.some(
      u => u.codigo_unidade_orgao === codigoAnterior
    );

    if (unidadeAindaExiste) {
      // Preserva a seleção e atualiza o filtro
      this.codigoUnidadeSelecionado.set(codigoAnterior);
      this.salvarUasgNoCache(codigoAnterior);
      const unidadePreservada = unidadesComSigla.find(u => u.codigo_unidade_orgao === codigoAnterior);
      if (unidadePreservada) {
        this.filtroUnidade.set(this.getUnidadeDisplayText(unidadePreservada));
      }
      // Aplica o filtro e carrega as atas
      this.aplicarFiltroUnidade();
      await this.carregarListagemAtas(codigoAnterior, ano);
    } else {
      // Se o código não existe no novo ano, verifica se há cache para tentar carregar
      if (this.carregandoDoCache) {
        const uasgCache = this.carregarUasgDoCache();
        if (uasgCache) {
          const unidadeDoCache = unidadesComSigla.find(u => u.codigo_unidade_orgao === uasgCache);
          if (unidadeDoCache) {
            // Se encontrou a unidade do cache no novo ano, seleciona
            this.codigoUnidadeSelecionado.set(uasgCache);
            this.filtroUnidade.set(this.getUnidadeDisplayText(unidadeDoCache));
            this.aplicarFiltroUnidade();
            await this.carregarListagemAtas(uasgCache, ano);
            return;
          }
        }
      }
      // Se não encontrou no cache ou não está carregando do cache, limpa a seleção
      this.codigoUnidadeSelecionado.set(null);
      this.filtroUnidade.set('');
      if (!this.carregandoDoCache) {
        this.salvarUasgNoCache(null);
      }
      // Aplica o filtro vazio para mostrar todas as unidades
      this.aplicarFiltroUnidade();
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
        u => u.codigo_unidade_orgao === codigoSelecionado
      );
      if (!aindaExiste) {
        this.codigoUnidadeSelecionado.set(null);
        this.atasListagem.set([]);
        this.atasListagemFiltradas.set([]);
      }
    }
  }

  /**
   * Quando uma opção é selecionada no dropdown do filtro de busca
   */
  async onUnidadeSelected(unidade: UnidadeComSiglaAta): Promise<void> {
    await this.onUnidadeChange(unidade.codigo_unidade_orgao);
    this.filtroUnidade.set(this.getUnidadeDisplayText(unidade));
  }

  /**
   * Quando Enter é pressionado no filtro de busca
   */
  async onFiltroUnidadeEnter(filtro: string): Promise<void> {
    if (!filtro || !filtro.trim()) {
      return;
    }

    const filtroLower = filtro.toLowerCase().trim();
    const unidadesFiltradas = this.unidadesFiltradas();
    
    // Busca por correspondência exata primeiro (código UASG, sigla_om ou código)
    let unidadeEncontrada = unidadesFiltradas.find(unidade => {
      const codigoExato = unidade.codigo_unidade_orgao.toLowerCase() === filtroLower;
      const codigoNumerico = unidade.codigo_unidade_orgao === filtro.trim();
      const siglaExata = unidade.sigla_om?.toLowerCase() === filtroLower;
      return codigoExato || codigoNumerico || siglaExata;
    });

    // Se não encontrou correspondência exata, busca por correspondência parcial única
    if (!unidadeEncontrada && unidadesFiltradas.length === 1) {
      unidadeEncontrada = unidadesFiltradas[0];
    }

    if (unidadeEncontrada) {
      await this.onUnidadeChange(unidadeEncontrada.codigo_unidade_orgao);
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
      // Busca parcial no código da unidade (UASG)
      const codigo = unidade.codigo_unidade_orgao?.toLowerCase() || '';
      const codigoMatch = codigo.includes(filtro);
      
      // Busca parcial na sigla OM
      const sigla = unidade.sigla_om?.toLowerCase() || '';
      const siglaMatch = sigla.includes(filtro);
      
      // Busca exata por código numérico (sem conversão para lowercase)
      const uasgExatoMatch = unidade.codigo_unidade_orgao === filtro.trim();
      
      // Busca exata por sigla OM (case insensitive)
      const siglaExataMatch = sigla === filtro;
      
      // Busca também pelo texto de exibição completo (para compatibilidade com FiltroBusca)
      const displayText = this.getUnidadeDisplayText(unidade).toLowerCase();
      const displayMatch = displayText.includes(filtro);
      
      return codigoMatch || siglaMatch || uasgExatoMatch || siglaExataMatch || displayMatch;
    });
    
    this.unidadesFiltradas.set(filtradas);
  }

  /**
   * Quando a unidade é alterada, carrega as atas do ano selecionado
   */
  async onUnidadeChange(codigoUnidade: string): Promise<void> {
    this.codigoUnidadeSelecionado.set(codigoUnidade);
    this.salvarUasgNoCache(codigoUnidade);
    
    const ano = this.anoSelecionado();
    if (ano) {
      await this.carregarListagemAtas(codigoUnidade, ano);
    }
  }

  /**
   * Carrega a listagem de atas para a unidade e ano selecionados
   */
  async carregarListagemAtas(codigoUnidade: string, ano: number | null): Promise<void> {
    // Valida se o ano é válido
    if (!ano || isNaN(Number(ano))) {
      this.loadingListagem.set(false);
      return;
    }
    
    this.loadingListagem.set(true);
    try {
      // Busca as atas da unidade usando o endpoint específico
      const response = await firstValueFrom(
        this.ataService.getAtasPorUnidadeAno(codigoUnidade, ano)
      );
      
      // Busca as atas completas da unidade para obter todos os campos
      const atasUnidade = await firstValueFrom(
        this.ataService.getAtasPorUnidade(codigoUnidade)
      );
      
      // Cria um mapa de atas completas por numero_controle_pncp_ata
      const atasMap = new Map<string, Ata>();
      atasUnidade.forEach((ata) => {
        if (ata.numero_controle_pncp_ata && ata.ano === ano) {
          atasMap.set(ata.numero_controle_pncp_ata, ata);
        }
      });
      
      // Monta a lista de atas com dados completos
      const atasCompletas: Ata[] = response.atas.map((ataResumo) => {
        const ataCompleta = atasMap.get(ataResumo.numero_controle_pncp_ata);
        if (ataCompleta) {
          // Usa os dados completos e atualiza com os dados do resumo
          return {
            ...ataCompleta,
            vigencia_inicio: ataResumo.vigencia_inicio,
            vigencia_fim: ataResumo.vigencia_fim,
            data_assinatura: ataResumo.data_assinatura,
            cancelado: ataResumo.cancelado,
            objeto_contratacao: ataResumo.objeto_contratacao,
            cnpj_orgao: ataResumo.cnpj_orgao || ataCompleta.cnpj_orgao || '',
            sequencial: ataResumo.sequencial || ataCompleta.sequencial || '',
            numero_compra: ataResumo.numero_compra || ataCompleta.numero_compra || '',
            ano: ataResumo.ano || ataCompleta.ano || response.ano
          };
        } else {
          // Se não encontrar completa, cria com os dados disponíveis
          return {
            numero_controle_pncp_ata: ataResumo.numero_controle_pncp_ata,
            numero_ata_registro_preco: ataResumo.numero_ata_registro_preco,
            ano_ata: ataResumo.ano_ata,
            numero_controle_pncp_compra: '',
            cancelado: ataResumo.cancelado,
            data_cancelamento: null,
            data_assinatura: ataResumo.data_assinatura,
            vigencia_inicio: ataResumo.vigencia_inicio,
            vigencia_fim: ataResumo.vigencia_fim,
            data_publicacao_pncp: null,
            data_inclusao: null,
            data_atualizacao: null,
            data_atualizacao_global: null,
            usuario: '',
            objeto_contratacao: ataResumo.objeto_contratacao,
            cnpj_orgao: ataResumo.cnpj_orgao || '',
            nome_orgao: '',
            cnpj_orgao_subrogado: null,
            nome_orgao_subrogado: null,
            codigo_unidade_orgao: response.codigo_unidade_orgao,
            nome_unidade_orgao: '',
            codigo_unidade_orgao_subrogado: null,
            nome_unidade_orgao_subrogado: null,
            sequencial: ataResumo.sequencial || '',
            ano: ataResumo.ano || response.ano,
            numero_compra: ataResumo.numero_compra || ''
          } as Ata;
        }
      });

      this.atasListagem.set(atasCompletas);
      this.atasListagemFiltradas.set(atasCompletas);
      this.countAtas.set(response.total_atas);
    } catch (error) {
      console.error('Erro ao carregar listagem de atas:', error);
      this.snackBar.open('Erro ao carregar atas', 'Fechar', {
        duration: 5000
      });
      this.atasListagem.set([]);
      this.atasListagemFiltradas.set([]);
      this.countAtas.set(0);
    } finally {
      this.loadingListagem.set(false);
    }
  }

  /**
   * Retorna o texto de exibição da unidade
   */
  getUnidadeDisplayText(unidade: UnidadeComSiglaAta): string {
    const partes: string[] = [unidade.codigo_unidade_orgao];
    
    if (unidade.sigla_om) {
      partes.push(unidade.sigla_om);
    }
    
    return partes.join(' - ');
  }

  /**
   * Retorna o texto da UASG selecionada
   */
  getUasgSelecionadaTexto(): string {
    const codigo = this.codigoUnidadeSelecionado();
    if (!codigo) return '';
    
    const unidades = this.unidadesDoAno();
    const unidade = unidades.find(u => u.codigo_unidade_orgao === codigo);
    if (unidade) {
      return this.getUnidadeDisplayText(unidade);
    }
    return codigo;
  }

  /**
   * Retorna o título da tabela de atas
   */
  getTituloAtas(): string {
    const count = this.countAtas();
    const unidade = this.getUasgSelecionadaTexto();
    if (count === 0) {
      return 'Nenhuma ata encontrada';
    }
    return `${count} ata(s) encontrada(s)${unidade ? ` para ${unidade}` : ''}`;
  }

  /**
   * Formata uma data
   */
  formatarData(data: string | null): string {
    if (!data) return 'N/A';
    try {
      const date = new Date(data);
      return date.toLocaleDateString('pt-BR');
    } catch {
      return 'N/A';
    }
  }

  /**
   * Gera o link do PNCP para download do arquivo da ata
   */
  getLinkDownloadPncp(ata: Ata): string | null {
    // Verifica se tem os dados necessários: cnpj_orgao, ano e sequencial
    if (!ata.cnpj_orgao || !ata.ano || !ata.sequencial) {
      return null;
    }

    // Remove caracteres não numéricos do CNPJ
    const cnpj = ata.cnpj_orgao.replace(/\D/g, '');
    
    // Converte sequencial para número se for string
    let sequencial: number;
    if (typeof ata.sequencial === 'string') {
      sequencial = parseInt(ata.sequencial.trim(), 10);
    } else {
      sequencial = Number(ata.sequencial);
    }
    
    // Valida os dados
    if (!cnpj || cnpj.length < 14 || isNaN(sequencial) || sequencial <= 0 || !ata.ano || ata.ano <= 0) {
      return null;
    }

    // Monta o link: pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/atas/1/arquivos/1
    return `https://pncp.gov.br/api/pncp/v1/orgaos/${cnpj}/compras/${ata.ano}/${sequencial}/atas/1/arquivos/1`;
  }

  /**
   * Abre o link de download em nova aba
   */
  abrirLinkDownload(ata: Ata): void {
    const link = this.getLinkDownloadPncp(ata);
    if (link) {
      window.open(link, '_blank');
    } else {
      this.snackBar.open('Dados insuficientes para gerar o link de download', 'Fechar', {
        duration: 3000
      });
    }
  }

  /**
   * Gera o link da contratação no PNCP
   */
  getLinkContratacaoPncp(ata: Ata): string | null {
    // Verifica se tem os dados necessários: cnpj_orgao, ano e sequencial
    if (!ata.cnpj_orgao || !ata.ano || !ata.sequencial) {
      return null;
    }

    // Remove caracteres não numéricos do CNPJ
    const cnpj = ata.cnpj_orgao.replace(/\D/g, '');
    
    // Converte sequencial para número se for string
    let sequencial: number;
    if (typeof ata.sequencial === 'string') {
      sequencial = parseInt(ata.sequencial.trim(), 10);
    } else {
      sequencial = Number(ata.sequencial);
    }
    
    // Valida os dados
    if (!cnpj || cnpj.length < 14 || isNaN(sequencial) || sequencial <= 0 || !ata.ano || ata.ano <= 0) {
      return null;
    }

    // Monta o link: pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}
    return `https://pncp.gov.br/app/editais/${cnpj}/${ata.ano}/${sequencial}`;
  }

  /**
   * Abre o link da contratação em nova aba
   */
  abrirLinkContratacao(ata: Ata): void {
    const link = this.getLinkContratacaoPncp(ata);
    if (link) {
      window.open(link, '_blank');
    } else {
      this.snackBar.open('Dados insuficientes para gerar o link da contratação', 'Fechar', {
        duration: 3000
      });
    }
  }

  /**
   * Formata o número da ata de registro de preço com o ano
   */
  getNumeroAtaFormatado(ata: Ata): string {
    if (!ata.numero_ata_registro_preco) {
      return 'N/A';
    }
    const anoAta = ata.ano_ata || ata.ano;
    if (anoAta) {
      return `${ata.numero_ata_registro_preco}/${anoAta}`;
    }
    return ata.numero_ata_registro_preco;
  }

  /**
   * Formata o número da compra com o ano
   */
  getNumeroCompraFormatado(ata: Ata): string {
    if (!ata.numero_compra) {
      return 'N/A';
    }
    const ano = ata.ano || ata.ano_ata;
    if (ano) {
      return `${ata.numero_compra}/${ano}`;
    }
    return ata.numero_compra;
  }

  /**
   * Exporta as atas filtradas para XLSX
   */
  exportarAtasXlsx(): void {
    const atas = this.atasListagemFiltradas();
    if (atas.length === 0) {
      this.snackBar.open('Nenhuma ata para exportar', 'Fechar', {
        duration: 3000
      });
      return;
    }

    const data = atas.map(ata => ({
      'Código da Unidade': ata.codigo_unidade_orgao || 'N/A',
      'Número da Ata': this.getNumeroAtaFormatado(ata),
      'Número da Compra': this.getNumeroCompraFormatado(ata),
      'Ano': ata.ano || ata.ano_ata || 'N/A',
      'Sequencial': ata.sequencial || 'N/A',
      'Objeto da Contratação': ata.objeto_contratacao || 'N/A',
      'Vigência Início': this.formatarData(ata.vigencia_inicio),
      'Vigência Fim': this.formatarData(ata.vigencia_fim),
      'Data de Assinatura': this.formatarData(ata.data_assinatura),
      'Cancelado': ata.cancelado === 1 ? 'Sim' : 'Não',
      'CNPJ do Órgão': ata.cnpj_orgao || 'N/A',
      'Nome do Órgão': ata.nome_orgao || 'N/A',
      'Nome da Unidade': ata.nome_unidade_orgao || 'N/A'
    }));

    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Atas');
    
    const dataAtual = new Date().toISOString().slice(0, 10);
    const unidade = this.getUasgSelecionadaTexto();
    const nomeArquivo = unidade 
      ? `Atas_${unidade.replace(/[^a-zA-Z0-9]/g, '_')}_${dataAtual}.xlsx`
      : `Atas_${dataAtual}.xlsx`;
    
    XLSX.writeFile(wb, nomeArquivo);
  }
}
