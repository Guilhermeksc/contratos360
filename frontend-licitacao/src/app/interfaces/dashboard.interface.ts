export interface DashboardSummary {
  total_contratos: number;
  valor_total: number;
  ativos: number;
  expirando: number;  // Próximos 90 dias
  status_distribuicao: Record<string, number>;  // { "ALERTA PRAZO": 5, ... }
}

