import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { EmpresaSancionada, EmpresasSancionadasListResponse, EmpresasSancionadasFilters } from '../interfaces/empresas-sancionadas.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class EmpresasSancionadasService {
  private apiUrl = `${environment.apiUrl}/empresas-sancionadas`;

  constructor(private http: HttpClient) {}

  /**
   * Lista todas as empresas sancionadas
   */
  list(filters?: EmpresasSancionadasFilters): Observable<EmpresasSancionadasListResponse | EmpresaSancionada[]> {
    let params = new HttpParams();
    
    if (filters) {
      Object.keys(filters).forEach(key => {
        const value = filters[key as keyof EmpresasSancionadasFilters];
        if (value !== undefined && value !== null && value !== '') {
          params = params.set(key, value.toString());
        }
      });
    }

    return this.http.get<any>(this.apiUrl, { params }).pipe(
      map((response: any) => {
        // Se for um objeto paginado, retorna como está
        if (response && (response.results || response.count !== undefined)) {
          return response;
        }
        // Se for um array direto, retorna como array
        if (Array.isArray(response)) {
          return response;
        }
        return [];
      })
    );
  }

  /**
   * Busca uma empresa sancionada específica por ID
   */
  get(id: number): Observable<EmpresaSancionada> {
    return this.http.get<EmpresaSancionada>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Busca empresas sancionadas por CPF/CNPJ
   */
  getByCpfCnpj(cpfCnpj: string): Observable<EmpresaSancionada[]> {
    return this.list({ cpf_cnpj: cpfCnpj }).pipe(
      map((response: any) => {
        if (Array.isArray(response)) {
          return response;
        }
        if (response && Array.isArray(response.results)) {
          return response.results;
        }
        return [];
      })
    );
  }

  /**
   * Busca empresas sancionadas ativas (com data_final_sancao no futuro ou nula)
   */
  getAtivas(): Observable<EmpresaSancionada[]> {
    const hoje = new Date().toISOString().split('T')[0];
    // Filtra empresas com data_final_sancao >= hoje ou sem data_final_sancao
    return this.list({ ordering: '-data_inicio_sancao' }).pipe(
      map((response: any) => {
        let empresas: EmpresaSancionada[] = [];
        
        if (Array.isArray(response)) {
          empresas = response;
        } else if (response && Array.isArray(response.results)) {
          empresas = response.results;
        }
        
        // Filtra no cliente empresas com data_final_sancao >= hoje ou nula
        return empresas.filter(empresa => {
          if (!empresa.data_final_sancao) return true;
          return empresa.data_final_sancao >= hoje;
        });
      })
    );
  }
}

