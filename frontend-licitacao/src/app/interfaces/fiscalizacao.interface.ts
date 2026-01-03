export interface FiscalizacaoContrato {
  id: number;
  contrato: string;
  gestor: string | null;
  gestor_substituto: string | null;
  fiscal_tecnico: string | null;
  fiscal_tec_substituto: string | null;
  fiscal_administrativo: string | null;
  fiscal_admin_substituto: string | null;
  observacoes: string | null;
  data_criacao: string | null;  // DateTimeField (ISO)
  data_atualizacao: string | null;  // DateTimeField (ISO)
}

