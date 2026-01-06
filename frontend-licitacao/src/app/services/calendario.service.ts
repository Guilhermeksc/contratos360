import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CalendarioEvento, CalendarioEventoCreate, CalendarioEventoUpdate } from '../interfaces/calendario.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class CalendarioService {
  private apiUrl = `${environment.apiUrl}/calendario`;

  constructor(private http: HttpClient) {}

  /**
   * Lista todos os eventos do calendário
   */
  list(): Observable<CalendarioEvento[]> {
    return this.http.get<CalendarioEvento[]>(`${this.apiUrl}/eventos/`);
  }

  /**
   * Busca eventos por mês e ano
   */
  getByMonth(ano: number, mes: number): Observable<CalendarioEvento[]> {
    const params = new HttpParams()
      .set('ano', ano.toString())
      .set('mes', mes.toString());
    return this.http.get<CalendarioEvento[]>(`${this.apiUrl}/eventos/por_mes/`, { params });
  }

  /**
   * Obtém um evento específico por ID
   */
  get(id: number): Observable<CalendarioEvento> {
    return this.http.get<CalendarioEvento>(`${this.apiUrl}/eventos/${id}/`);
  }

  /**
   * Cria um novo evento
   */
  create(evento: CalendarioEventoCreate): Observable<CalendarioEvento> {
    return this.http.post<CalendarioEvento>(`${this.apiUrl}/eventos/`, evento);
  }

  /**
   * Atualiza um evento existente
   */
  update(id: number, evento: CalendarioEventoUpdate): Observable<CalendarioEvento> {
    return this.http.patch<CalendarioEvento>(`${this.apiUrl}/eventos/${id}/`, evento);
  }

  /**
   * Remove um evento
   */
  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/eventos/${id}/`);
  }
}

