import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { StatusContrato, RegistroStatus, RegistroMensagem } from '../interfaces/status.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class StatusService {
  private apiUrl = `${environment.apiUrl}`;

  constructor(private http: HttpClient) {}

  // StatusContrato
  getStatus(contratoId: string, forceRefresh: boolean = false): Observable<StatusContrato | null> {
    let params = new HttpParams().set('contrato', contratoId);
    
    // Adiciona timestamp para evitar cache se forceRefresh for true
    if (forceRefresh) {
      params = params.set('_t', Date.now().toString());
    }
    
    return this.http.get<StatusContrato[]>(`${this.apiUrl}/status/`, {
      params: params
    }).pipe(
      map(results => results.length > 0 ? results[0] : null)
    );
  }

  createOrUpdateStatus(data: Partial<StatusContrato>): Observable<StatusContrato> {
    return this.http.post<StatusContrato>(`${this.apiUrl}/status/`, data);
  }

  updateStatus(contratoId: string, data: Partial<StatusContrato>): Observable<StatusContrato> {
    return this.http.put<StatusContrato>(`${this.apiUrl}/status/${contratoId}/`, data);
  }

  // RegistroStatus
  listRegistrosStatus(contratoId: string): Observable<RegistroStatus[]> {
    return this.http.get<RegistroStatus[]>(`${this.apiUrl}/registros-status/`, {
      params: new HttpParams().set('contrato', contratoId)
    }).pipe(
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

  createRegistroStatus(data: { contrato: string; uasg_code?: string; texto: string }): Observable<RegistroStatus> {
    return this.http.post<RegistroStatus>(`${this.apiUrl}/registros-status/`, data);
  }

  deleteRegistroStatus(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/registros-status/${id}/`);
  }

  // RegistroMensagem
  listRegistrosMensagem(contratoId: string): Observable<RegistroMensagem[]> {
    return this.http.get<RegistroMensagem[]>(`${this.apiUrl}/registros-mensagem/`, {
      params: new HttpParams().set('contrato', contratoId)
    }).pipe(
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

  createRegistroMensagem(data: { contrato: string; texto: string }): Observable<RegistroMensagem> {
    return this.http.post<RegistroMensagem>(`${this.apiUrl}/registros-mensagem/`, data);
  }

  deleteRegistroMensagem(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/registros-mensagem/${id}/`);
  }

  // Import/Export (endpoints a serem criados no backend)
  exportStatus(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/status/export/`, { responseType: 'blob' });
  }

  importStatus(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/status/import/`, formData);
  }
}

