export interface StatusContrato {
  contrato: string;  // FK para Contrato.id
  uasg_code: string | null;
  status: string | null;  // Ex: "ALERTA PRAZO", "PORTARIA", etc.
  objeto_editado: string | null;
  portaria_edit: string | null;
  termo_aditivo_edit: string | null;
  radio_options_json: RadioOptions | null;  // JSONField parseado
  data_registro: string | null;  // Formato: "DD/MM/AAAA HH:MM:SS"
}

export interface RadioOptions {
  "Pode Renovar?": string;
  "Custeio?": string;
  "Natureza Continuada?": string;
  "Material/Serviço:": string;
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

