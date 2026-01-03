import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ArquivoContrato } from '../interfaces/offline.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class ArquivosService {
  private apiUrl = `${environment.apiUrl}/arquivos`;

  constructor(private http: HttpClient) {}

  list(contratoId: string): Observable<ArquivoContrato[]> {
    return this.http.get<ArquivoContrato[]>(this.apiUrl, {
      params: new HttpParams().set('contrato', contratoId)
    });
  }
}

