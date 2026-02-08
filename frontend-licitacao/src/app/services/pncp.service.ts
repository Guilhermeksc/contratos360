import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { 
  Compra, 
  ItemResultadoMerge, 
  ModalidadeAgregada, 
  FornecedorAgregado 
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
}
