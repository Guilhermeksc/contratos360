from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count, Value
from django.db.models.functions import Concat
import logging

logger = logging.getLogger(__name__)

from .models import Ata
from .serializers import AtaSerializer, AtaListagemSerializer
from django_licitacao360.apps.uasgs.models import Uasg


class AtaViewSet(viewsets.ModelViewSet):
    queryset = Ata.objects.all()
    serializer_class = AtaSerializer
    permission_classes = [AllowAny]
    filterset_fields = [
        "ano_ata",
        "cancelado",
        "cnpj_orgao",
        "codigo_unidade_orgao",
        "nome_orgao",
    ]
    search_fields = [
        "numero_ata_registro_preco",
        "numero_controle_pncp_ata",
        "numero_controle_pncp_compra",
        "objeto_contratacao",
        "nome_orgao",
        "nome_unidade_orgao",
    ]
    
    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na ação"""
        if self.action == 'list':
            return AtaListagemSerializer
        return AtaSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def por_orgao(self, request):
        """Retorna atas filtradas por CNPJ do órgão"""
        cnpj_orgao = request.query_params.get('cnpj_orgao')
        if not cnpj_orgao:
            return Response(
                {'error': 'CNPJ do órgão é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            atas = self.queryset.filter(cnpj_orgao=cnpj_orgao).order_by('-ano_ata', '-data_assinatura')
            serializer = self.get_serializer(atas, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao buscar atas por órgão {cnpj_orgao}: {str(e)}")
            return Response(
                {'error': 'Erro ao processar requisição'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def por_unidade(self, request):
        """Retorna atas filtradas por código da unidade"""
        codigo_unidade = request.query_params.get('codigo_unidade')
        if not codigo_unidade:
            return Response(
                {'error': 'Código da unidade é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            atas = self.queryset.filter(codigo_unidade_orgao=codigo_unidade).order_by('-ano_ata', '-data_assinatura')
            serializer = self.get_serializer(atas, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao buscar atas por unidade {codigo_unidade}: {str(e)}")
            return Response(
                {'error': 'Erro ao processar requisição'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def vigentes(self, request):
        """Retorna apenas atas vigentes (não canceladas e dentro do período de vigência)"""
        try:
            from django.utils import timezone
            agora = timezone.now()
            
            atas = self.queryset.filter(
                cancelado=0,
                vigencia_inicio__lte=agora,
                vigencia_fim__gte=agora
            ).order_by('-ano_ata', '-data_assinatura')
            
            serializer = self.get_serializer(atas, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao buscar atas vigentes: {str(e)}")
            return Response(
                {'error': 'Erro ao processar requisição'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def canceladas(self, request):
        """Retorna apenas atas canceladas"""
        try:
            atas = self.queryset.filter(cancelado=1).order_by('-data_cancelamento', '-ano_ata')
            serializer = self.get_serializer(atas, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao buscar atas canceladas: {str(e)}")
            return Response(
                {'error': 'Erro ao processar requisição'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def buscar_especifica(self, request):
        """Endpoint específico: busca ata por codigo_unidade_orgao + numero_compra + ano"""
        codigo_unidade_orgao = request.query_params.get('codigo_unidade_orgao')
        numero_compra = request.query_params.get('numero_compra')
        ano = request.query_params.get('ano')
        
        if not codigo_unidade_orgao or not numero_compra or not ano:
            return Response(
                {'error': 'Parâmetros obrigatórios: codigo_unidade_orgao, numero_compra e ano'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ano = int(ano)
            atas = self.queryset.filter(
                codigo_unidade_orgao=codigo_unidade_orgao,
                numero_compra=numero_compra,
                ano=ano
            ).order_by('-ano_ata', '-data_assinatura')
            
            serializer = self.get_serializer(atas, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'O parâmetro ano deve ser um número inteiro'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro ao buscar ata específica: {str(e)}")
            return Response(
                {'error': 'Erro ao processar requisição'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def unidades_por_ano(self, request):
        """Endpoint amplo: relaciona todos os codigo_unidade_orgao para cada ano"""
        try:
            # Agrupa por ano e codigo_unidade_orgao, contando quantas atas existem
            resultado = (
                self.queryset
                .values('ano', 'codigo_unidade_orgao')
                .annotate(total_atas=Count('numero_controle_pncp_ata'))
                .order_by('ano', 'codigo_unidade_orgao')
            )
            
            # Organiza os dados por ano e busca sigla_om do Uasg
            dados_por_ano = {}
            for item in resultado:
                ano = item['ano']
                if ano not in dados_por_ano:
                    dados_por_ano[ano] = []
                
                # Busca sigla_om do Uasg relacionado
                sigla_om = None
                codigo_unidade = item['codigo_unidade_orgao']
                if codigo_unidade:
                    try:
                        # Tenta converter para inteiro e buscar Uasg
                        codigo_int = int(codigo_unidade)
                        uasg = Uasg.objects.filter(uasg=codigo_int).first()
                        if uasg:
                            sigla_om = uasg.sigla_om
                    except (ValueError, TypeError):
                        # Se não conseguir converter, sigla_om permanece None
                        pass
                
                dados_por_ano[ano].append({
                    'codigo_unidade_orgao': codigo_unidade,
                    'sigla_om': sigla_om,
                    'total_atas': item['total_atas']
                })
            
            return Response(dados_por_ano)
        except Exception as e:
            logger.error(f"Erro ao buscar unidades por ano: {str(e)}")
            return Response(
                {'error': 'Erro ao processar requisição'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def atas_por_unidade_ano(self, request):
        """Endpoint: relaciona todos os numero_controle_pncp_ata para cada codigo_unidade_orgao para o ano"""
        codigo_unidade_orgao = request.query_params.get('codigo_unidade_orgao')
        ano = request.query_params.get('ano')
        
        if not codigo_unidade_orgao or not ano:
            return Response(
                {'error': 'Parâmetros obrigatórios: codigo_unidade_orgao e ano'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ano = int(ano)
            
            # Busca as atas filtradas
            atas = self.queryset.filter(
                codigo_unidade_orgao=codigo_unidade_orgao,
                ano=ano
            ).values(
                'numero_controle_pncp_ata',
                'numero_ata_registro_preco',
                'ano_ata',
                'objeto_contratacao',
                'data_assinatura',
                'vigencia_inicio',
                'vigencia_fim',
                'cancelado',
                'codigo_unidade_orgao',
                'numero_compra',
                'ano',
                'sequencial',
                'cnpj_orgao'
            ).order_by('-ano_ata', '-data_assinatura')
            
            # Busca sigla_om do Uasg relacionado uma vez
            sigla_om = None
            try:
                codigo_int = int(codigo_unidade_orgao)
                uasg = Uasg.objects.filter(uasg=codigo_int).first()
                if uasg:
                    sigla_om = uasg.sigla_om
            except (ValueError, TypeError):
                pass
            
            # Adiciona sigla_om a cada ata
            atas_list = []
            for ata in atas:
                ata_dict = dict(ata)
                ata_dict['sigla_om'] = sigla_om
                # Garante que objeto_contratacao e cnpj_orgao estejam presentes
                if 'objeto_contratacao' not in ata_dict:
                    ata_dict['objeto_contratacao'] = ''
                if 'cnpj_orgao' not in ata_dict:
                    ata_dict['cnpj_orgao'] = ''
                atas_list.append(ata_dict)
            
            resultado = {
                'codigo_unidade_orgao': codigo_unidade_orgao,
                'ano': ano,
                'total_atas': len(atas_list),
                'atas': atas_list
            }
            
            return Response(resultado)
        except ValueError:
            return Response(
                {'error': 'O parâmetro ano deve ser um número inteiro'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro ao buscar atas por unidade e ano: {str(e)}")
            return Response(
                {'error': 'Erro ao processar requisição'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
