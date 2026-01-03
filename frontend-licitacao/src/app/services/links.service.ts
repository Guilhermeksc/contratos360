import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { LinksContrato } from '../interfaces/links.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class LinksService {
  private apiUrl = `${environment.apiUrl}/links`;

  constructor(private http: HttpClient) {}

  get(contratoId: string): Observable<LinksContrato | null> {
    return this.http.get<LinksContrato[]>(this.apiUrl, {
      params: new HttpParams().set('contrato', contratoId)
    }).pipe(
      map(results => results.length > 0 ? results[0] : null)
    );
  }

  createOrUpdate(data: Partial<LinksContrato>): Observable<LinksContrato> {
    return this.http.post<LinksContrato>(this.apiUrl, data);
  }

  update(id: number, data: Partial<LinksContrato>): Observable<LinksContrato> {
    return this.http.put<LinksContrato>(`${this.apiUrl}/${id}/`, data);
  }
}

