export interface StatusContrato {
  contrato: string;  // FK para Contrato.id
  uasg_code: string | null;
  uasg_nome?: string | null;  // Nome da UASG
  status: string | null;  // Ex: "ALERTA PRAZO", "PORTARIA", etc.
  objeto_editado: string | null;
  portaria_edit: string | null;
  termo_aditivo_edit: string | null;
  pode_renovar: boolean;  // Indica se o contrato pode ser renovado
  custeio: boolean;  // Indica se é contrato de custeio
  natureza_continuada: boolean;  // Indica se o contrato tem natureza continuada
  tipo_contrato: 'material' | 'servico' | null;  // Tipo do contrato: Material ou Serviço
  data_registro: string | null;  // Formato: "DD/MM/AAAA HH:MM:SS"
}

export interface RegistroStatus {
  id: number;
  contrato: string;
  uasg_code: string | null;
  texto: string;  // Formato: "DD/MM/AAAA - mensagem - STATUS"
}

export interface RegistroMensagem {
  id: number;
  contrato: string;
  texto: string;
}

