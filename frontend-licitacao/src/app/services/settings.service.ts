import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { environment } from '../environments/environment';

export interface AppSettings {
  data_mode: 'Online' | 'Offline';
  db_path?: string;
}

@Injectable({ providedIn: 'root' })
export class SettingsService {
  private apiUrl = `${environment.apiUrl}/settings`;
  private modeSubject = new BehaviorSubject<'Online' | 'Offline'>('Online');
  public mode$ = this.modeSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadSettings();
  }

  getSettings(): Observable<AppSettings> {
    // Endpoint a ser criado: GET /api/contratos/settings/
    // Por enquanto retorna padrão
    return new Observable(observer => {
      observer.next({ data_mode: 'Online' });
      observer.complete();
    });
  }

  updateSettings(settings: Partial<AppSettings>): Observable<AppSettings> {
    // Endpoint a ser criado: PUT /api/contratos/settings/
    return this.getSettings().pipe(
      tap(s => {
        const updated = { ...s, ...settings };
        if (updated.data_mode) {
          this.modeSubject.next(updated.data_mode);
        }
      })
    );
  }

  syncContrato(contratoId: string): Observable<any> {
    // Endpoint a ser criado: POST /api/contratos/sync-detalhes/
    return this.http.post(`${environment.apiUrl}/sync-detalhes/`, {
      contrato_id: contratoId
    });
  }

  private loadSettings(): void {
    this.getSettings().subscribe(settings => {
      this.modeSubject.next(settings.data_mode || 'Online');
    });
  }
}

