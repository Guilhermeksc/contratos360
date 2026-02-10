import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import {
  Ata,
  AtaListagem,
  UnidadesPorAnoResponse,
  AtasPorUnidadeAnoResponse,
  AnosUnidadesComboAta,
  UnidadeComSiglaAta
} from '../interfaces/ata.interface';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class AtaService {
  private apiUrl = `${environment.apiUrl}/atas`;
  private readonly CACHE_TTL_MS = 2 * 60 * 60 * 1000;

  constructor(private http: HttpClient) {}

  private buildCacheKey(path: string, params?: HttpParams): string {
    const query = params?.toString();
    return `ata_cache|${path}${query ? `?${query}` : ''}`;
  }

  private getCached<T>(key: string): T | null {
    const raw = localStorage.getItem(key);
    if (!raw) {
      return null;
    }
    try {
      const parsed = JSON.parse(raw) as { timestamp: number; data: T };
      if (!parsed?.timestamp || Date.now() - parsed.timestamp > this.CACHE_TTL_MS) {
        localStorage.removeItem(key);
        return null;
      }
      return parsed.data;
    } catch {
      localStorage.removeItem(key);
      return null;
    }
  }

  private setCached<T>(key: string, data: T): void {
    try {
      const serialized = JSON.stringify({ timestamp: Date.now(), data });
      localStorage.setItem(key, serialized);
    } catch (error) {
      // Se exceder a quota, limpa cache antigo e tenta novamente
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        console.warn('Quota do localStorage excedida, limpando cache antigo...');
        this.limparCacheAntigo();
        try {
          const serialized = JSON.stringify({ timestamp: Date.now(), data });
          localStorage.setItem(key, serialized);
        } catch (retryError) {
          console.error('Erro ao salvar no cache após limpeza:', retryError);
          // Remove o item específico se ainda falhar
          localStorage.removeItem(key);
        }
      } else {
        console.error('Erro ao salvar no cache:', error);
      }
    }
  }

  /**
   * Limpa cache antigo quando a quota é excedida
   */
  private limparCacheAntigo(): void {
    const keysToRemove: string[] = [];
    const now = Date.now();
    
    // Coleta todas as chaves de cache de atas
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('ata_cache|')) {
        try {
          const item = localStorage.getItem(key);
          if (item) {
            const parsed = JSON.parse(item);
            // Remove itens com mais de 1 hora
            if (parsed.timestamp && now - parsed.timestamp > 60 * 60 * 1000) {
              keysToRemove.push(key);
            }
          }
        } catch {
          // Se não conseguir parsear, remove também
          keysToRemove.push(key);
        }
      }
    }
    
    // Remove as chaves antigas
    keysToRemove.forEach(key => localStorage.removeItem(key));
    
    // Se ainda não tiver espaço, remove metade dos itens restantes
    if (keysToRemove.length === 0) {
      const allCacheKeys: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('ata_cache|')) {
          allCacheKeys.push(key);
        }
      }
      // Remove metade dos itens mais antigos
      allCacheKeys.slice(0, Math.floor(allCacheKeys.length / 2)).forEach(key => {
        localStorage.removeItem(key);
      });
    }
  }

  private withCache<T>(key: string, request$: Observable<T>): Observable<T> {
    const cached = this.getCached<T>(key);
    if (cached !== null) {
      return of(cached);
    }
    return request$.pipe(tap((data) => this.setCached(key, data)));
  }

  /**
   * Endpoint específico: busca ata por codigo_unidade_orgao + numero_compra + ano
   */
  buscarEspecifica(
    codigoUnidadeOrgao: string,
    numeroCompra: string,
    ano: number
  ): Observable<Ata[]> {
    const params = new HttpParams()
      .set('codigo_unidade_orgao', codigoUnidadeOrgao)
      .set('numero_compra', numeroCompra)
      .set('ano', ano.toString());

    const url = `${this.apiUrl}/buscar_especifica/`;
    return this.withCache(
      this.buildCacheKey(url, params),
      this.http.get<Ata[]>(url, { params })
    );
  }

  /**
   * Endpoint amplo: relaciona todos os codigo_unidade_orgao para cada ano
   */
  getUnidadesPorAno(): Observable<UnidadesPorAnoResponse> {
    const url = `${this.apiUrl}/unidades_por_ano/`;
    return this.withCache(
      this.buildCacheKey(url),
      this.http.get<UnidadesPorAnoResponse>(url)
    );
  }

  /**
   * Endpoint: relaciona todos os numero_controle_pncp_ata para cada codigo_unidade_orgao para o ano
   */
  getAtasPorUnidadeAno(
    codigoUnidadeOrgao: string,
    ano: number
  ): Observable<AtasPorUnidadeAnoResponse> {
    const params = new HttpParams()
      .set('codigo_unidade_orgao', codigoUnidadeOrgao)
      .set('ano', ano.toString());

    const url = `${this.apiUrl}/atas_por_unidade_ano/`;
    return this.withCache(
      this.buildCacheKey(url, params),
      this.http.get<AtasPorUnidadeAnoResponse>(url, { params })
    );
  }

  /**
   * Obtém todas as atas (listagem completa)
   */
  getAllAtas(): Observable<AtaListagem[]> {
    const url = `${this.apiUrl}/`;
    return this.withCache(
      this.buildCacheKey(url),
      this.http.get<AtaListagem[]>(url)
    );
  }

  /**
   * Obtém uma ata específica por número de controle PNCP
   */
  getAtaPorNumeroControle(numeroControlePncpAta: string): Observable<Ata> {
    const url = `${this.apiUrl}/${numeroControlePncpAta}/`;
    return this.withCache(
      this.buildCacheKey(url),
      this.http.get<Ata>(url)
    );
  }

  /**
   * Obtém atas por órgão (CNPJ)
   */
  getAtasPorOrgao(cnpjOrgao: string): Observable<Ata[]> {
    const params = new HttpParams().set('cnpj_orgao', cnpjOrgao);
    const url = `${this.apiUrl}/por_orgao/`;
    return this.withCache(
      this.buildCacheKey(url, params),
      this.http.get<Ata[]>(url, { params })
    );
  }

  /**
   * Obtém atas por unidade (código da unidade)
   */
  getAtasPorUnidade(codigoUnidade: string): Observable<Ata[]> {
    const params = new HttpParams().set('codigo_unidade', codigoUnidade);
    const url = `${this.apiUrl}/por_unidade/`;
    return this.withCache(
      this.buildCacheKey(url, params),
      this.http.get<Ata[]>(url, { params })
    );
  }

  /**
   * Obtém apenas atas vigentes
   */
  getAtasVigentes(): Observable<Ata[]> {
    const url = `${this.apiUrl}/vigentes/`;
    return this.withCache(
      this.buildCacheKey(url),
      this.http.get<Ata[]>(url)
    );
  }

  /**
   * Obtém apenas atas canceladas
   */
  getAtasCanceladas(): Observable<Ata[]> {
    const url = `${this.apiUrl}/canceladas/`;
    return this.withCache(
      this.buildCacheKey(url),
      this.http.get<Ata[]>(url)
    );
  }

  /**
   * Obtém anos e unidades para combobox (similar ao PNCP)
   */
  getAnosUnidadesCombo(): Observable<AnosUnidadesComboAta> {
    const url = `${this.apiUrl}/unidades_por_ano/`;
    // Usa uma chave de cache específica para forçar atualização quando necessário
    const cacheKey = this.buildCacheKey(url) + '_v2';
    return this.withCache(
      cacheKey,
      this.http.get<UnidadesPorAnoResponse>(url)
    ).pipe(
      map((response) => {
        const anos: number[] = [];
        const unidadesPorAno: { [ano: string]: UnidadeComSiglaAta[] } = {};

        // Processa a resposta para criar a estrutura do combo
        Object.keys(response).forEach((anoStr) => {
          const ano = parseInt(anoStr, 10);
          if (!isNaN(ano)) {
            anos.push(ano);
            unidadesPorAno[anoStr] = response[anoStr].map((unidade) => {
              // Garante que sigla_om seja incluída mesmo se vier como null ou undefined
              return {
                codigo_unidade_orgao: unidade.codigo_unidade_orgao || '',
                sigla_om: unidade.sigla_om ?? null
              };
            });
          }
        });

        // Ordena anos em ordem decrescente
        anos.sort((a, b) => b - a);

        return {
          anos,
          unidades_por_ano: unidadesPorAno
        };
      })
    );
  }
}
