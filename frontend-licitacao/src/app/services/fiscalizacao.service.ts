import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { FiscalizacaoContrato } from '../interfaces/fiscalizacao.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class FiscalizacaoService {
  private apiUrl = `${environment.apiUrl}/fiscalizacao`;

  constructor(private http: HttpClient) {}

  get(contratoId: string): Observable<FiscalizacaoContrato | null> {
    return this.http.get<FiscalizacaoContrato[]>(this.apiUrl, {
      params: new HttpParams().set('contrato', contratoId)
    }).pipe(
      map(results => results.length > 0 ? results[0] : null)
    );
  }

  createOrUpdate(data: Partial<FiscalizacaoContrato>): Observable<FiscalizacaoContrato> {
    return this.http.post<FiscalizacaoContrato>(this.apiUrl, data);
  }

  update(id: number, data: Partial<FiscalizacaoContrato>): Observable<FiscalizacaoContrato> {
    return this.http.put<FiscalizacaoContrato>(`${this.apiUrl}/${id}/`, data);
  }
}

