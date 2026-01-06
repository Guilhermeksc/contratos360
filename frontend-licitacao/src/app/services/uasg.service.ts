import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Uasg } from '../interfaces/uasg.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class UasgService {
  private apiUrl = `${environment.apiUrl}/uasgs`;

  constructor(private http: HttpClient) {}

  list(): Observable<Uasg[]> {
    return this.http.get<any>(this.apiUrl).pipe(
      map((response: any) => {
        // Garante que sempre retorne um array
        if (Array.isArray(response)) {
          console.log('UasgService: Resposta é array direto, tamanho:', response.length);
          return response;
        }
        // Se for um objeto paginado, extrai os resultados
        if (response && Array.isArray(response.results)) {
          console.log('UasgService: Resposta paginada, resultados:', response.results.length);
          return response.results;
        }
        console.warn('UasgService.list: Resposta não é um array:', response);
        return [];
      })
    );
  }

  get(code: string): Observable<Uasg> {
    return this.http.get<Uasg>(`${this.apiUrl}/${code}/`);
  }
}

