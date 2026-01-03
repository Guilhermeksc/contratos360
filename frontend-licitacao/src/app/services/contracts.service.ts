import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Contrato, ContratoDetail, ContratoCreate } from '../interfaces/contrato.interface';
import { environment } from '../environments/environment';

export interface ContratoFilters {
  uasg?: string;
  status?: string;
  manual?: boolean;
  vigencia_fim__gte?: string;
  vigencia_fim__lte?: string;
  fornecedor_cnpj?: string;
  search?: string;
  ordering?: string;
  page?: number;
}

@Injectable({ providedIn: 'root' })
export class ContractsService {
  private apiUrl = `${environment.apiUrl}/contratos`;

  constructor(private http: HttpClient) {}

  list(filters?: ContratoFilters): Observable<{ count: number; results: Contrato[]; next: string | null; previous: string | null }> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        const value = filters[key as keyof ContratoFilters];
        if (value !== undefined && value !== null) {
          params = params.set(key, value.toString());
        }
      });
    }
    return this.http.get<{ count: number; results: Contrato[]; next: string | null; previous: string | null }>(this.apiUrl, { params });
  }

  get(id: string): Observable<Contrato> {
    return this.http.get<Contrato>(`${this.apiUrl}/${id}/`);
  }

  getDetails(id: string): Observable<ContratoDetail> {
    return this.http.get<ContratoDetail>(`${this.apiUrl}/${id}/detalhes/`);
  }

  create(data: ContratoCreate): Observable<Contrato> {
    return this.http.post<Contrato>(this.apiUrl, data);
  }

  update(id: string, data: Partial<Contrato>): Observable<Contrato> {
    return this.http.put<Contrato>(`${this.apiUrl}/${id}/`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  // Endpoints especiais
  getVencidos(): Observable<Contrato[]> {
    return this.http.get<any>(`${this.apiUrl}/vencidos/`).pipe(
      map((response: any) => {
        // Garante que sempre retorne um array
        if (Array.isArray(response)) {
          return response;
        }
        // Se for um objeto paginado, extrai os resultados
        if (response && Array.isArray(response.results)) {
          return response.results;
        }
        return [];
      })
    );
  }

  getProximosVencer(): Observable<Contrato[]> {
    return this.http.get<any>(`${this.apiUrl}/proximos_vencer/`).pipe(
      map((response: any) => {
        // Garante que sempre retorne um array
        if (Array.isArray(response)) {
          return response;
        }
        // Se for um objeto paginado, extrai os resultados
        if (response && Array.isArray(response.results)) {
          return response.results;
        }
        return [];
      })
    );
  }

  getAtivos(): Observable<Contrato[]> {
    return this.http.get<any>(`${this.apiUrl}/ativos/`).pipe(
      map((response: any) => {
        // Garante que sempre retorne um array
        if (Array.isArray(response)) {
          return response;
        }
        // Se for um objeto paginado, extrai os resultados
        if (response && Array.isArray(response.results)) {
          return response.results;
        }
        // Se for um objeto único, retorna array vazio (não deveria acontecer)
        console.warn('ContractsService.getAtivos: Resposta não é um array:', response);
        return [];
      })
    );
  }

  // Sincronização
  syncUasg(uasgCode: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/sync/`, null, {
      params: new HttpParams().set('uasg', uasgCode)
    });
  }
}

