/**
 * Utilitários para formatação de valores monetários
 */

export function formatCurrency(value: number | null): string {
  if (value === null) return 'R$ 0,00';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
}

