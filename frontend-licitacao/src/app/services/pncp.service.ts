import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { 
  Compra, 
  ItemResultadoMerge, 
  ModalidadeAgregada, 
  FornecedorAgregado,
  CompraDetalhada,
  CompraListagem,
  ListagemComprasResponse,
  AnosUnidadesCombo,
  UnidadePorAno
} from '../interfaces/pncp.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class PncpService {
  private apiUrl = `${environment.apiUrl}/pncp`;
  private readonly CACHE_TTL_MS = 2 * 60 * 60 * 1000;

  constructor(private http: HttpClient) {}

  private buildCacheKey(path: string, params?: HttpParams): string {
    const query = params?.toString();
    return `pncp_cache|${path}${query ? `?${query}` : ''}`;
  }

  private getCached<T>(key: string): T | null {
    const raw = localStorage.getItem(key);
    if (!raw) {
      return null;
    }
    try {
      const parsed = JSON.parse(raw) as { timestamp: number; data: T };
      if (!parsed?.timestamp || Date.now() - parsed.timestamp > this.CACHE_TTL_MS) {
        localStorage.removeItem(key);
        return null;
      }
      return parsed.data;
    } catch {
      localStorage.removeItem(key);
      return null;
    }
  }

  private setCached<T>(key: string, data: T): void {
    localStorage.setItem(key, JSON.stringify({ timestamp: Date.now(), data }));
  }

  private withCache<T>(key: string, request$: Observable<T>): Observable<T> {
    const cached = this.getCached<T>(key);
    if (cached !== null) {
      return of(cached);
    }
    return request$.pipe(tap((data) => this.setCached(key, data)));
  }

  /**
   * Obtém compras por código de unidade
   */
  getComprasPorUnidade(codigoUnidade: string): Observable<Compra[]> {
    const url = `${this.apiUrl}/compras/por-unidade/${codigoUnidade}/`;
    return this.withCache(this.buildCacheKey(url), this.http.get<Compra[]>(url));
  }

  /**
   * Obtém itens com resultado merge por código de unidade
   */
  getItensResultadoMerge(codigoUnidade: string): Observable<ItemResultadoMerge[]> {
    const url = `${this.apiUrl}/compras/itens-resultado-merge/${codigoUnidade}/`;
    return this.withCache(this.buildCacheKey(url), this.http.get<ItemResultadoMerge[]>(url));
  }

  /**
   * Obtém modalidades agregadas por código de unidade
   */
  getModalidadesAgregadas(codigoUnidade: string): Observable<ModalidadeAgregada[]> {
    const url = `${this.apiUrl}/compras/modalidades-agregadas/${codigoUnidade}/`;
    return this.withCache(this.buildCacheKey(url), this.http.get<ModalidadeAgregada[]>(url));
  }

  /**
   * Obtém modalidades agregadas por ano (todas as UASG)
   */
  getModalidadesAgregadasAno(anoCompra: number): Observable<ModalidadeAgregada[]> {
    const params = new HttpParams().set('ano_compra', anoCompra.toString());
    const url = `${this.apiUrl}/compras/modalidades-agregadas-ano/`;
    return this.withCache(
      this.buildCacheKey(url, params),
      this.http.get<ModalidadeAgregada[]>(url, { params })
    );
  }

  /**
   * Obtém fornecedores agregados por código de unidade
   */
  getFornecedoresAgregados(codigoUnidade: string): Observable<FornecedorAgregado[]> {
    const url = `${this.apiUrl}/compras/fornecedores-agregados/${codigoUnidade}/`;
    return this.withCache(this.buildCacheKey(url), this.http.get<FornecedorAgregado[]>(url));
  }

  /**
   * Obtém itens por modalidade
   */
  getItensPorModalidade(codigoUnidade: string, modalidadeId?: number): Observable<ItemResultadoMerge[]> {
    let url = `${this.apiUrl}/compras/itens-por-modalidade/${codigoUnidade}/`;
    if (modalidadeId) {
      url += `?modalidade_id=${modalidadeId}`;
    }
    return this.withCache(this.buildCacheKey(url), this.http.get<ItemResultadoMerge[]>(url));
  }

  /**
   * Obtém compra detalhada por codigo_unidade, numero_compra, ano_compra e modalidade
   */
  getCompraDetalhada(
    codigoUnidade: string,
    numeroCompra: string,
    anoCompra: number,
    modalidade: number
  ): Observable<CompraDetalhada> {
    const params = new HttpParams()
      .set('codigo_unidade', codigoUnidade)
      .set('numero_compra', numeroCompra)
      .set('ano_compra', anoCompra.toString())
      .set('modalidade', modalidade.toString());

    const url = `${this.apiUrl}/compras/detalhada/`;
    return this.withCache(this.buildCacheKey(url, params), this.http.get<CompraDetalhada>(url, { params }));
  }

  /**
   * Obtém listagem de compras por codigo_unidade e ano_compra
   */
  getComprasListagem(codigoUnidade: string, anoCompra: number): Observable<ListagemComprasResponse> {
    const params = new HttpParams()
      .set('codigo_unidade', codigoUnidade)
      .set('ano_compra', anoCompra.toString());

    const url = `${this.apiUrl}/compras/listagem/`;
    return this.withCache(this.buildCacheKey(url, params), this.http.get<ListagemComprasResponse>(url, { params }));
  }

  /**
   * Obtém unidades por ano com informações agregadas
   */
  getUnidadesPorAno(anoCompra: number): Observable<UnidadePorAno[]> {
    const params = new HttpParams().set('ano_compra', anoCompra.toString());
    const url = `${this.apiUrl}/unidades/por-ano/`;
    return this.withCache(
      this.buildCacheKey(url, params),
      this.http.get<{ ano_compra: number; count: number; results: UnidadePorAno[] }>(url, { params })
    ).pipe(map(response => response.results));
  }

  /**
   * Obtém anos e unidades para combobox
   */
  getAnosUnidadesCombo(): Observable<AnosUnidadesCombo> {
    const url = `${this.apiUrl}/combo/anos-unidades/`;
    return this.withCache(this.buildCacheKey(url), this.http.get<AnosUnidadesCombo>(url));
  }
}
