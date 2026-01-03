/**
 * Utilitários para formatação e cálculo de datas
 */

export function calcularDiasRestantes(vigenciaFim: string | null): number | null {
  if (!vigenciaFim) return null;
  
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  
  const fim = new Date(vigenciaFim);
  fim.setHours(0, 0, 0, 0);
  
  const diffTime = fim.getTime() - hoje.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
}

export function getDiasRestantesStyle(dias: number | null): string {
  if (dias === null) return 'gray';
  if (dias < 0) return 'gray';
  if (dias <= 30) return 'red';
  if (dias <= 90) return 'orange';
  if (dias <= 180) return 'yellow';
  if (dias <= 360) return 'green';
  return 'blue';
}

export function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Não informado';
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR');
}

export function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return 'Não informado';
  const date = new Date(dateStr);
  return date.toLocaleString('pt-BR');
}

