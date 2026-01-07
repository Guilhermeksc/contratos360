/**
 * Utilitários para cores e estilos de status
 */

export const STATUS_COLORS: Record<string, string> = {
  'SEÇÃO CONTRATOS': '#808080', // Cinza médio compatível com ambos os temas
  'PORTARIA': '#E6E696',
  'EMPRESA': '#E6E696',
  'SIGDEM': '#E6B464',
  'ASSINADO': '#E6B464',
  'PUBLICADO': '#87CEFA',
  'ALERTA PRAZO': '#FFA0A0',
  'NOTA TÉCNICA': '#FFA0A0',
  'AGU': '#FFA0A0',
  'PRORROGADO': '#87CEFA',
  'SIGAD': '#E6B464'
};

export function getStatusColor(status: string | null | undefined, isDarkTheme: boolean = false): string {
  if (!status) {
    return STATUS_COLORS['SEÇÃO CONTRATOS'];
  }
  
  // Para "SEÇÃO CONTRATOS", ajusta a cor baseado no tema
  if (status === 'SEÇÃO CONTRATOS') {
    return isDarkTheme ? '#CCCCCC' : '#666666'; // Cinza claro no tema escuro, cinza escuro no tema claro
  }
  
  return STATUS_COLORS[status] || STATUS_COLORS['SEÇÃO CONTRATOS'];
}

