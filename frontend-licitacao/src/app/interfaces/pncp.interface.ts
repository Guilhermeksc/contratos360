export interface Compra {
  compra_id: string;
  ano_compra: number;
  sequencial_compra: number;
  numero_compra: string;
  codigo_unidade: string;
  objeto_compra: string;
  modalidade_nome: string;
  numero_processo: string;
  data_publicacao_pncp: string | null;
  data_atualizacao: string | null;
  valor_total_estimado: string | null;
  valor_total_homologado: string | null;
  percentual_desconto: string | null;
  link_pncp: string;
  itens?: ItemCompra[];
}

export interface ItemCompra {
  item_id: string;
  numero_item: number;
  descricao: string;
  unidade_medida: string;
  valor_unitario_estimado: string | null;
  valor_total_estimado: string | null;
  quantidade: string;
  percentual_economia: string | null;
  situacao_compra_item_nome: string;
  resultados?: ResultadoItem[];
}

export interface ResultadoItem {
  resultado_id: string;
  valor_total_homologado: string;
  quantidade_homologada: number;
  valor_unitario_homologado: string;
  fornecedor_detalhes: {
    cnpj_fornecedor: string;
    razao_social: string;
  };
}

export interface ItemResultadoMerge {
  ano_compra: number;
  sequencial_compra: number;
  numero_item: number;
  descricao: string;
  unidade_medida: string;
  valor_unitario_estimado: string | null;
  valor_total_estimado: string | null;
  quantidade: string;
  situacao_compra_item_nome: string;
  cnpj_fornecedor: string | null;
  valor_total_homologado: string | null;
  valor_unitario_homologado: string | null;
  quantidade_homologada: number | null;
  percentual_desconto: number | string | null;
  link_pncp: string;
  razao_social: string | null;
}

export interface ModalidadeAgregada {
  ano_compra: number;
  modalidade_nome: string;
  quantidade_compras: number;
  valor_total_homologado: string | null;
}

export interface FornecedorAgregado {
  cnpj_fornecedor: string;
  razao_social: string | null;
  valor_total_homologado: string;
}
