export interface InlabsArticle {
  id: number;
  article_id: string;
  edition_date: string; // ISO date string
  name: string;
  id_oficio: string;
  pub_name: string;
  art_type: string;
  pub_date: string;
  art_class: string;
  art_category: string;
  art_notes: string;
  pdf_page: string;
  edition_number: string;
  highlight_type: string;
  highlight_priority: string;
  highlight: string;
  highlight_image: string;
  highlight_image_name: string;
  materia_id: string;
  body_html: string;
  source_filename: string;
  source_zip: string;
  raw_payload: Record<string, any>;
  uasg?: string | null; // UASG extraído do Identifica
  om_name?: string | null; // Nome da OM extraído da categoria
  objeto?: string | null; // Objeto extraído (quando tipo é Aviso de Licitação-Pregão)
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}
