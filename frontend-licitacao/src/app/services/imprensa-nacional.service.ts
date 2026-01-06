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
    edition_date?: string;
    article_id?: string;
    pub_name?: string;
    art_type?: string;
    search?: string;
    ordering?: string;
    page?: number;
  }): Observable<InlabsArticleListResponse | InlabsArticle[]> {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.edition_date) {
        httpParams = httpParams.set('edition_date', params.edition_date);
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
   * Busca artigos por data de edição
   */
  getByDate(editionDate: string): Observable<InlabsArticle[]> {
    return this.list({ edition_date: editionDate }).pipe(
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

