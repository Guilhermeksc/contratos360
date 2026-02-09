import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { InlabsArticle } from '../interfaces/imprensa-nacional.interface';
import { environment } from '../environments/environment';

export interface InlabsArticleListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: InlabsArticle[];
}

@Injectable({ providedIn: 'root' })
export class ImprensaNacionalService {
  private apiUrl = `${environment.apiUrl}/inlabs/articles`;

  constructor(private http: HttpClient) {}

  /**
   * Lista todos os artigos do INLABS
   */
  list(params?: {
    pub_date?: string; // Data de publicação (formato YYYY-MM-DD)
    article_id?: string;
    pub_name?: string;
    art_type?: string;
    uasg?: string;
    nome_om?: string;
    materia_id?: string;
    search?: string; // Busca em: name, nome_om, body_identifica, body_texto
    ordering?: string; // Campos: pub_date, article_id, pub_name (prefixo - para desc)
    page?: number;
  }): Observable<InlabsArticleListResponse | InlabsArticle[]> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.pub_date) {
        httpParams = httpParams.set('pub_date', params.pub_date);
      }
      if (params.article_id) {
        httpParams = httpParams.set('article_id', params.article_id);
      }
      if (params.pub_name) {
        httpParams = httpParams.set('pub_name', params.pub_name);
      }
      if (params.art_type) {
        httpParams = httpParams.set('art_type', params.art_type);
      }
      if (params.uasg) {
        httpParams = httpParams.set('uasg', params.uasg);
      }
      if (params.nome_om) {
        httpParams = httpParams.set('nome_om', params.nome_om);
      }
      if (params.materia_id) {
        httpParams = httpParams.set('materia_id', params.materia_id);
      }
      if (params.search) {
        httpParams = httpParams.set('search', params.search);
      }
      if (params.ordering) {
        httpParams = httpParams.set('ordering', params.ordering);
      }
      if (params.page) {
        httpParams = httpParams.set('page', params.page.toString());
      }
    }

    return this.http.get<any>(this.apiUrl, { params: httpParams }).pipe(
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
   * Busca um artigo específico por ID
   */
  get(id: number): Observable<InlabsArticle> {
    return this.http.get<InlabsArticle>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Busca artigos por data de publicação
   */
  getByDate(pubDate: string): Observable<InlabsArticle[]> {
    return this.list({ pub_date: pubDate }).pipe(
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
}




