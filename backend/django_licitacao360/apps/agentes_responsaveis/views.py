from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
import logging
from .models import (
    AgenteResponsavel,
    AgenteResponsavelFuncao,
    PostoGraduacao,
    Especializacao,
)
from .serializers import (
    AgenteResponsavelFuncaoSerializer,
    AgenteResponsavelSerializer,
    AgenteResponsavelDetailSerializer,
    PostoGraduacaoSerializer,
    EspecializacaoSerializer,
)

try:
    from .export import export_agentes_responsaveis_to_xlsx
except ImportError:  # pragma: no cover - optional feature still in desenvolvimento
    export_agentes_responsaveis_to_xlsx = None

try:
    from .import_xlsx import import_agentes_responsaveis_from_xlsx
except ImportError:  # pragma: no cover - optional feature still in desenvolvimento
    import_agentes_responsaveis_from_xlsx = None

logger = logging.getLogger(__name__)


class AgenteResponsavelFuncaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgenteResponsavelFuncao.objects.all()
    serializer_class = AgenteResponsavelFuncaoSerializer


class AgentesResponsaveisViewSet(viewsets.ModelViewSet):
    queryset = AgenteResponsavel.objects.all()
    serializer_class = AgenteResponsavelSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AgenteResponsavelDetailSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        # 🔹 Filtro opcional: ?ativo=true/false
        ativo_param = request.query_params.get('ativo')
        queryset = self.get_queryset().prefetch_related('funcoes')
        if ativo_param is not None:
            if ativo_param.lower() == 'true':
                queryset = queryset.filter(ativo=True)
            elif ativo_param.lower() == 'false':
                queryset = queryset.filter(ativo=False)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # 🔹 Endpoints auxiliares
    @action(detail=False, methods=['get'], url_path='postos-graduacoes', url_name='postos-graduacoes')
    def postos_graduacoes(self, request):
        """Retorna todos os postos/graduações disponíveis"""
        postos = PostoGraduacao.objects.all()
        serializer = PostoGraduacaoSerializer(postos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='funcoes', url_name='funcoes')
    def funcoes(self, request):
        """Retorna todas as funções disponíveis"""
        funcoes = AgenteResponsavelFuncao.objects.all()
        serializer = AgenteResponsavelFuncaoSerializer(funcoes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='especializacoes', url_name='especializacoes')
    def especializacoes(self, request):
        """Retorna todas as especializações disponíveis"""
        especializacoes = Especializacao.objects.all()
        serializer = EspecializacaoSerializer(especializacoes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='export', url_name='export')
    def export(self, request):
        if not export_agentes_responsaveis_to_xlsx:
            return Response({'error': 'Endpoint de exportação ainda não está configurado'}, status=501)

        logger.info("Iniciando exportação dos agentes responsáveis")
        try:
            response = export_agentes_responsaveis_to_xlsx()
            logger.info("Exportação concluída com sucesso")
            return response
        except Exception as e:
            logger.error(f"Erro durante a exportação: {str(e)}")
            raise

    @action(detail=False, methods=['post'], url_path='import', url_name='import', parser_classes=[MultiPartParser])
    def import_file(self, request):
        if not import_agentes_responsaveis_from_xlsx:
            return Response({'error': 'Endpoint de importação ainda não está configurado'}, status=501)

        logger.info("Iniciando importação dos agentes responsáveis")
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'Nenhum arquivo enviado'}, status=400)

            result = import_agentes_responsaveis_from_xlsx(file)
            logger.info("Importação concluída com sucesso")
            return Response({'success': True, 'message': 'Importação concluída com sucesso', 'details': result})
        except Exception as e:
            logger.error(f"Erro durante a importação: {str(e)}")
            return Response({'error': str(e)}, status=400)