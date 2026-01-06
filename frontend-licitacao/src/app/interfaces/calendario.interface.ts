export interface CalendarioEvento {
  id: number;
  nome: string;
  data: string;  // DateField (ISO: YYYY-MM-DD)
  descricao: string | null;
  cor: string;  // Cor em formato hexadecimal (ex: #3788d8)
  created_at: string;  // DateTimeField (ISO)
  updated_at: string;  // DateTimeField (ISO)
}

export interface CalendarioEventoCreate {
  nome: string;
  data: string;  // DateField (ISO: YYYY-MM-DD)
  descricao?: string | null;
  cor?: string;  // Cor em formato hexadecimal (ex: #3788d8)
}

export interface CalendarioEventoUpdate {
  nome?: string;
  data?: string;
  descricao?: string | null;
  cor?: string;
}

