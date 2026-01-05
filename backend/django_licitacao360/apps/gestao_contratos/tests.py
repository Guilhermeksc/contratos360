"""
Testes para o modelo Contrato e serviço de ingestão
"""
import json
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.exceptions import ValidationError

from django_licitacao360.apps.uasgs.models import Uasg

from .models import Contrato
from .services.ingestion import ComprasNetIngestionService


class ContratoModelTest(TestCase):
    """Testes para o modelo Contrato"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.uasg = Uasg.objects.create(
            id_uasg=123456,
            uasg=123456,
            sigla_om='UASG TESTE',
            nome_om='UASG Teste',
            classificacao='Nao informado'
        )
    
    def test_create_contrato_with_all_fields(self):
        """Testa criação de contrato com todos os campos preenchidos"""
        contrato = Contrato.objects.create(
            id='test-contrato-001',
            uasg=self.uasg,
            numero='123/2024',
            licitacao_numero='456/2024',
            processo='PROC-001',
            fornecedor_nome='Fornecedor Teste LTDA',
            fornecedor_cnpj='12.345.678/0001-90',
            objeto='Objeto de teste do contrato',
            valor_global=Decimal('1000000.50'),
            vigencia_inicio=date(2024, 1, 1),
            vigencia_fim=date(2024, 12, 31),
            tipo='Contrato de Fornecimento',
            modalidade='Pregão Eletrônico',
            contratante_orgao_unidade_gestora_codigo='123456',
            contratante_orgao_unidade_gestora_nome_resumido='UG Teste',
            manual=False,
            raw_json={'test': 'data'}
        )
        
        # Verifica se foi salvo corretamente
        self.assertIsNotNone(contrato.id)
        self.assertEqual(contrato.numero, '123/2024')
        self.assertEqual(contrato.valor_global, Decimal('1000000.50'))
        self.assertEqual(contrato.fornecedor_nome, 'Fornecedor Teste LTDA')
    
    def test_valor_global_decimal_field(self):
        """Testa especificamente o campo valor_global com diferentes valores"""
        # Teste 1: Valor com 2 casas decimais
        contrato1 = Contrato.objects.create(
            id='test-valor-001',
            uasg=self.uasg,
            valor_global=Decimal('123456.78')
        )
        self.assertEqual(contrato1.valor_global, Decimal('123456.78'))
        
        # Teste 2: Valor inteiro
        contrato2 = Contrato.objects.create(
            id='test-valor-002',
            uasg=self.uasg,
            valor_global=Decimal('500000')
        )
        self.assertEqual(contrato2.valor_global, Decimal('500000.00'))
        
        # Teste 3: Valor zero
        contrato3 = Contrato.objects.create(
            id='test-valor-003',
            uasg=self.uasg,
            valor_global=Decimal('0.00')
        )
        self.assertEqual(contrato3.valor_global, Decimal('0.00'))
        
        # Teste 4: Valor None (deve ser permitido)
        contrato4 = Contrato.objects.create(
            id='test-valor-004',
            uasg=self.uasg,
            valor_global=None
        )
        self.assertIsNone(contrato4.valor_global)
    
    def test_valor_global_validation(self):
        """Testa validação do campo valor_global"""
        # Valor negativo deve falhar
        with self.assertRaises(ValidationError):
            contrato = Contrato(
                id='test-valor-negativo',
                uasg=self.uasg,
                valor_global=Decimal('-100.00')
            )
            contrato.full_clean()


class ComprasNetIngestionServiceTest(TestCase):
    """Testes para o serviço de ingestão da API ComprasNet"""
    
    BASE_URL = "https://contratos.comprasnet.gov.br/api"
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.uasg = Uasg.objects.create(
            id_uasg=123456,
            uasg=123456,
            sigla_om='UASG TESTE',
            nome_om='UASG Teste',
            classificacao='Nao informado'
        )
        self.service = ComprasNetIngestionService()
    
    def _create_mock_contrato_data(self, valor_global=None):
        """Cria dados mockados de um contrato da API"""
        return {
            "id": "test-contrato-api-001",
            "numero": "123/2024",
            "licitacao_numero": "456/2024",
            "processo": "PROC-001",
            "objeto": "Objeto de teste do contrato via API",
            "valor_global": valor_global,
            "vigencia_inicio": "2024-01-01",
            "vigencia_fim": "2024-12-31",
            "tipo": "Contrato de Fornecimento",
            "modalidade": "Pregão Eletrônico",
            "fornecedor": {
                "nome": "Fornecedor Teste LTDA",
                "cnpj_cpf_idgener": "12.345.678/0001-90"
            },
            "contratante": {
                "orgao": {
                    "unidade_gestora": {
                        "codigo": "123456",
                        "nome_resumido": "UG Teste"
                    }
                }
            }
        }
    
    @patch('gestao_contratos.services.ingestion.requests.get')
    def test_save_contrato_with_valor_global_string_com_virgula(self, mock_get):
        """Testa salvamento de contrato com valor_global como string com vírgula"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = [self._create_mock_contrato_data(valor_global="1.000.000,50")]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Executa a sincronização
        stats = self.service.sync_contratos_por_uasg('123456')
        
        # Verifica se o contrato foi criado
        self.assertEqual(stats['contratos_processados'], 1)
        
        # Busca o contrato no banco
        contrato = Contrato.objects.get(id='test-contrato-api-001')
        
        # Verifica se valor_global foi salvo corretamente
        self.assertIsNotNone(contrato.valor_global)
        self.assertEqual(contrato.valor_global, Decimal('1000000.50'))
        self.assertEqual(str(contrato.valor_global), '1000000.50')
    
    @patch('gestao_contratos.services.ingestion.requests.get')
    def test_save_contrato_with_valor_global_string_com_ponto(self, mock_get):
        """Testa salvamento de contrato com valor_global como string com ponto"""
        mock_response = MagicMock()
        mock_response.json.return_value = [self._create_mock_contrato_data(valor_global="500000.75")]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        stats = self.service.sync_contratos_por_uasg('123456')
        
        self.assertEqual(stats['contratos_processados'], 1)
        contrato = Contrato.objects.get(id='test-contrato-api-001')
        
        self.assertIsNotNone(contrato.valor_global)
        self.assertEqual(contrato.valor_global, Decimal('500000.75'))
    
    @patch('gestao_contratos.services.ingestion.requests.get')
    def test_save_contrato_with_valor_global_numerico(self, mock_get):
        """Testa salvamento de contrato com valor_global como número"""
        mock_response = MagicMock()
        mock_response.json.return_value = [self._create_mock_contrato_data(valor_global=750000.25)]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        stats = self.service.sync_contratos_por_uasg('123456')
        
        self.assertEqual(stats['contratos_processados'], 1)
        contrato = Contrato.objects.get(id='test-contrato-api-001')
        
        self.assertIsNotNone(contrato.valor_global)
        # Float pode ter pequenas diferenças, então verificamos se está próximo
        self.assertAlmostEqual(float(contrato.valor_global), 750000.25, places=2)
    
    @patch('gestao_contratos.services.ingestion.requests.get')
    def test_save_contrato_with_valor_global_none(self, mock_get):
        """Testa salvamento de contrato com valor_global None"""
        mock_response = MagicMock()
        mock_response.json.return_value = [self._create_mock_contrato_data(valor_global=None)]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        stats = self.service.sync_contratos_por_uasg('123456')
        
        self.assertEqual(stats['contratos_processados'], 1)
        contrato = Contrato.objects.get(id='test-contrato-api-001')
        
        # valor_global pode ser None
        self.assertIsNone(contrato.valor_global)
    
    @patch('gestao_contratos.services.ingestion.requests.get')
    def test_save_contrato_with_valor_global_string_vazia(self, mock_get):
        """Testa salvamento de contrato com valor_global como string vazia"""
        mock_response = MagicMock()
        mock_response.json.return_value = [self._create_mock_contrato_data(valor_global="")]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        stats = self.service.sync_contratos_por_uasg('123456')
        
        self.assertEqual(stats['contratos_processados'], 1)
        contrato = Contrato.objects.get(id='test-contrato-api-001')
        
        # String vazia deve resultar em None
        self.assertIsNone(contrato.valor_global)
    
    @patch('gestao_contratos.services.ingestion.requests.get')
    def test_save_contrato_with_all_fields_from_api(self, mock_get):
        """Testa salvamento de contrato com TODOS os campos da API"""
        contrato_data = {
            "id": "test-completo-001",
            "numero": "999/2024",
            "licitacao_numero": "888/2024",
            "processo": "PROC-999",
            "objeto": "Objeto completo de teste",
            "valor_global": "2.500.000,99",
            "vigencia_inicio": "2024-01-15",
            "vigencia_fim": "2024-12-15",
            "tipo": "Contrato de Serviço",
            "modalidade": "Tomada de Preços",
            "fornecedor": {
                "nome": "Empresa Completa LTDA",
                "cnpj_cpf_idgener": "98.765.432/0001-10"
            },
            "contratante": {
                "orgao": {
                    "unidade_gestora": {
                        "codigo": "654321",
                        "nome_resumido": "UG Completa"
                    }
                }
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = [contrato_data]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        stats = self.service.sync_contratos_por_uasg('123456')
        
        self.assertEqual(stats['contratos_processados'], 1)
        
        # Busca o contrato e verifica TODOS os campos
        contrato = Contrato.objects.get(id='test-completo-001')
        
        # Verifica cada campo individualmente
        self.assertEqual(contrato.id, 'test-completo-001')
        self.assertEqual(contrato.uasg, self.uasg)
        self.assertEqual(contrato.numero, '999/2024')
        self.assertEqual(contrato.licitacao_numero, '888/2024')
        self.assertEqual(contrato.processo, 'PROC-999')
        self.assertEqual(contrato.objeto, 'Objeto completo de teste')
        self.assertEqual(contrato.valor_global, Decimal('2500000.99'))
        self.assertEqual(contrato.vigencia_inicio, date(2024, 1, 15))
        self.assertEqual(contrato.vigencia_fim, date(2024, 12, 15))
        self.assertEqual(contrato.tipo, 'Contrato de Serviço')
        self.assertEqual(contrato.modalidade, 'Tomada de Preços')
        self.assertEqual(contrato.fornecedor_nome, 'Empresa Completa LTDA')
        self.assertEqual(contrato.fornecedor_cnpj, '98.765.432/0001-10')
        self.assertEqual(contrato.contratante_orgao_unidade_gestora_codigo, '654321')
        self.assertEqual(contrato.contratante_orgao_unidade_gestora_nome_resumido, 'UG Completa')
        self.assertFalse(contrato.manual)
        self.assertIsNotNone(contrato.raw_json)
        self.assertEqual(contrato.raw_json['id'], 'test-completo-001')
    
    def test_parse_decimal_method(self):
        """Testa o método _parse_decimal diretamente"""
        # Teste com vírgula
        result = self.service._parse_decimal("1.234.567,89")
        self.assertEqual(result, Decimal('1234567.89'))
        
        # Teste com ponto
        result = self.service._parse_decimal("500000.50")
        self.assertEqual(result, Decimal('500000.50'))
        
        # Teste com None
        result = self.service._parse_decimal(None)
        self.assertIsNone(result)
        
        # Teste com string vazia
        result = self.service._parse_decimal("")
        self.assertIsNone(result)
        
        # Teste com número inteiro como string
        result = self.service._parse_decimal("1000000")
        self.assertEqual(result, Decimal('1000000'))
        
        # Teste com valor inválido
        result = self.service._parse_decimal("abc")
        self.assertIsNone(result)
    
    @patch('gestao_contratos.services.ingestion.requests.get')
    def test_save_contrato_valor_global_com_formatos_diferentes(self, mock_get):
        """Testa diferentes formatos de valor_global que podem vir da API"""
        formatos_teste = [
            ("1.000.000,50", Decimal('1000000.50')),
            ("500000,75", Decimal('500000.75')),
            ("750.000", Decimal('750000')),
            ("1000000.25", Decimal('1000000.25')),
            (1000000.50, Decimal('1000000.50')),
            ("0,00", Decimal('0.00')),
            ("0.00", Decimal('0.00')),
        ]
        
        for idx, (valor_input, valor_esperado) in enumerate(formatos_teste):
            with self.subTest(valor_input=valor_input):
                contrato_data = self._create_mock_contrato_data(valor_global=valor_input)
                contrato_data["id"] = f"test-format-{idx}"
                
                mock_response = MagicMock()
                mock_response.json.return_value = [contrato_data]
                mock_response.raise_for_status = MagicMock()
                mock_get.return_value = mock_response
                
                stats = self.service.sync_contratos_por_uasg('123456')
                
                self.assertEqual(stats['contratos_processados'], 1)
                contrato = Contrato.objects.get(id=f"test-format-{idx}")
                
                if valor_input is not None and valor_input != "":
                    self.assertIsNotNone(contrato.valor_global, 
                                        f"valor_global não foi salvo para entrada: {valor_input}")
                    self.assertEqual(contrato.valor_global, valor_esperado,
                                   f"valor_global incorreto para entrada: {valor_input}")

