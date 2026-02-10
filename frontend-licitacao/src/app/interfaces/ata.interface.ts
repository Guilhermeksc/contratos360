/**
 * Interface completa para Ata de Registro de Preço
 */
export interface Ata {
  numero_controle_pncp_ata: string;
  numero_ata_registro_preco: string;
  ano_ata: number;
  numero_controle_pncp_compra: string;
  cancelado: number;
  data_cancelamento: string | null;
  data_assinatura: string | null;
  vigencia_inicio: string | null;
  vigencia_fim: string | null;
  data_publicacao_pncp: string | null;
  data_inclusao: string | null;
  data_atualizacao: string | null;
  data_atualizacao_global: string | null;
  usuario: string;
  objeto_contratacao: string;
  cnpj_orgao: string;
  nome_orgao: string;
  cnpj_orgao_subrogado: string | null;
  nome_orgao_subrogado: string | null;
  codigo_unidade_orgao: string;
  nome_unidade_orgao: string;
  codigo_unidade_orgao_subrogado: string | null;
  nome_unidade_orgao_subrogado: string | null;
  sequencial: string;
  ano: number | null;
  numero_compra: string;
}

/**
 * Interface simplificada para listagem de Atas
 */
export interface AtaListagem {
  numero_controle_pncp_ata: string;
  numero_ata_registro_preco: string;
  ano_ata: number;
  nome_orgao: string;
  nome_unidade_orgao: string;
  objeto_contratacao: string;
  data_assinatura: string | null;
  vigencia_inicio: string | null;
  vigencia_fim: string | null;
  cancelado: number;
  data_cancelamento: string | null;
}

/**
 * Interface para unidade por ano (usado no endpoint unidades_por_ano)
 */
export interface UnidadePorAnoAta {
  codigo_unidade_orgao: string;
  sigla_om: string | null;
  total_atas: number;
}

/**
 * Interface para resposta do endpoint unidades_por_ano
 * Agrupa unidades por ano
 */
export interface UnidadesPorAnoResponse {
  [ano: string]: UnidadePorAnoAta[];
}

/**
 * Interface para item de ata no endpoint atas_por_unidade_ano
 */
export interface AtaPorUnidadeAnoItem {
  numero_controle_pncp_ata: string;
  numero_ata_registro_preco: string;
  ano_ata: number;
  objeto_contratacao: string;
  data_assinatura: string | null;
  vigencia_inicio: string | null;
  vigencia_fim: string | null;
  cancelado: number;
  codigo_unidade_orgao: string;
  numero_compra: string;
  ano: number;
  sequencial: string;
  sigla_om: string | null;
  cnpj_orgao: string;
}

/**
 * Interface para resposta do endpoint atas_por_unidade_ano
 */
export interface AtasPorUnidadeAnoResponse {
  codigo_unidade_orgao: string;
  ano: number;
  total_atas: number;
  atas: AtaPorUnidadeAnoItem[];
}

/**
 * Interface para unidade com sigla (usado no combo)
 */
export interface UnidadeComSiglaAta {
  codigo_unidade_orgao: string;
  sigla_om: string | null;
}

/**
 * Interface para combo de anos e unidades
 */
export interface AnosUnidadesComboAta {
  anos: number[];
  unidades_por_ano: { [ano: string]: UnidadeComSiglaAta[] };
}
