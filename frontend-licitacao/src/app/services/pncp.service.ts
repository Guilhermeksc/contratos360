import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
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

  constructor(private http: HttpClient) {}

  /**
   * Obtém compras por código de unidade
   */
  getComprasPorUnidade(codigoUnidade: string): Observable<Compra[]> {
    return this.http.get<Compra[]>(`${this.apiUrl}/compras/por-unidade/${codigoUnidade}/`);
  }

  /**
   * Obtém itens com resultado merge por código de unidade
   */
  getItensResultadoMerge(codigoUnidade: string): Observable<ItemResultadoMerge[]> {
    return this.http.get<ItemResultadoMerge[]>(`${this.apiUrl}/compras/itens-resultado-merge/${codigoUnidade}/`);
  }

  /**
   * Obtém modalidades agregadas por código de unidade
   */
  getModalidadesAgregadas(codigoUnidade: string): Observable<ModalidadeAgregada[]> {
    return this.http.get<ModalidadeAgregada[]>(`${this.apiUrl}/compras/modalidades-agregadas/${codigoUnidade}/`);
  }

  /**
   * Obtém fornecedores agregados por código de unidade
   */
  getFornecedoresAgregados(codigoUnidade: string): Observable<FornecedorAgregado[]> {
    return this.http.get<FornecedorAgregado[]>(`${this.apiUrl}/compras/fornecedores-agregados/${codigoUnidade}/`);
  }

  /**
   * Obtém itens por modalidade
   */
  getItensPorModalidade(codigoUnidade: string, modalidadeId?: number): Observable<ItemResultadoMerge[]> {
    let url = `${this.apiUrl}/compras/itens-por-modalidade/${codigoUnidade}/`;
    if (modalidadeId) {
      url += `?modalidade_id=${modalidadeId}`;
    }
    return this.http.get<ItemResultadoMerge[]>(url);
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
    
    return this.http.get<CompraDetalhada>(`${this.apiUrl}/compras/detalhada/`, { params });
  }

  /**
   * Obtém listagem de compras por codigo_unidade e ano_compra
   */
  getComprasListagem(codigoUnidade: string, anoCompra: number): Observable<ListagemComprasResponse> {
    const params = new HttpParams()
      .set('codigo_unidade', codigoUnidade)
      .set('ano_compra', anoCompra.toString());
    
    return this.http.get<ListagemComprasResponse>(`${this.apiUrl}/compras/listagem/`, { params });
  }

  /**
   * Obtém unidades por ano com informações agregadas
   */
  getUnidadesPorAno(anoCompra: number): Observable<UnidadePorAno[]> {
    const params = new HttpParams().set('ano_compra', anoCompra.toString());
    return this.http.get<{ ano_compra: number; count: number; results: UnidadePorAno[] }>(
      `${this.apiUrl}/unidades/por-ano/`,
      { params }
    ).pipe(
      map(response => response.results)
    );
  }

  /**
   * Obtém anos e unidades para combobox
   */
  getAnosUnidadesCombo(): Observable<AnosUnidadesCombo> {
    return this.http.get<AnosUnidadesCombo>(`${this.apiUrl}/combo/anos-unidades/`);
  }
}
