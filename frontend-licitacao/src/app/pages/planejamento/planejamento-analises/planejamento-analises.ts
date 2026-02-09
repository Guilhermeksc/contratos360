import { Component, OnInit, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { firstValueFrom } from 'rxjs';
import { PncpService } from '../../../services/pncp.service';
import { Combobox } from '../../../components/combobox/combobox';
import { FiltroBusca } from '../../../components/filtro-busca/filtro-busca';
import { AnosUnidadesCombo, ModalidadeAgregada, UnidadeComSigla } from '../../../interfaces/pncp.interface';

interface PieItem {
  label: string;
  value: number;
  color: string;
}

interface PieSlice extends PieItem {
  path: string;
  percentage: number;
  isFullCircle: boolean;
}

@Component({
  selector: 'app-planejamento-analises',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    Combobox,
    FiltroBusca
  ],
  templateUrl: './planejamento-analises.html',
  styleUrl: './planejamento-analises.scss',
})
export class PlanejamentoAnalises implements OnInit {
  private readonly ALL_UASG_CODE = '__ALL__';
  loadingCombo = signal<boolean>(false);
  loadingChart = signal<boolean>(false);

  anosDisponiveis = signal<number[]>([]);
  unidadesPorAno = signal<{ [ano: string]: UnidadeComSigla[] }>({});
  anoSelecionado = signal<number | null>(null);
  codigoUnidadeSelecionado = signal<string | null>(null);
  unidadesDoAno = signal<UnidadeComSigla[]>([]);
  filtroUnidade = signal<string>('');

  readonly unidadesDoAnoComTodas = computed<UnidadeComSigla[]>(() => {
    if (!this.anoSelecionado()) {
      return [];
    }
    return [
      { codigo_unidade: this.ALL_UASG_CODE, sigla_om: 'Todas as UASG' },
      ...this.unidadesDoAno()
    ];
  });

  modalidadesAgregadas = signal<ModalidadeAgregada[]>([]);

  private readonly STORAGE_KEY_ANO = 'planejamento_analises_ano_selecionado';
  private readonly STORAGE_KEY_UASG = 'planejamento_analises_uasg_selecionada';

  private readonly pieColors: string[] = [
    '#4f8ef7',
    '#7bc96f',
    '#f4b942',
    '#ef5350',
    '#ab47bc',
    '#26a69a',
    '#5c6bc0',
    '#ec407a',
    '#78909c',
    '#ff7043'
  ];

  readonly chartItems = computed(() => this.buildChartItems());
  readonly pieSlices = computed(() => this.buildPieSlices(this.chartItems()));
  readonly totalQuantidade = computed(() =>
    this.chartItems().reduce((total, item) => total + item.value, 0)
  );

  constructor(
    private pncpService: PncpService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.carregarAnosUnidades();
  }

  async carregarAnosUnidades(): Promise<void> {
    this.loadingCombo.set(true);
    try {
      const dados: AnosUnidadesCombo = await firstValueFrom(this.pncpService.getAnosUnidadesCombo());
      this.anosDisponiveis.set(dados.anos);
      this.unidadesPorAno.set(dados.unidades_por_ano);

      if (dados.anos.length > 0) {
        const anoCache = this.carregarAnoDoCache();
        const anoAtual = new Date().getFullYear();
        const anoParaSelecionar =
          anoCache && dados.anos.includes(anoCache)
            ? anoCache
            : dados.anos.includes(anoAtual)
              ? anoAtual
              : dados.anos[0];

        this.onAnoChange(anoParaSelecionar);

        const uasgCache = this.carregarUasgDoCache();
        if (uasgCache) {
          if (uasgCache === this.ALL_UASG_CODE) {
            this.onUnidadeSelected({ codigo_unidade: this.ALL_UASG_CODE, sigla_om: 'Todas as UASG' });
          } else {
            const unidade = this.unidadesDoAno().find((u) => u.codigo_unidade === uasgCache);
            if (unidade) {
              this.onUnidadeSelected(unidade);
            }
          }
        }
      }
    } catch (error) {
      console.error('Erro ao carregar anos e unidades:', error);
      this.snackBar.open('Erro ao carregar anos e unidades disponíveis', 'Fechar', {
        duration: 5000
      });
    } finally {
      this.loadingCombo.set(false);
    }
  }

  onAnoChange(ano: number | null): void {
    this.anoSelecionado.set(ano);
    this.salvarAnoNoCache(ano);

    if (!ano) {
      this.unidadesDoAno.set([]);
      this.codigoUnidadeSelecionado.set(null);
      this.salvarUasgNoCache(null);
      this.modalidadesAgregadas.set([]);
      return;
    }

    const unidadesDoAno = this.unidadesPorAno()[String(ano)] ?? [];
    this.unidadesDoAno.set(unidadesDoAno);

    const codigoAtual = this.codigoUnidadeSelecionado();
    if (codigoAtual) {
      if (codigoAtual === this.ALL_UASG_CODE) {
        this.filtroUnidade.set('Todas as UASG');
        this.carregarModalidadesAgregadas();
        return;
      }

      const unidadeEncontrada = unidadesDoAno.find((u) => u.codigo_unidade === codigoAtual);
      if (!unidadeEncontrada) {
        this.codigoUnidadeSelecionado.set(null);
        this.salvarUasgNoCache(null);
        this.modalidadesAgregadas.set([]);
        this.filtroUnidade.set('');
      } else {
        this.filtroUnidade.set(this.getUnidadeDisplayText(unidadeEncontrada));
        this.carregarModalidadesAgregadas();
      }
    }
  }

  onFiltroUnidadeChange(valor: string): void {
    this.filtroUnidade.set(valor);
  }

  onFiltroUnidadeEnter(valor: string): void {
    const texto = valor.trim().toLowerCase();
    if (texto === 'todas' || texto === 'todas as uasg') {
      this.onUnidadeSelected({ codigo_unidade: this.ALL_UASG_CODE, sigla_om: 'Todas as UASG' });
      return;
    }
    const unidade = this.unidadesDoAno().find((u) => {
      const codigo = u.codigo_unidade.toLowerCase();
      const sigla = (u.sigla_om ?? '').toLowerCase();
      return codigo === texto || sigla === texto;
    });

    if (unidade) {
      this.onUnidadeSelected(unidade);
    }
  }

  onUnidadeSelected(unidade: UnidadeComSigla): void {
    if (unidade.codigo_unidade === this.ALL_UASG_CODE) {
      this.codigoUnidadeSelecionado.set(this.ALL_UASG_CODE);
      this.salvarUasgNoCache(this.ALL_UASG_CODE);
      this.filtroUnidade.set('Todas as UASG');
      this.carregarModalidadesAgregadas();
      return;
    }
    this.codigoUnidadeSelecionado.set(unidade.codigo_unidade);
    this.salvarUasgNoCache(unidade.codigo_unidade);
    this.filtroUnidade.set(this.getUnidadeDisplayText(unidade));
    this.carregarModalidadesAgregadas();
  }

  getUnidadeDisplayText(unidade: UnidadeComSigla): string {
    if (unidade.codigo_unidade === this.ALL_UASG_CODE) {
      return 'Todas as UASG';
    }
    const sigla = unidade.sigla_om ? ` - ${unidade.sigla_om}` : '';
    return `${unidade.codigo_unidade}${sigla}`;
  }

  getUasgSelecionadaTexto(): string {
    const codigo = this.codigoUnidadeSelecionado();
    if (!codigo) {
      return '';
    }
    if (codigo === this.ALL_UASG_CODE) {
      return 'Todas as UASG';
    }
    const unidade = this.unidadesDoAno().find((u) => u.codigo_unidade === codigo);
    return unidade ? this.getUnidadeDisplayText(unidade) : codigo;
  }

  getTituloGrafico(): string {
    return this.anoSelecionado() ? `Modalidades por ano (${this.anoSelecionado()})` : 'Modalidades por ano';
  }

  formatPercentual(valor: number): string {
    return `${valor.toFixed(1).replace('.', ',')}%`;
  }

  private async carregarModalidadesAgregadas(): Promise<void> {
    const codigoUnidade = this.codigoUnidadeSelecionado();
    if (!codigoUnidade) {
      this.modalidadesAgregadas.set([]);
      return;
    }

    if (codigoUnidade === this.ALL_UASG_CODE) {
      await this.carregarModalidadesAgregadasTodasUasg();
      return;
    }

    this.loadingChart.set(true);
    try {
      const dados = await firstValueFrom(this.pncpService.getModalidadesAgregadas(codigoUnidade));
      this.modalidadesAgregadas.set(dados);
    } catch (error) {
      console.error('Erro ao carregar modalidades agregadas:', error);
      this.snackBar.open('Erro ao carregar modalidades para a UASG selecionada', 'Fechar', {
        duration: 5000
      });
      this.modalidadesAgregadas.set([]);
    } finally {
      this.loadingChart.set(false);
    }
  }

  private async carregarModalidadesAgregadasTodasUasg(): Promise<void> {
    const ano = this.anoSelecionado();
    if (!ano) {
      this.modalidadesAgregadas.set([]);
      return;
    }

    this.loadingChart.set(true);
    try {
      const dados = await firstValueFrom(this.pncpService.getModalidadesAgregadasAno(ano));
      this.modalidadesAgregadas.set(dados);
    } catch (error) {
      console.error('Erro ao carregar modalidades agregadas (todas UASG):', error);
      this.snackBar.open('Erro ao carregar modalidades para todas as UASG', 'Fechar', {
        duration: 5000
      });
      this.modalidadesAgregadas.set([]);
    } finally {
      this.loadingChart.set(false);
    }
  }

  private buildChartItems(): PieItem[] {
    const ano = this.anoSelecionado();
    if (!ano) {
      return [];
    }

    const items = this.modalidadesAgregadas()
      .filter((modalidade) => modalidade.ano_compra === ano)
      .map((modalidade) => ({
        label: this.getModalidadeLabel(modalidade),
        value: modalidade.quantidade_compras || 0
      }))
      .filter((item) => item.value > 0)
      .sort((a, b) => b.value - a.value)
      .map((item, index) => ({
        ...item,
        color: this.pieColors[index % this.pieColors.length]
      }));

    return items;
  }

  private getModalidadeLabel(modalidade: ModalidadeAgregada): string {
    if (modalidade.modalidade?.nome) {
      return modalidade.modalidade.nome;
    }
    if (modalidade.modalidade_id !== null && modalidade.modalidade_id !== undefined) {
      return `Modalidade ${modalidade.modalidade_id}`;
    }
    return 'Sem modalidade';
  }

  private buildPieSlices(items: PieItem[]): PieSlice[] {
    if (!items.length) {
      return [];
    }

    const total = items.reduce((sum, item) => sum + item.value, 0);
    if (total <= 0) {
      return [];
    }

    if (items.length === 1) {
      const item = items[0];
      return [
        {
          ...item,
          path: '',
          percentage: 100,
          isFullCircle: true
        }
      ];
    }

    const center = 50;
    const radius = 45;
    let startAngle = 0;

    return items.map((item) => {
      const angle = (item.value / total) * 360;
      const endAngle = startAngle + angle;
      const path = this.describeArc(center, center, radius, startAngle, endAngle);
      const slice: PieSlice = {
        ...item,
        path,
        percentage: (item.value / total) * 100,
        isFullCircle: false
      };
      startAngle = endAngle;
      return slice;
    });
  }

  private describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number): string {
    const start = this.polarToCartesian(cx, cy, r, endAngle);
    const end = this.polarToCartesian(cx, cy, r, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    return [
      'M',
      cx,
      cy,
      'L',
      start.x,
      start.y,
      'A',
      r,
      r,
      0,
      largeArcFlag,
      0,
      end.x,
      end.y,
      'Z'
    ].join(' ');
  }

  private polarToCartesian(cx: number, cy: number, r: number, angleInDegrees: number): { x: number; y: number } {
    const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
    return {
      x: cx + r * Math.cos(angleInRadians),
      y: cy + r * Math.sin(angleInRadians)
    };
  }

  private salvarAnoNoCache(ano: number | null): void {
    if (ano !== null) {
      localStorage.setItem(this.STORAGE_KEY_ANO, String(ano));
    } else {
      localStorage.removeItem(this.STORAGE_KEY_ANO);
    }
  }

  private salvarUasgNoCache(codigoUnidade: string | null): void {
    if (codigoUnidade) {
      localStorage.setItem(this.STORAGE_KEY_UASG, codigoUnidade);
    } else {
      localStorage.removeItem(this.STORAGE_KEY_UASG);
    }
  }

  private carregarAnoDoCache(): number | null {
    const anoSalvo = localStorage.getItem(this.STORAGE_KEY_ANO);
    if (anoSalvo) {
      const ano = parseInt(anoSalvo, 10);
      return isNaN(ano) ? null : ano;
    }
    return null;
  }

  private carregarUasgDoCache(): string | null {
    return localStorage.getItem(this.STORAGE_KEY_UASG);
  }
}
