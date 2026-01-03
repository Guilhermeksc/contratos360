import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Empenho } from '../interfaces/offline.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class EmpenhosService {
  private apiUrl = `${environment.apiUrl}/empenhos`;

  constructor(private http: HttpClient) {}

  list(contratoId: string, filters?: { ano?: number }): Observable<Empenho[]> {
    let params = new HttpParams().set('contrato', contratoId);
    if (filters?.ano) {
      params = params.set('data_emissao__year', filters.ano.toString());
    }
    return this.http.get<Empenho[]>(this.apiUrl, { params });
  }

  generateReport(contratoId: string): Observable<Blob> {
    // Endpoint a ser criado: GET /api/contratos/empenhos/report/?contrato={id}
    return this.http.get(`${this.apiUrl}/report/`, {
      params: new HttpParams().set('contrato', contratoId),
      responseType: 'blob'
    });
  }
}

