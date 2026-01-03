export interface HistoricoContrato {
  id: number;
  contrato: string;
  receita_despesa: string | null;
  numero: string | null;
  observacao: string | null;
  ug: string | null;
  gestao: string | null;
  fornecedor_cnpj: string | null;
  fornecedor_nome: string | null;
  tipo: string | null;
  categoria: string | null;
  processo: string | null;
  objeto: string | null;
  modalidade: string | null;
  licitacao_numero: string | null;
  data_assinatura: string | null;  // DateField (ISO)
  data_publicacao: string | null;  // DateField (ISO)
  vigencia_inicio: string | null;  // DateField (ISO)
  vigencia_fim: string | null;  // DateField (ISO)
  valor_global: number | null;  // DecimalField
  raw_json: any | null;
}

export interface Empenho {
  id: number;
  contrato: string;
  unidade_gestora: string | null;
  gestao: string | null;
  numero: string | null;
  data_emissao: string | null;  // DateField (ISO)
  credor_cnpj: string | null;
  credor_nome: string | null;
  empenhado: number | null;  // DecimalField
  liquidado: number | null;  // DecimalField
  pago: number | null;  // DecimalField
  informacao_complementar: string | null;
  raw_json: any | null;
}

export interface ItemContrato {
  id: number;
  contrato: string;
  tipo_id: string | null;
  tipo_material: string | null;
  grupo_id: string | null;
  catmatseritem_id: string | null;
  descricao_complementar: string | null;
  quantidade: number | null;  // DecimalField (4 casas)
  valorunitario: number | null;  // DecimalField
  valortotal: number | null;  // DecimalField
  numero_item_compra: string | null;
  raw_json: any | null;
}

export interface ArquivoContrato {
  id: number;
  contrato: string;
  tipo: string | null;
  descricao: string | null;
  path_arquivo: string | null;
  origem: string | null;
  link_sei: string | null;
  raw_json: any | null;
}

