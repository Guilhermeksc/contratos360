"""
Testes de integração com a API real do ComprasNet
Execute dentro do Docker: docker compose exec backend python manage.py test gestao_contratos.tests_integration
"""
from decimal import Decimal
from django.test import TestCase
from django.db import transaction

from django_licitacao360.apps.uasgs.models import Uasg

from .models import Contrato
from .services.ingestion import ComprasNetIngestionService


class ComprasNetIntegrationTest(TestCase):
    """Testes de integração com a API real do ComprasNet"""
    
    def setUp(self):
        """Configuração inicial"""
        self.service = ComprasNetIngestionService()
        self.uasg_code = '787010'
    
    def test_sync_uasg_787010_and_verify_all_fields(self):
        """
        Testa sincronização real da UASG 787010 e verifica se TODOS os campos
        estão sendo salvos corretamente, especialmente valor_global
        """
        print(f"\n{'='*80}")
        print(f"Testando sincronização da UASG {self.uasg_code}")
        print(f"{'='*80}\n")
        
        # Sincroniza a UASG
        stats = self.service.sync_contratos_por_uasg(self.uasg_code)
        
        print(f"\nEstatísticas da sincronização: {stats}")
        print(f"Contratos processados: {stats.get('contratos_processados', 0)}\n")
        
        # Verifica se pelo menos um contrato foi processado
        contratos_count = Contrato.objects.filter(uasg__uasg=self.uasg_code).count()
        self.assertGreater(contratos_count, 0, 
                          f"Nenhum contrato foi encontrado para a UASG {self.uasg_code}")
        
        print(f"Total de contratos salvos: {contratos_count}\n")
        
        # Verifica cada contrato individualmente
        contratos = Contrato.objects.filter(uasg__uasg=self.uasg_code)[:10]  # Limita a 10 para não sobrecarregar
        
        campos_verificados = {
            'id': 0,
            'uasg': 0,
            'numero': 0,
            'licitacao_numero': 0,
            'processo': 0,
            'fornecedor_nome': 0,
            'fornecedor_cnpj': 0,
            'objeto': 0,
            'valor_global': 0,  # Campo crítico!
            'vigencia_inicio': 0,
            'vigencia_fim': 0,
            'tipo': 0,
            'modalidade': 0,
            'contratante_orgao_unidade_gestora_codigo': 0,
            'contratante_orgao_unidade_gestora_nome_resumido': 0,
            'raw_json': 0,
        }
        
        problemas_encontrados = []
        
        for idx, contrato in enumerate(contratos, 1):
            print(f"\n--- Contrato {idx}/{len(contratos)} ---")
            print(f"ID: {contrato.id}")
            print(f"Número: {contrato.numero or 'N/A'}")
            
            # Verifica cada campo
            if contrato.id:
                campos_verificados['id'] += 1
            if contrato.uasg:
                campos_verificados['uasg'] += 1
            if contrato.numero:
                campos_verificados['numero'] += 1
            if contrato.licitacao_numero:
                campos_verificados['licitacao_numero'] += 1
            if contrato.processo:
                campos_verificados['processo'] += 1
            if contrato.fornecedor_nome:
                campos_verificados['fornecedor_nome'] += 1
            if contrato.fornecedor_cnpj:
                campos_verificados['fornecedor_cnpj'] += 1
            if contrato.objeto:
                campos_verificados['objeto'] += 1
            
            # VERIFICAÇÃO CRÍTICA: valor_global
            if contrato.valor_global is not None:
                campos_verificados['valor_global'] += 1
                print(f"✅ valor_global: R$ {contrato.valor_global:,.2f}")
                
                # Verifica se o valor está no formato correto (Decimal)
                self.assertIsInstance(contrato.valor_global, Decimal, 
                                    f"valor_global deve ser Decimal, mas é {type(contrato.valor_global)}")
                
                # Verifica se o valor é positivo ou zero
                self.assertGreaterEqual(contrato.valor_global, Decimal('0.00'),
                                      f"valor_global deve ser >= 0, mas é {contrato.valor_global}")
            else:
                print(f"⚠️  valor_global: None (não foi salvo)")
                problemas_encontrados.append({
                    'contrato_id': contrato.id,
                    'campo': 'valor_global',
                    'problema': 'Valor não foi salvo (None)',
                    'raw_json_valor': contrato.raw_json.get('valor_global') if contrato.raw_json else None
                })
            
            if contrato.vigencia_inicio:
                campos_verificados['vigencia_inicio'] += 1
            if contrato.vigencia_fim:
                campos_verificados['vigencia_fim'] += 1
            if contrato.tipo:
                campos_verificados['tipo'] += 1
            if contrato.modalidade:
                campos_verificados['modalidade'] += 1
            if contrato.contratante_orgao_unidade_gestora_codigo:
                campos_verificados['contratante_orgao_unidade_gestora_codigo'] += 1
            if contrato.contratante_orgao_unidade_gestora_nome_resumido:
                campos_verificados['contratante_orgao_unidade_gestora_nome_resumido'] += 1
            if contrato.raw_json:
                campos_verificados['raw_json'] += 1
                
                # Verifica se o valor_global está no raw_json
                if contrato.raw_json.get('valor_global'):
                    raw_valor = contrato.raw_json.get('valor_global')
                    print(f"   valor_global no raw_json: {raw_valor} (tipo: {type(raw_valor).__name__})")
        
        # Relatório final
        print(f"\n{'='*80}")
        print("RELATÓRIO DE VERIFICAÇÃO DE CAMPOS")
        print(f"{'='*80}\n")
        
        total_contratos = len(contratos)
        for campo, quantidade in campos_verificados.items():
            porcentagem = (quantidade / total_contratos * 100) if total_contratos > 0 else 0
            status = "✅" if quantidade == total_contratos else "⚠️"
            print(f"{status} {campo:50} {quantidade:3}/{total_contratos} ({porcentagem:5.1f}%)")
        
        # Verifica problemas específicos com valor_global
        if problemas_encontrados:
            print(f"\n{'='*80}")
            print("PROBLEMAS ENCONTRADOS COM valor_global:")
            print(f"{'='*80}\n")
            for problema in problemas_encontrados:
                print(f"Contrato ID: {problema['contrato_id']}")
                print(f"  Campo: {problema['campo']}")
                print(f"  Problema: {problema['problema']}")
                print(f"  Valor no raw_json: {problema['raw_json_valor']}")
                print()
        
        # Assertions finais
        self.assertGreater(campos_verificados['valor_global'], 0,
                          "Nenhum contrato tem valor_global salvo! Isso indica um problema crítico.")
        
        # Verifica se pelo menos 50% dos contratos têm valor_global
        porcentagem_valor_global = (campos_verificados['valor_global'] / total_contratos * 100) if total_contratos > 0 else 0
        self.assertGreater(porcentagem_valor_global, 50,
                          f"Apenas {porcentagem_valor_global:.1f}% dos contratos têm valor_global. Esperado > 50%")
        
        print(f"\n✅ Teste concluído! {campos_verificados['valor_global']}/{total_contratos} contratos têm valor_global salvo.")
    
    def test_parse_decimal_with_real_api_formats(self):
        """Testa o método _parse_decimal com formatos reais que podem vir da API"""
        print("\nTestando _parse_decimal com formatos reais...\n")
        
        # Busca um contrato real para verificar o formato
        stats = self.service.sync_contratos_por_uasg(self.uasg_code)
        
        if stats.get('contratos_processados', 0) > 0:
            contrato = Contrato.objects.filter(uasg__uasg=self.uasg_code).first()
            
            if contrato and contrato.raw_json:
                raw_valor = contrato.raw_json.get('valor_global')
                if raw_valor:
                    print(f"Valor original da API: {raw_valor} (tipo: {type(raw_valor).__name__})")
                    parsed = self.service._parse_decimal(raw_valor)
                    print(f"Valor parseado: {parsed}")
                    print(f"Valor salvo no banco: {contrato.valor_global}")
                    
                    if parsed and contrato.valor_global:
                        self.assertEqual(parsed, contrato.valor_global,
                                       f"Valor parseado ({parsed}) não corresponde ao valor salvo ({contrato.valor_global})")
        
        # Testa formatos conhecidos
        formatos_teste = [
            ("1.000.000,50", Decimal('1000000.50')),
            ("500000,75", Decimal('500000.75')),
            ("750.000", Decimal('750000')),
            ("1000000.25", Decimal('1000000.25')),
            (1000000.50, Decimal('1000000.50')),
        ]
        
        for valor_input, valor_esperado in formatos_teste:
            resultado = self.service._parse_decimal(valor_input)
            self.assertEqual(resultado, valor_esperado,
                          f"Falha ao parsear {valor_input}: esperado {valor_esperado}, obtido {resultado}")



