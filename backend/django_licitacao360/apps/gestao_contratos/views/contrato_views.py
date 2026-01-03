"""
Views para Contrato
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from django.utils import timezone
from django.db import models
from datetime import timedelta

from ..models import Contrato
from ..serializers import (
    ContratoSerializer,
    ContratoDetailSerializer,
    ContratoCreateSerializer,
    ContratoUpdateSerializer,
)
from ..services.ingestion import ComprasNetIngestionService


class ContratoFilter(filters.FilterSet):
    """Filtros para Contrato"""
    uasg = filters.CharFilter(field_name='uasg__uasg_code')
    status = filters.CharFilter(field_name='status__status')
    manual = filters.BooleanFilter()
    vigencia_fim__gte = filters.DateFilter(field_name='vigencia_fim', lookup_expr='gte')
    vigencia_fim__lte = filters.DateFilter(field_name='vigencia_fim', lookup_expr='lte')
    fornecedor_cnpj = filters.CharFilter(field_name='fornecedor_cnpj', lookup_expr='icontains')
    
    class Meta:
        model = Contrato
        fields = ['uasg', 'status', 'manual', 'tipo', 'modalidade']


class ContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Contrato
    """
    queryset = Contrato.objects.select_related('uasg', 'status').prefetch_related(
        'registros_status',
        'registros_mensagem'
    ).all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ContratoFilter
    search_fields = ['numero', 'processo', 'fornecedor_nome', 'objeto']
    ordering_fields = ['vigencia_fim', 'numero', 'valor_global', 'created_at']
    ordering = ['-vigencia_fim', 'numero']
    
    def get_serializer_class(self):
        """Retorna serializer apropriado para cada ação"""
        if self.action == 'create':
            return ContratoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContratoUpdateSerializer
        elif self.action == 'retrieve':
            return ContratoDetailSerializer
        return ContratoSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def vencidos(self, request):
        """Retorna contratos vencidos"""
        hoje = timezone.now().date()
        contratos = self.queryset.filter(vigencia_fim__lt=hoje)
        serializer = self.get_serializer(contratos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def proximos_vencer(self, request):
        """Retorna contratos próximos a vencer (próximos 30 dias)"""
        hoje = timezone.now().date()
        proximos_30_dias = hoje + timedelta(days=30)
        contratos = self.queryset.filter(
            vigencia_fim__gte=hoje,
            vigencia_fim__lte=proximos_30_dias
        )
        serializer = self.get_serializer(contratos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def ativos(self, request):
        """
        Retorna todos os contratos (sem filtro de vigência).
        Inclui contratos ativos, vencidos e sem data de fim.
        """
        contratos = self.queryset.all()
        serializer = self.get_serializer(contratos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='sync')
    def sync(self, request):
        """Sincroniza contratos de uma UASG específica"""
        import traceback
        import logging
        
        logger = logging.getLogger(__name__)
        uasg_code = request.query_params.get('uasg') or request.data.get('uasg')
        
        if not uasg_code:
            response = Response(
                {'error': 'Parâmetro "uasg" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
            # Garante headers CORS mesmo em erro
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        try:
            logger.info(f'Iniciando sincronização da UASG {uasg_code}')
            service = ComprasNetIngestionService()
            stats = service.sync_contratos_por_uasg(uasg_code)
            
            logger.info(f'Sincronização da UASG {uasg_code} concluída: {stats}')
            response = Response({
                'success': True,
                'uasg': uasg_code,
                'stats': stats,
                'message': f'Sincronização da UASG {uasg_code} concluída com sucesso'
            })
            response['Access-Control-Allow-Origin'] = '*'
            return response
                    
        except (SystemExit, KeyboardInterrupt) as e:
            # Captura SystemExit do Gunicorn (quando worker é morto)
            logger.error(f'Worker abortado durante sincronização da UASG {uasg_code}: {str(e)}')
            response = Response(
                {
                    'success': False,
                    'error': 'Sincronização interrompida pelo servidor. A operação pode ter demorado muito tempo.',
                    'message': f'A sincronização da UASG {uasg_code} foi interrompida. Tente novamente ou sincronize em lotes menores.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f'Erro ao sincronizar UASG {uasg_code}: {str(e)}\n{error_traceback}')
            response = Response(
                {
                    'success': False,
                    'error': str(e),
                    'traceback': error_traceback if request.query_params.get('debug') == 'true' else None,
                    'message': f'Erro ao sincronizar UASG {uasg_code}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
    
    @action(detail=True, methods=['get'], url_path='detalhes', permission_classes=[AllowAny])
    def detalhes(self, request, pk=None):
        """Retorna detalhes completos de um contrato"""
        from django.core.exceptions import ObjectDoesNotExist
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Usa queryset otimizado para detalhes
            contrato = Contrato.objects.select_related(
                'uasg',
                'status',
                'links',
                'fiscalizacao',
                'dados_manuais'
            ).prefetch_related(
                'registros_status',
                'registros_mensagem',
                'historicos',
                'empenhos',
                'itens',
                'arquivos'
            ).get(id=pk)
            
            serializer = ContratoDetailSerializer(contrato)
            response = Response(serializer.data)
            response['Access-Control-Allow-Origin'] = '*'
            return response
            
        except ObjectDoesNotExist:
            logger.warning(f'Contrato {pk} não encontrado')
            response = Response(
                {'error': f'Contrato {pk} não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f'Erro ao buscar detalhes do contrato {pk}: {str(e)}\n{error_traceback}')
            response = Response(
                {
                    'error': str(e),
                    'traceback': error_traceback if request.query_params.get('debug') == 'true' else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
    
    @action(
        detail=True, 
        methods=['post'], 
        url_path='sincronizar/historico',
        permission_classes=[AllowAny]
    )
    def sincronizar_historico(self, request, pk=None):
        """Sincroniza histórico de um contrato específico"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            contrato = self.get_object()
            service = ComprasNetIngestionService()
            result = service._sync_single_related_dataset(contrato, 'historico')
            
            logger.info(f'Histórico do contrato {pk} sincronizado: {result}')
            response = Response({
                'success': True,
                'contrato_id': pk,
                'stats': result,
                'message': 'Histórico sincronizado com sucesso'
            })
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            import traceback
            logger.error(f'Erro ao sincronizar histórico do contrato {pk}: {str(e)}')
            response = Response(
                {
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response

    @action(
        detail=True, 
        methods=['post'], 
        url_path='sincronizar/empenhos',
        permission_classes=[AllowAny]
    )
    def sincronizar_empenhos(self, request, pk=None):
        """Sincroniza empenhos de um contrato específico"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            contrato = self.get_object()
            service = ComprasNetIngestionService()
            result = service._sync_single_related_dataset(contrato, 'empenhos')
            
            logger.info(f'Empenhos do contrato {pk} sincronizados: {result}')
            response = Response({
                'success': True,
                'contrato_id': pk,
                'stats': result,
                'message': 'Empenhos sincronizados com sucesso'
            })
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            import traceback
            logger.error(f'Erro ao sincronizar empenhos do contrato {pk}: {str(e)}')
            response = Response(
                {
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response

    @action(
        detail=True, 
        methods=['post'], 
        url_path='sincronizar/itens',
        permission_classes=[AllowAny]
    )
    def sincronizar_itens(self, request, pk=None):
        """Sincroniza itens de um contrato específico"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            contrato = self.get_object()
            service = ComprasNetIngestionService()
            result = service._sync_single_related_dataset(contrato, 'itens')
            
            logger.info(f'Itens do contrato {pk} sincronizados: {result}')
            response = Response({
                'success': True,
                'contrato_id': pk,
                'stats': result,
                'message': 'Itens sincronizados com sucesso'
            })
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            import traceback
            logger.error(f'Erro ao sincronizar itens do contrato {pk}: {str(e)}')
            response = Response(
                {
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response

    @action(
        detail=True, 
        methods=['post'], 
        url_path='sincronizar/arquivos',
        permission_classes=[AllowAny]
    )
    def sincronizar_arquivos(self, request, pk=None):
        """Sincroniza arquivos de um contrato específico"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            contrato = self.get_object()
            service = ComprasNetIngestionService()
            result = service._sync_single_related_dataset(contrato, 'arquivos')
            
            logger.info(f'Arquivos do contrato {pk} sincronizados: {result}')
            response = Response({
                'success': True,
                'contrato_id': pk,
                'stats': result,
                'message': 'Arquivos sincronizados com sucesso'
            })
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            import traceback
            logger.error(f'Erro ao sincronizar arquivos do contrato {pk}: {str(e)}')
            response = Response(
                {
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc() if request.query_params.get('debug') == 'true' else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response


class ContratoDetalhesView(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para detalhes completos de um contrato
    Retorna contrato + status + registros + links + fiscalização + dados offline
    """
    queryset = Contrato.objects.select_related(
        'uasg',
        'status',
        'links',
        'fiscalizacao',
        'dados_manuais'
    ).prefetch_related(
        'registros_status',
        'registros_mensagem',
        'historicos',
        'empenhos',
        'itens',
        'arquivos'
    ).all()
    serializer_class = ContratoDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

