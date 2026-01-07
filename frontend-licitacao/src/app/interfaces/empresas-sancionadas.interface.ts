export interface EmpresaSancionada {
  id: number;
  cadastro: string;
  codigo_sancao: string;
  tipo_pessoa: 'F' | 'J' | '';
  cpf_cnpj: string;
  nome_sancionado: string;
  nome_orgao_sancionador: string;
  razao_social: string;
  nome_fantasia: string;
  numero_processo: string;
  categoria_sancao: string;
  data_inicio_sancao: string | null;  // DateField (ISO: YYYY-MM-DD)
  data_final_sancao: string | null;  // DateField (ISO: YYYY-MM-DD)
  data_publicacao: string | null;  // DateField (ISO: YYYY-MM-DD)
  publicacao: string;
  detalhamento_meio_publicacao: string;
  data_transito_julgado: string | null;  // DateField (ISO: YYYY-MM-DD)
  abrangencia_sancao: string;
  orgao_sancionador: string;
  uf_orgao_sancionador: string;
  esfera_orgao_sancionador: string;
  fundamentacao_legal: string;
  data_origem_informacao: string | null;  // DateField (ISO: YYYY-MM-DD)
  origem_informacoes: string;
  observacoes: string;
  created_at: string;  // DateTimeField (ISO)
  updated_at: string;  // DateTimeField (ISO)
}

export interface EmpresasSancionadasListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: EmpresaSancionada[];
}

export interface EmpresasSancionadasFilters {
  tipo_pessoa?: 'F' | 'J';
  categoria_sancao?: string;
  esfera_orgao_sancionador?: string;
  uf_orgao_sancionador?: string;
  data_inicio_sancao?: string;
  data_final_sancao?: string;
  cpf_cnpj?: string;
  search?: string;
  ordering?: string;
  page?: number;
}

