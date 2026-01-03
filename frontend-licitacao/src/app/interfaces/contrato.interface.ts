import { StatusContrato } from './status.interface';
import { LinksContrato } from './links.interface';
import { FiscalizacaoContrato } from './fiscalizacao.interface';

export interface Contrato {
  id: string;  // String (vem da API)
  numero: string | null;
  uasg: string;  // FK para Uasg.uasg_code
  uasg_nome?: string;  // Campo calculado do serializer
  licitacao_numero: string | null;
  processo: string | null;
  fornecedor_nome: string | null;
  fornecedor_cnpj: string | null;
  objeto: string | null;
  valor_global: number | null;  // DecimalField convertido
  vigencia_inicio: string | null;  // DateField (ISO: YYYY-MM-DD)
  vigencia_fim: string | null;  // DateField (ISO: YYYY-MM-DD)
  tipo: string | null;
  modalidade: string | null;
  contratante_orgao_unidade_gestora_codigo: string | null;
  contratante_orgao_unidade_gestora_nome_resumido: string | null;
  manual: boolean;
  raw_json: any | null;  // JSONField
  status_atual?: string;  // Campo calculado do serializer
  created_at?: string;  // DateTimeField (ISO)
  updated_at?: string;  // DateTimeField (ISO)
}

export interface ContratoDetail extends Contrato {
  status: StatusContrato | null;
  links: LinksContrato | null;
  fiscalizacao: FiscalizacaoContrato | null;
  registros_status: string[];  // Array de textos
  registros_mensagem: string[];  // Array de textos
  historicos_count: number;
  empenhos_count: number;
  itens_count: number;
  arquivos_count: number;
}

export interface ContratoCreate {
  id: string;
  uasg: string;
  numero: string;
  licitacao_numero?: string | null;
  processo?: string | null;
  fornecedor_nome?: string | null;
  fornecedor_cnpj?: string | null;
  objeto?: string | null;
  valor_global?: number | null;
  vigencia_inicio?: string | null;
  vigencia_fim?: string | null;
  tipo?: string | null;
  modalidade?: string | null;
  contratante_orgao_unidade_gestora_codigo?: string | null;
  contratante_orgao_unidade_gestora_nome_resumido?: string | null;
  manual: boolean;
  raw_json?: any | null;
}

