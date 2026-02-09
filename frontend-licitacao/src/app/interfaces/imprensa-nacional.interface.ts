export interface AvisoLicitacao {
  id: number;
  article_id: string;
  modalidade: string | null;
  numero: string | null;
  ano: string | null;
  uasg: string | null;
  processo: string | null;
  objeto: string | null;
  itens_licitados: string | null;
  publicacao: string | null;
  entrega_propostas: string | null;
  abertura_propostas: string | null;
  nome_responsavel: string | null;
  cargo: string | null;
}

export interface Credenciamento {
  id: number;
  article_id: string;
  tipo: string | null;
  numero: string | null;
  ano: string | null;
  uasg: string | null;
  processo: string | null;
  tipo_processo: string | null;
  numero_processo: string | null;
  ano_processo: string | null;
  contratante: string | null;
  contratado: string | null;
  objeto: string | null;
  fundamento_legal: string | null;
  vigencia: string | null;
  valor_total: string | null;
  data_assinatura: string | null;
  nome_responsavel: string | null;
  cargo: string | null;
}

export interface InlabsArticle {
  id: number;
  article_id: string;
  name: string | null;
  id_oficio: string | null;
  pub_name: string | null;
  art_type: string | null;
  pub_date: string | null; // Data de publicação (formato YYYY-MM-DD)
  nome_om: string | null; // Nome da Organização Militar
  number_page: string | null;
  pdf_page: string | null;
  edition_number: string | null;
  highlight_type: string | null;
  highlight_priority: string | null;
  highlight: string | null;
  highlight_image: string | null;
  highlight_image_name: string | null;
  materia_id: string | null;
  body_identifica: string | null; // Texto do campo Identifica
  uasg: string | null; // UASG extraído (pode vir do campo uasg ou do body_identifica)
  body_texto: string | null; // HTML do conteúdo do artigo (decodificado)
  om_name: string | null; // Nome da OM extraído (alias para nome_om)
  aviso_licitacao: AvisoLicitacao | null; // Aviso de licitação relacionado (se existir)
  credenciamento: Credenciamento | null; // Credenciamento relacionado (se existir)
}
