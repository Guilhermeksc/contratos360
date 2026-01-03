"""
Serviço de ingestão de dados da API ComprasNet
Migrado do OfflineDBController do PyQt
"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from ..models import (
    Uasg,
    Contrato,
    HistoricoContrato,
    Empenho,
    ItemContrato,
    ArquivoContrato,
)


class ComprasNetIngestionService:
    """
    Serviço para ingerir dados da API pública do ComprasNet
    """
    
    BASE_URL = "https://contratos.comprasnet.gov.br/api"
    TIMEOUT = 20
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    def _fetch_api_data(self, url: str, tentativas_maximas: int = None) -> List[Dict]:
        """
        Busca dados de uma API com retentativas.
        
        Args:
            url: URL da API
            tentativas_maximas: Número máximo de tentativas (padrão: self.MAX_RETRIES)
        
        Returns:
            Lista de dados JSON ou lista vazia em caso de erro
        """
        tentativas_maximas = tentativas_maximas or self.MAX_RETRIES
        
        for tentativa in range(1, tentativas_maximas + 1):
            try:
                print(f" - Buscando dados em {url} (Tentativa {tentativa}/{tentativas_maximas})")
                response = requests.get(url, timeout=self.TIMEOUT, stream=False)
                response.raise_for_status()
                # Lê o conteúdo de uma vez para evitar problemas com streaming
                data = response.json()
                return data
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                print(f"⚠ Erro de conexão/timeout na tentativa {tentativa}/{tentativas_maximas}: {e}")
                if tentativa < tentativas_maximas:
                    time.sleep(self.RETRY_DELAY)
                    continue
                return []
            except requests.exceptions.RequestException as e:
                print(f"   ⚠ Erro na requisição: {e}")
                if tentativa < tentativas_maximas:
                    time.sleep(self.RETRY_DELAY)
                else:
                    return []
        return []
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Converte string de data para datetime"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    def _truncate_string(self, value: Optional[str], max_length: int) -> Optional[str]:
        """Trunca string se exceder max_length"""
        if value is None:
            return None
        if len(value) > max_length:
            print(f"⚠ Valor truncado de {len(value)} para {max_length} caracteres: {value[:50]}...")
            return value[:max_length]
        return value
    
    def _parse_decimal(self, value: Optional[str]) -> Optional[Decimal]:
        """Converte string numérica para Decimal
        
        Suporta formatos:
        - "1.000.000,50" (vírgula como separador decimal, ponto como separador de milhar)
        - "1000000.50" (ponto como separador decimal)
        - "1000000,50" (vírgula como separador decimal)
        - 1000000.50 (número float)
        """
        if not value:
            return None
        try:
            value_str = str(value).strip()
            
            # Se for número, converte diretamente
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            
            # Se contém vírgula, assume formato brasileiro (1.000.000,50)
            if ',' in value_str:
                # Remove pontos (separadores de milhar) e substitui vírgula por ponto
                cleaned = value_str.replace('.', '').replace(',', '.')
            else:
                # Se não tem vírgula, pode ter ponto como separador decimal ou de milhar
                # Se tem mais de um ponto, assume que são separadores de milhar
                if value_str.count('.') > 1:
                    # Remove todos os pontos (separadores de milhar)
                    cleaned = value_str.replace('.', '')
                else:
                    # Um único ponto é separador decimal
                    cleaned = value_str
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError, TypeError):
            return None
    
    def _filter_contracts_by_vigency(self, contratos: List[Dict]) -> List[Dict]:
        """
        Filtra contratos por vigência.
        Inclui contratos sem data de fim ou que venceram há menos de 100 dias.
        """
        hoje = timezone.now().date()
        contratos_a_processar = []
        
        print(f"Iniciando filtro de {len(contratos)} contratos...")
        
        for contrato_data in contratos:
            vigencia_fim_str = contrato_data.get("vigencia_fim")
            
            # Se não há data de fim, o contrato é válido e deve ser incluído
            if not vigencia_fim_str:
                contratos_a_processar.append(contrato_data)
                continue
            
            try:
                vigencia_fim = datetime.strptime(vigencia_fim_str, '%Y-%m-%d').date()
                # Se tem data, verifica se venceu há menos de 100 dias
                if (hoje - vigencia_fim).days <= 100:
                    contratos_a_processar.append(contrato_data)
            except (ValueError, TypeError):
                print(f"⚠ Aviso: Data de vigência inválida para o contrato {contrato_data.get('id')}. Será ignorado.")
        
        print(f"Filtro concluído. Serão processados {len(contratos_a_processar)} contratos.")
        return contratos_a_processar
    
    def _save_contrato(self, contrato_data: Dict, uasg_code: str) -> Contrato:
        """
        Salva ou atualiza um contrato no banco de dados.
        
        Args:
            contrato_data: Dados do contrato da API
            uasg_code: Código da UASG
        
        Returns:
            Instância do Contrato salvo
        """
        contrato_id = str(contrato_data.get("id"))
        
        # Extrai dados do fornecedor
        fornecedor = contrato_data.get("fornecedor", {})
        contratante = contrato_data.get("contratante", {})
        orgao = contratante.get("orgao", {})
        unidade_gestora = orgao.get("unidade_gestora", {})
        
        # Cria ou atualiza o contrato
        contrato, created = Contrato.objects.update_or_create(
            id=contrato_id,
            defaults={
                'uasg_id': uasg_code,
                'numero': contrato_data.get("numero"),
                'licitacao_numero': contrato_data.get("licitacao_numero"),
                'processo': contrato_data.get("processo"),
                'fornecedor_nome': fornecedor.get("nome"),
                'fornecedor_cnpj': fornecedor.get("cnpj_cpf_idgener"),
                'objeto': contrato_data.get("objeto"),
                'valor_global': self._parse_decimal(contrato_data.get("valor_global")),
                'vigencia_inicio': self._parse_date(contrato_data.get("vigencia_inicio")),
                'vigencia_fim': self._parse_date(contrato_data.get("vigencia_fim")),
                'tipo': contrato_data.get("tipo"),
                'modalidade': contrato_data.get("modalidade"),
                'contratante_orgao_unidade_gestora_codigo': unidade_gestora.get("codigo"),
                'contratante_orgao_unidade_gestora_nome_resumido': unidade_gestora.get("nome_resumido"),
                'manual': False,
                'raw_json': contrato_data,
            }
        )
        
        action = "Criado" if created else "Atualizado"
        print(f"  {action} contrato {contrato.numero or contrato_id}")
        
        return contrato
    
    def _save_historico(self, contrato: Contrato, historico_data: List[Dict]):
        """Salva histórico de um contrato"""
        HistoricoContrato.objects.filter(contrato=contrato).delete()
        
        for item_data in historico_data:
            try:
                HistoricoContrato.objects.create(
                    contrato=contrato,
                    receita_despesa=self._truncate_string(item_data.get("receita_despesa"), 200),
                    numero=self._truncate_string(item_data.get("numero"), 100),
                    observacao=item_data.get("observacao"),
                    ug=self._truncate_string(item_data.get("ug"), 20),
                    gestao=self._truncate_string(item_data.get("gestao"), 200),
                    fornecedor_cnpj=self._truncate_string(item_data.get("fornecedor_cnpj"), 20),
                    fornecedor_nome=self._truncate_string(item_data.get("fornecedor_nome"), 255),
                    tipo=self._truncate_string(item_data.get("tipo"), 100),
                    categoria=self._truncate_string(item_data.get("categoria"), 100),
                    processo=self._truncate_string(item_data.get("processo"), 100),
                    objeto=item_data.get("objeto"),
                    modalidade=self._truncate_string(item_data.get("modalidade"), 100),
                    licitacao_numero=self._truncate_string(item_data.get("licitacao_numero"), 100),
                    data_assinatura=self._parse_date(item_data.get("data_assinatura")),
                    data_publicacao=self._parse_date(item_data.get("data_publicacao")),
                    vigencia_inicio=self._parse_date(item_data.get("vigencia_inicio")),
                    vigencia_fim=self._parse_date(item_data.get("vigencia_fim")),
                    valor_global=self._parse_decimal(item_data.get("valor_global")),
                    raw_json=item_data,
                )
            except Exception as e:
                print(f"⚠ Erro ao salvar histórico: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def _save_empenhos(self, contrato: Contrato, empenhos_data: List[Dict]):
        """Salva empenhos de um contrato"""
        Empenho.objects.filter(contrato=contrato).delete()
        
        for item_data in empenhos_data:
            try:
                Empenho.objects.create(
                    contrato=contrato,
                    unidade_gestora=self._truncate_string(item_data.get("unidade_gestora"), 200),
                    gestao=self._truncate_string(item_data.get("gestao"), 200),
                    numero=self._truncate_string(item_data.get("numero"), 100),
                    data_emissao=self._parse_date(item_data.get("data_emissao")),
                    credor_cnpj=self._truncate_string(item_data.get("credor_cnpj"), 20),
                    credor_nome=self._truncate_string(item_data.get("credor_nome"), 255),
                    empenhado=self._parse_decimal(item_data.get("empenhado")),
                    liquidado=self._parse_decimal(item_data.get("liquidado")),
                    pago=self._parse_decimal(item_data.get("pago")),
                    informacao_complementar=item_data.get("informacao_complementar"),
                    raw_json=item_data,
                )
            except Exception as e:
                print(f"⚠ Erro ao salvar empenho: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def _save_itens(self, contrato: Contrato, itens_data: List[Dict]):
        """Salva itens de um contrato"""
        ItemContrato.objects.filter(contrato=contrato).delete()
        
        for item_data in itens_data:
            try:
                ItemContrato.objects.create(
                    contrato=contrato,
                    tipo_id=self._truncate_string(item_data.get("tipo_id"), 200),
                    tipo_material=self._truncate_string(item_data.get("tipo_material"), 500),
                    grupo_id=self._truncate_string(item_data.get("grupo_id"), 200),
                    catmatseritem_id=self._truncate_string(item_data.get("catmatseritem_id"), 200),
                    descricao_complementar=item_data.get("descricao_complementar"),
                    quantidade=self._parse_decimal(item_data.get("quantidade")),
                    valorunitario=self._parse_decimal(item_data.get("valorunitario")),
                    valortotal=self._parse_decimal(item_data.get("valortotal")),
                    numero_item_compra=self._truncate_string(item_data.get("numero_item_compra"), 100),
                    raw_json=item_data,
                )
            except Exception as e:
                print(f"⚠ Erro ao salvar item: {e}")
                import traceback
                traceback.print_exc()
                # Continua processando outros itens
                continue
    
    def _save_arquivos(self, contrato: Contrato, arquivos_data: List[Dict]):
        """Salva arquivos de um contrato"""
        ArquivoContrato.objects.filter(contrato=contrato).delete()
        
        for item_data in arquivos_data:
            try:
                ArquivoContrato.objects.create(
                    contrato=contrato,
                    tipo=item_data.get("tipo"),
                    descricao=item_data.get("descricao"),
                    path_arquivo=item_data.get("path_arquivo"),
                    origem=item_data.get("origem"),
                    link_sei=item_data.get("link_sei"),
                    raw_json=item_data,
                )
            except Exception as e:
                print(f"⚠ Erro ao salvar arquivo: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def sync_contratos_por_uasg(self, uasg_code: str) -> Dict[str, int]:
        """
        Sincroniza todos os contratos de uma UASG.
        
        Args:
            uasg_code: Código da UASG
        
        Returns:
            Dicionário com estatísticas da sincronização
        """
        url = f"{self.BASE_URL}/contrato/ug/{uasg_code}"
        main_data = self._fetch_api_data(url)
        
        if not main_data:
            print(f"⚠ Não foi possível obter dados para a UASG {uasg_code}.")
            return {'contratos_processados': 0, 'historicos': 0, 'empenhos': 0, 'itens': 0, 'arquivos': 0}
        
        # Cria ou atualiza UASG (fora da transação principal)
        try:
            nome_resumido = main_data[0].get("contratante", {}).get("orgao", {}).get("unidade_gestora", {}).get("nome_resumido", "")
            Uasg.objects.update_or_create(
                uasg_code=uasg_code,
                defaults={'nome_resumido': nome_resumido}
            )
        except Exception as e:
            print(f"⚠ Erro ao criar/atualizar UASG {uasg_code}: {e}")
        
        # Filtra contratos por vigência
        contratos_a_processar = self._filter_contracts_by_vigency(main_data)
        
        if not contratos_a_processar:
            return {'contratos_processados': 0, 'historicos': 0, 'empenhos': 0, 'itens': 0, 'arquivos': 0}
        
        stats = {
            'contratos_processados': 0,
            'historicos': 0,
            'empenhos': 0,
            'itens': 0,
            'arquivos': 0,
        }
        
        # Processa cada contrato individualmente (cada um em sua própria transação)
        for i, contrato_data in enumerate(contratos_a_processar, 1):
            contrato_id = str(contrato_data.get("id"))
            print(f"Processando contrato {i}/{len(contratos_a_processar)}: {contrato_data.get('numero', contrato_id)}")
            
            try:
                with transaction.atomic():
                    # Salva apenas o contrato (dados básicos)
                    # Dados detalhados (histórico, empenhos, itens, arquivos) serão
                    # sincronizados sob demanda quando o usuário selecionar a aba correspondente
                    contrato = self._save_contrato(contrato_data, uasg_code)
                    stats['contratos_processados'] += 1
            except Exception as e:
                print(f"⚠ Erro ao processar contrato {contrato_id}: {e}")
                import traceback
                traceback.print_exc()
                # Continua processando os próximos contratos mesmo se um falhar
                continue
        
        print(f"✅ Sincronização da UASG {uasg_code} concluída: {stats}")
        return stats
    
    def sync_contrato_detalhes(
        self, 
        contrato_id: str,
        data_types: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Sincroniza detalhes de um contrato específico.
        
        Args:
            contrato_id: ID do contrato
            data_types: Lista opcional de tipos de dados a sincronizar.
                       Se None, sincroniza todos ('historico', 'empenhos', 'itens', 'arquivos').
                       Valores válidos: 'historico', 'empenhos', 'itens', 'arquivos'
        
        Returns:
            Dicionário com estatísticas da sincronização
        """
        try:
            contrato = Contrato.objects.get(id=contrato_id)
        except Contrato.DoesNotExist:
            print(f"⚠ Contrato {contrato_id} não encontrado.")
            return {'historicos': 0, 'empenhos': 0, 'itens': 0, 'arquivos': 0}
        
        # Se não especificado, sincroniza todos
        if data_types is None:
            data_types = ['historico', 'empenhos', 'itens', 'arquivos']
        
        stats = {
            'historicos': 0,
            'empenhos': 0,
            'itens': 0,
            'arquivos': 0,
        }
        
        # Sincroniza cada tipo solicitado
        for data_type in data_types:
            if data_type in ['historico', 'empenhos', 'itens', 'arquivos']:
                result = self._sync_single_related_dataset(contrato, data_type)
                stats.update(result)
        
        print(f"✅ Detalhes do contrato {contrato_id} sincronizados: {stats}")
        return stats
    
    def _sync_single_related_dataset(
        self, 
        contrato: Contrato, 
        data_type: str
    ) -> Dict[str, int]:
        """
        Sincroniza um único tipo de dado relacionado (histórico, empenhos, itens ou arquivos).
        
        Args:
            contrato: Instância do Contrato
            data_type: Tipo de dado ('historico', 'empenhos', 'itens' ou 'arquivos')
        
        Returns:
            Dicionário com estatísticas da sincronização
        """
        from django.utils import timezone
        
        # Validação do tipo de dado
        valid_types = ['historico', 'empenhos', 'itens', 'arquivos']
        if data_type not in valid_types:
            raise ValueError(f"Tipo de dado inválido: {data_type}. Deve ser um de {valid_types}")
        
        print(f"🔄 Sincronizando {data_type} do contrato {contrato.id}...")
        
        # Busca dados atualizados do contrato para obter links atualizados
        url = f"{self.BASE_URL}/contrato/{contrato.id}"
        contrato_data = self._fetch_api_data(url)
        
        if not contrato_data:
            print(f"⚠ Não foi possível obter dados atualizados do contrato {contrato.id}.")
            return {data_type: 0}
        
        # Se retornou lista, pega o primeiro item
        if isinstance(contrato_data, list) and contrato_data:
            contrato_data = contrato_data[0]
        
        links = contrato_data.get("links", {})
        link_key = data_type
        
        if link_key not in links:
            print(f"⚠ Link para {data_type} não encontrado no contrato {contrato.id}.")
            return {data_type: 0}
        
        # Busca e salva dados
        data = self._fetch_api_data(links[link_key])
        count = 0
        
        if data:
            # Mapeia tipo de dado para método de salvamento
            save_methods = {
                'historico': (self._save_historico, 'historico_atualizado_em'),
                'empenhos': (self._save_empenhos, 'empenhos_atualizados_em'),
                'itens': (self._save_itens, 'itens_atualizados_em'),
                'arquivos': (self._save_arquivos, 'arquivos_atualizados_em'),
            }
            
            save_method, field_name = save_methods[data_type]
            save_method(contrato, data)
            count = len(data)
            
            # Atualiza timestamp de sincronização
            setattr(contrato, field_name, timezone.now())
            contrato.save(update_fields=[field_name])
            
            print(f"✅ {data_type.capitalize()} do contrato {contrato.id} sincronizado: {count} registros")
        
        return {data_type: count}
