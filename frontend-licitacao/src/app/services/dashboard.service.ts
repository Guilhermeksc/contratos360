import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import { map } from 'rxjs/operators';
import { DashboardSummary } from '../interfaces/dashboard.interface';
import { ContractsService } from './contracts.service';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  constructor(
    private http: HttpClient,
    private contractsService: ContractsService
  ) {}

  getSummary(): Observable<DashboardSummary> {
    // Busca dados agregados
    return forkJoin({
      total: this.contractsService.list().pipe(map(r => r.count)),
      ativos: this.contractsService.getAtivos().pipe(map(r => r.length)),
      proximosVencer: this.contractsService.getProximosVencer().pipe(map(r => r.length)),
      vencidos: this.contractsService.getVencidos().pipe(map(r => r.length))
    }).pipe(
      map(data => {
        // Calcula valor total e distribuição de status
        // (pode ser otimizado com endpoint agregado no backend)
        return {
          total_contratos: data.total,
          valor_total: 0,  // Calcular somando valor_global
          ativos: data.ativos,
          expirando: data.proximosVencer,
          status_distribuicao: {}  // Agregar por status
        };
      })
    );
  }
}

