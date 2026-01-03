import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ItemContrato } from '../interfaces/offline.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class ItensService {
  private apiUrl = `${environment.apiUrl}/itens`;

  constructor(private http: HttpClient) {}

  list(contratoId: string): Observable<ItemContrato[]> {
    return this.http.get<ItemContrato[]>(this.apiUrl, {
      params: new HttpParams().set('contrato', contratoId)
    });
  }

  generateReport(contratoId: string): Observable<Blob> {
    // Endpoint a ser criado: GET /api/contratos/itens/report/?contrato={id}
    return this.http.get(`${this.apiUrl}/report/`, {
      params: new HttpParams().set('contrato', contratoId),
      responseType: 'blob'
    });
  }
}

