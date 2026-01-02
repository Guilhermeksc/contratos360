from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from .models import (
    BibliografiaModel,
    FlashCardsModel,
    PerguntaMultiplaModel, 
    PerguntaVFModel, 
    PerguntaCorrelacaoModel,
    RespostaUsuario,
    QuestaoErradaAnonima
)
from .serializers import (
    BibliografiaSerializer,
    BibliografiaCreateUpdateSerializer,
    FlashCardsSerializer,
    FlashCardsCreateUpdateSerializer,
    PerguntaMultiplaSerializer,
    PerguntaMultiplaCreateUpdateSerializer,
    PerguntaVFSerializer,
    PerguntaVFCreateUpdateSerializer,
    PerguntaCorrelacaoSerializer,
    PerguntaCorrelacaoCreateUpdateSerializer,
    PerguntaResumoSerializer,
    RespostaUsuarioSerializer,
    RespostaUsuarioCreateSerializer,
    QuestaoErradaAnonimaSerializer
)


class BibliografiaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar bibliografias"""
    queryset = BibliografiaModel.objects.all()
    serializer_class = BibliografiaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['autor', 'materia']
    search_fields = ['titulo', 'autor', 'materia__materia', 'descricao']
    ordering_fields = ['id', 'titulo', 'autor', 'materia']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BibliografiaCreateUpdateSerializer
        return BibliografiaSerializer
    
    @action(detail=True, methods=['get'])
    def perguntas(self, request, pk=None):
        """Retorna todas as perguntas de uma bibliografia"""
        bibliografia = self.get_object()
        perguntas = []
        
        # Buscar perguntas múltipla escolha
        multiplas = PerguntaMultiplaModel.objects.filter(bibliografia=bibliografia)
        for pergunta in multiplas:
            perguntas.append({
                'id': pergunta.id,
                'tipo': pergunta.tipo,
                'tipo_display': pergunta.get_tipo_display(),
                'bibliografia_titulo': pergunta.bibliografia.titulo,
                'pergunta': pergunta.pergunta,
                'paginas': pergunta.paginas,
                'assunto': pergunta.assunto,
                'caiu_em_prova': pergunta.caiu_em_prova,
                'ano_prova': pergunta.ano_prova
            })
        
        # Buscar perguntas V/F
        vfs = PerguntaVFModel.objects.filter(bibliografia=bibliografia)
        for pergunta in vfs:
            perguntas.append({
                'id': pergunta.id,
                'tipo': pergunta.tipo,
                'tipo_display': pergunta.get_tipo_display(),
                'bibliografia_titulo': pergunta.bibliografia.titulo,
                'pergunta': pergunta.pergunta,
                'paginas': pergunta.paginas,
                'assunto': pergunta.assunto,
                'caiu_em_prova': pergunta.caiu_em_prova,
                'ano_prova': pergunta.ano_prova
            })
        
        # Buscar perguntas de correlação
        correlacoes = PerguntaCorrelacaoModel.objects.filter(bibliografia=bibliografia)
        for pergunta in correlacoes:
            perguntas.append({
                'id': pergunta.id,
                'tipo': pergunta.tipo,
                'tipo_display': pergunta.get_tipo_display(),
                'bibliografia_titulo': pergunta.bibliografia.titulo,
                'pergunta': pergunta.pergunta,
                'paginas': pergunta.paginas,
                'assunto': pergunta.assunto,
                'caiu_em_prova': pergunta.caiu_em_prova,
                'ano_prova': pergunta.ano_prova
            })
        
        # Ordenar por ID
        perguntas.sort(key=lambda x: x['id'])
        
        serializer = PerguntaResumoSerializer(perguntas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def flashcards(self, request, pk=None):
        """Retorna todos os flashcards de uma bibliografia"""
        bibliografia = self.get_object()
        flashcards = FlashCardsModel.objects.filter(bibliografia=bibliografia).order_by('id')
        serializer = FlashCardsSerializer(flashcards, many=True)
        return Response(serializer.data)


class FlashCardsViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar flash cards"""
    queryset = FlashCardsModel.objects.select_related('bibliografia').all()
    serializer_class = FlashCardsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bibliografia', 'assunto', 'prova', 'ano', 'caveira']
    search_fields = ['pergunta', 'resposta', 'assunto', 'bibliografia__titulo']
    ordering_fields = ['id', 'bibliografia__titulo', 'assunto', 'prova', 'ano', 'caveira']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FlashCardsCreateUpdateSerializer
        return FlashCardsSerializer


class PerguntaMultiplaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar perguntas de múltipla escolha"""
    queryset = PerguntaMultiplaModel.objects.select_related('bibliografia').all()
    serializer_class = PerguntaMultiplaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bibliografia', 'caiu_em_prova', 'ano_prova', 'resposta_correta', 'assunto']
    search_fields = ['pergunta', 'bibliografia__titulo', 'justificativa_resposta_certa', 'assunto']
    ordering_fields = ['id', 'bibliografia__titulo', 'caiu_em_prova', 'ano_prova', 'assunto']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PerguntaMultiplaCreateUpdateSerializer
        return PerguntaMultiplaSerializer


class PerguntaVFViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar perguntas de verdadeiro ou falso"""
    queryset = PerguntaVFModel.objects.select_related('bibliografia').all()
    serializer_class = PerguntaVFSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bibliografia', 'caiu_em_prova', 'ano_prova', 'assunto']
    search_fields = ['pergunta', 'afirmacao_verdadeira', 'afirmacao_falsa', 'assunto', 'bibliografia__titulo', 'justificativa_resposta_certa']
    ordering_fields = ['id', 'bibliografia__titulo', 'caiu_em_prova', 'ano_prova', 'assunto']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PerguntaVFCreateUpdateSerializer
        return PerguntaVFSerializer


class PerguntaCorrelacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar perguntas de correlação"""
    queryset = PerguntaCorrelacaoModel.objects.select_related('bibliografia').all()
    serializer_class = PerguntaCorrelacaoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bibliografia', 'caiu_em_prova', 'ano_prova', 'assunto']
    search_fields = ['pergunta', 'bibliografia__titulo', 'justificativa_resposta_certa', 'assunto']
    ordering_fields = ['id', 'bibliografia__titulo', 'caiu_em_prova', 'ano_prova', 'assunto']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PerguntaCorrelacaoCreateUpdateSerializer
        return PerguntaCorrelacaoSerializer


class RespostaUsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar respostas dos usuários
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RespostaUsuarioSerializer
    
    def get_queryset(self):
        """
        Usuários só veem suas próprias respostas
        Admins veem todas as respostas
        """
        queryset = RespostaUsuario.objects.select_related('usuario').all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(usuario=self.request.user)
        
        return queryset.order_by('-timestamp')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RespostaUsuarioCreateSerializer
        return RespostaUsuarioSerializer
    
    @action(detail=False, methods=['post'])
    def registrar_resposta(self, request):
        """
        Endpoint para registrar uma resposta do usuário
        POST /api/respostas-usuario/registrar_resposta/
        
        Body:
        {
            "pergunta_id": 1,
            "pergunta_tipo": "multipla",  // ou "vf" ou "correlacao"
            "resposta_usuario": "a",  // ou true/false para VF, ou objeto para correlação
            "bibliografia_id": 1,  // opcional
            "assunto": "Logística",  // opcional
            "afirmacao_sorteada_eh_verdadeira": true  // opcional, apenas para VF
        }
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"📥 Registrando resposta - Usuário: {request.user.username}, Dados: {request.data}")
        
        serializer = RespostaUsuarioCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Extrair informação sobre afirmação sorteada para VF
            afirmacao_sorteada_eh_verdadeira = request.data.get('afirmacao_sorteada_eh_verdadeira')
            
            # Verificar se a resposta está correta
            acertou = self._verificar_resposta(
                serializer.validated_data['pergunta_id'],
                serializer.validated_data['pergunta_tipo'],
                serializer.validated_data['resposta_usuario'],
                afirmacao_sorteada_eh_verdadeira
            )
            
            logger.info(f"✅ Verificação: Pergunta {serializer.validated_data['pergunta_id']} ({serializer.validated_data['pergunta_tipo']}) - Resposta: {serializer.validated_data['resposta_usuario']} - Acertou: {acertou}")
            
            serializer.validated_data['acertou'] = acertou
            resposta = serializer.save()
            
            # Se o usuário errou, registrar também na tabela anônima
            if not acertou:
                QuestaoErradaAnonima.objects.create(
                    pergunta_id=resposta.pergunta_id,
                    pergunta_tipo=resposta.pergunta_tipo,
                    bibliografia_id=resposta.bibliografia_id,
                    assunto=resposta.assunto
                )
                logger.info(f"📊 Questão errada registrada na tabela anônima - Pergunta ID: {resposta.pergunta_id}")
            
            logger.info(f"💾 Resposta salva - ID: {resposta.id}, Usuário: {resposta.usuario.username}, Acertou: {resposta.acertou}")
            
            return Response({
                'id': resposta.id,
                'acertou': resposta.acertou,
                'message': 'Resposta registrada com sucesso'
            }, status=status.HTTP_201_CREATED)
        
        logger.error(f"❌ Erro de validação: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _verificar_resposta(self, pergunta_id, pergunta_tipo, resposta_usuario, afirmacao_sorteada_eh_verdadeira=None):
        """
        Verifica se a resposta do usuário está correta
        """
        if pergunta_tipo == 'multipla':
            try:
                pergunta = PerguntaMultiplaModel.objects.get(id=pergunta_id)
                return pergunta.resposta_correta.lower() == resposta_usuario.lower()
            except PerguntaMultiplaModel.DoesNotExist:
                return False
        
        elif pergunta_tipo == 'vf':
            try:
                pergunta = PerguntaVFModel.objects.get(id=pergunta_id)
                # A resposta correta depende de qual afirmação foi sorteada
                # Se afirmacao_sorteada_eh_verdadeira é True, a resposta correta é True (Verdadeiro)
                # Se afirmacao_sorteada_eh_verdadeira é False, a resposta correta é False (Falso)
                # Se não foi informado, assume True (comportamento padrão)
                if afirmacao_sorteada_eh_verdadeira is not None:
                    resposta_correta = afirmacao_sorteada_eh_verdadeira
                else:
                    # Comportamento padrão: sempre True (assumindo que sempre mostra afirmação verdadeira)
                    resposta_correta = True
                
                return resposta_usuario == resposta_correta
            except PerguntaVFModel.DoesNotExist:
                return False
        
        elif pergunta_tipo == 'correlacao':
            try:
                pergunta = PerguntaCorrelacaoModel.objects.get(id=pergunta_id)
                # Converter resposta do usuário para formato do backend
                resposta_convertida = self._converter_resposta_correlacao(resposta_usuario)
                return pergunta.resposta_correta == resposta_convertida
            except PerguntaCorrelacaoModel.DoesNotExist:
                return False
        
        return False
    
    def _converter_resposta_correlacao(self, resposta_usuario):
        """
        Converte resposta de correlação do formato frontend para backend
        Frontend: {1: 'A', 2: 'B', 3: 'C'}
        Backend: {'0': '0', '1': '1', '2': '2'}
        """
        resposta_convertida = {}
        for key, letter in resposta_usuario.items():
            item_index = str(int(key) - 1)  # Converter 1,2,3 para 0,1,2
            letter_index = ord(letter) - ord('A')  # Converter A,B,C para 0,1,2
            resposta_convertida[item_index] = str(letter_index)
        return resposta_convertida
    
    @action(detail=False, methods=['get'])
    def estatisticas_usuario(self, request):
        """
        Retorna estatísticas do usuário logado
        GET /api/respostas-usuario/estatisticas_usuario/
        """
        usuario = request.user
        
        # Total de respostas
        total_respostas = RespostaUsuario.objects.filter(usuario=usuario).count()
        
        # Total de acertos e erros
        total_acertos = RespostaUsuario.objects.filter(usuario=usuario, acertou=True).count()
        total_erros = RespostaUsuario.objects.filter(usuario=usuario, acertou=False).count()
        
        # Taxa de acerto
        taxa_acerto = (total_acertos / total_respostas * 100) if total_respostas > 0 else 0
        
        # Por tipo de questão
        por_tipo = RespostaUsuario.objects.filter(usuario=usuario).values('pergunta_tipo').annotate(
            total=Count('id'),
            acertos=Count('id', filter=Q(acertou=True)),
            erros=Count('id', filter=Q(acertou=False))
        )
        
        # Por bibliografia
        por_bibliografia = RespostaUsuario.objects.filter(
            usuario=usuario,
            bibliografia_id__isnull=False
        ).values('bibliografia_id').annotate(
            total=Count('id'),
            acertos=Count('id', filter=Q(acertou=True)),
            erros=Count('id', filter=Q(acertou=False))
        )
        
        # Por assunto
        por_assunto = RespostaUsuario.objects.filter(
            usuario=usuario,
            assunto__isnull=False
        ).values('assunto').annotate(
            total=Count('id'),
            acertos=Count('id', filter=Q(acertou=True)),
            erros=Count('id', filter=Q(acertou=False))
        )
        
        # Últimas respostas
        ultimas_respostas = RespostaUsuario.objects.filter(usuario=usuario)[:10]
        
        return Response({
            'total_respostas': total_respostas,
            'total_acertos': total_acertos,
            'total_erros': total_erros,
            'taxa_acerto': round(taxa_acerto, 2),
            'por_tipo': list(por_tipo),
            'por_bibliografia': list(por_bibliografia),
            'por_assunto': list(por_assunto),
            'ultimas_respostas': RespostaUsuarioSerializer(ultimas_respostas, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def minhas_respostas(self, request):
        """
        Retorna todas as respostas do usuário com opção de filtrar por acertou/errou
        GET /api/respostas-usuario/minhas_respostas/?acertou=true ou ?acertou=false
        """
        usuario = request.user
        acertou_param = request.query_params.get('acertou')
        
        queryset = RespostaUsuario.objects.filter(usuario=usuario).select_related('usuario').order_by('-timestamp')
        
        # Filtrar por acertou/errou se especificado
        if acertou_param is not None:
            acertou_value = acertou_param.lower() == 'true'
            queryset = queryset.filter(acertou=acertou_value)
        
        # Paginação
        page_size = int(request.query_params.get('page_size', 50))
        page = int(request.query_params.get('page', 1))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        respostas = queryset[start:end]
        total = queryset.count()
        
        # Buscar detalhes das questões
        respostas_com_detalhes = []
        for resposta in respostas:
            detalhes = {
                'resposta': RespostaUsuarioSerializer(resposta).data,
                'questao': None
            }
            
            # Buscar detalhes da questão baseado no tipo
            try:
                if resposta.pergunta_tipo == 'multipla':
                    pergunta = PerguntaMultiplaModel.objects.get(id=resposta.pergunta_id)
                    detalhes['questao'] = {
                        'id': pergunta.id,
                        'tipo': 'multipla',
                        'pergunta': pergunta.pergunta,
                        'alternativa_a': pergunta.alternativa_a,
                        'alternativa_b': pergunta.alternativa_b,
                        'alternativa_c': pergunta.alternativa_c,
                        'alternativa_d': pergunta.alternativa_d,
                        'resposta_correta': pergunta.resposta_correta,
                        'justificativa_resposta_certa': pergunta.justificativa_resposta_certa,
                        'bibliografia_titulo': pergunta.bibliografia.titulo if pergunta.bibliografia else None,
                        'assunto': pergunta.assunto
                    }
                elif resposta.pergunta_tipo == 'vf':
                    pergunta = PerguntaVFModel.objects.get(id=resposta.pergunta_id)
                    detalhes['questao'] = {
                        'id': pergunta.id,
                        'tipo': 'vf',
                        'pergunta': pergunta.pergunta,
                        'afirmacao_verdadeira': pergunta.afirmacao_verdadeira,
                        'afirmacao_falsa': pergunta.afirmacao_falsa,
                        'resposta_correta': True,  # Sempre True para VF
                        'justificativa_resposta_certa': pergunta.justificativa_resposta_certa,
                        'bibliografia_titulo': pergunta.bibliografia.titulo if pergunta.bibliografia else None,
                        'assunto': pergunta.assunto
                    }
                elif resposta.pergunta_tipo == 'correlacao':
                    pergunta = PerguntaCorrelacaoModel.objects.get(id=resposta.pergunta_id)
                    detalhes['questao'] = {
                        'id': pergunta.id,
                        'tipo': 'correlacao',
                        'pergunta': pergunta.pergunta,
                        'coluna_a': pergunta.coluna_a,
                        'coluna_b': pergunta.coluna_b,
                        'resposta_correta': pergunta.resposta_correta,
                        'justificativa_resposta_certa': pergunta.justificativa_resposta_certa,
                        'bibliografia_titulo': pergunta.bibliografia.titulo if pergunta.bibliografia else None,
                        'assunto': pergunta.assunto
                    }
            except Exception as e:
                detalhes['questao'] = {'erro': f'Questão não encontrada: {str(e)}'}
            
            respostas_com_detalhes.append(detalhes)
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': respostas_com_detalhes
        })
    
    @action(detail=False, methods=['get'])
    def ranking_geral(self, request):
        """
        Retorna ranking geral de todos os usuários (apenas para admin)
        GET /api/respostas-usuario/ranking_geral/
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Acesso negado. Apenas administradores podem visualizar o ranking geral.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django_licitacao360.apps.core.users.models import Usuario
        
        # Ranking por total de acertos
        ranking_acertos = Usuario.objects.annotate(
            total_acertos=Count('respostas', filter=Q(respostas__acertou=True)),
            total_respostas=Count('respostas')
        ).filter(total_respostas__gt=0).order_by('-total_acertos', '-total_respostas')
        
        ranking_data = []
        for usuario in ranking_acertos:
            taxa = (usuario.total_acertos / usuario.total_respostas * 100) if usuario.total_respostas > 0 else 0
            ranking_data.append({
                'usuario_id': usuario.id,
                'username': usuario.username,
                'total_acertos': usuario.total_acertos,
                'total_respostas': usuario.total_respostas,
                'taxa_acerto': round(taxa, 2)
            })
        
        # Estatísticas gerais
        total_usuarios = Usuario.objects.filter(respostas__isnull=False).distinct().count()
        total_respostas_sistema = RespostaUsuario.objects.count()
        total_acertos_sistema = RespostaUsuario.objects.filter(acertou=True).count()
        
        # Questões mais acertadas/erradas
        questoes_mais_acertadas = RespostaUsuario.objects.filter(acertou=True).values(
            'pergunta_id', 'pergunta_tipo'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        questoes_mais_erradas = RespostaUsuario.objects.filter(acertou=False).values(
            'pergunta_id', 'pergunta_tipo'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        return Response({
            'ranking': ranking_data,
            'estatisticas_gerais': {
                'total_usuarios': total_usuarios,
                'total_respostas': total_respostas_sistema,
                'total_acertos': total_acertos_sistema,
                'taxa_acerto_geral': round(
                    (total_acertos_sistema / total_respostas_sistema * 100) if total_respostas_sistema > 0 else 0,
                    2
                )
            },
            'questoes_mais_acertadas': list(questoes_mais_acertadas),
            'questoes_mais_erradas': list(questoes_mais_erradas)
        })
    
    @action(detail=False, methods=['post'], url_path='resetar_estatisticas')
    def resetar_estatisticas(self, request):
        """
        Reseta estatísticas do usuário logado
        IMPORTANTE: O usuário só pode resetar suas próprias estatísticas.
        O campo 'usuario' é sempre definido como request.user, ignorando qualquer
        tentativa de passar um usuario_id diferente no body da requisição.
        
        Se bibliografia_ids (lista) for fornecido, reseta apenas dessas bibliografias
        Se bibliografia_id (único) for fornecido, reseta apenas dessa bibliografia
        Caso contrário, reseta todas as estatísticas
        Preserva questões erradas na tabela anônima antes de deletar
        
        POST /api/respostas-usuario/resetar_estatisticas/
        Body opcional: { "bibliografia_id": 1 } ou { "bibliografia_ids": [1, 2, 3] }
        """
        # SEMPRE usar o usuário autenticado da requisição
        # Ignorar qualquer tentativa de passar usuario_id no body
        usuario = request.user
        
        # Validar que o usuário está autenticado (já garantido por IsAuthenticated, mas reforçando)
        if not usuario or not usuario.is_authenticated:
            return Response(
                {'error': 'Usuário não autenticado'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        bibliografia_ids = request.data.get('bibliografia_ids', [])
        bibliografia_id = request.data.get('bibliografia_id')
        
        # Construir filtros base - SEMPRE filtrar por usuario=request.user
        # Isso garante que o usuário só pode resetar suas próprias respostas
        filtros_respostas = {'usuario': usuario}
        
        # Se bibliografia_ids (lista) foi fornecido, usar lista
        if bibliografia_ids:
            try:
                # Garantir que é uma lista
                if not isinstance(bibliografia_ids, list):
                    bibliografia_ids = [bibliografia_ids]
                # Converter para inteiros
                bibliografia_ids = [int(bid) for bid in bibliografia_ids]
                filtros_respostas['bibliografia_id__in'] = bibliografia_ids
            except (ValueError, TypeError) as e:
                return Response(
                    {'error': f'bibliografia_ids deve ser uma lista de números válidos: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        # Se bibliografia_id (único) foi fornecido, usar único
        elif bibliografia_id is not None:
            try:
                bibliografia_id = int(bibliografia_id)
                filtros_respostas['bibliografia_id'] = bibliografia_id
            except (ValueError, TypeError):
                return Response(
                    {'error': 'bibliografia_id deve ser um número válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Buscar respostas erradas do usuário (filtradas por bibliografia se especificado)
        respostas_erradas = RespostaUsuario.objects.filter(
            **filtros_respostas,
            acertou=False
        )
        
        # Contar quantas questões erradas serão preservadas
        total_erros_preservados = respostas_erradas.count()
        
        # Registrar questões erradas na tabela anônima (se ainda não estiverem lá)
        # Nota: Não verificamos duplicatas porque queremos contar cada erro de cada usuário
        questoes_anonimas_criadas = 0
        for resposta in respostas_erradas:
            # Criar registro anônimo para cada erro
            QuestaoErradaAnonima.objects.create(
                pergunta_id=resposta.pergunta_id,
                pergunta_tipo=resposta.pergunta_tipo,
                bibliografia_id=resposta.bibliografia_id,
                assunto=resposta.assunto
            )
            questoes_anonimas_criadas += 1
        
        # Deletar respostas do usuário (filtradas por bibliografia se especificado)
        total_deletadas = RespostaUsuario.objects.filter(**filtros_respostas).count()
        RespostaUsuario.objects.filter(**filtros_respostas).delete()
        
        mensagem = 'Estatísticas resetadas com sucesso'
        if bibliografia_ids:
            mensagem = f'Estatísticas de {len(bibliografia_ids)} bibliografia(s) resetadas com sucesso'
        elif bibliografia_id is not None:
            mensagem = f'Estatísticas da bibliografia {bibliografia_id} resetadas com sucesso'
        
        return Response({
            'message': mensagem,
            'total_respostas_deletadas': total_deletadas,
            'questoes_erradas_preservadas': questoes_anonimas_criadas
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='estatisticas_gerais_erros')
    def estatisticas_gerais_erros(self, request):
        """
        Retorna estatísticas gerais de questões erradas por matéria (apenas para admin)
        GET /api/respostas-usuario/estatisticas_gerais_erros/
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Acesso negado. Apenas administradores podem visualizar estas estatísticas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Agrupar por bibliografia_id e contar erros
        erros_por_bibliografia = QuestaoErradaAnonima.objects.filter(
            bibliografia_id__isnull=False
        ).values('bibliografia_id').annotate(
            total_erros=Count('id')
        ).order_by('-total_erros')
        
        # Buscar informações das bibliografias
        bibliografias_info = {}
        for item in erros_por_bibliografia:
            try:
                bibliografia = BibliografiaModel.objects.get(id=item['bibliografia_id'])
                bibliografias_info[item['bibliografia_id']] = {
                    'id': bibliografia.id,
                    'titulo': bibliografia.titulo,
                    'materia': bibliografia.materia.materia if bibliografia.materia else None,
                    'autor': bibliografia.autor
                }
            except BibliografiaModel.DoesNotExist:
                bibliografias_info[item['bibliografia_id']] = {
                    'id': item['bibliografia_id'],
                    'titulo': 'Bibliografia não encontrada',
                    'materia': None,
                    'autor': None
                }
        
        # Agrupar por matéria
        erros_por_materia = {}
        for item in erros_por_bibliografia:
            bibliografia_id = item['bibliografia_id']
            bibliografia = bibliografias_info.get(bibliografia_id, {})
            materia = bibliografia.get('materia') or 'Sem matéria'
            
            if materia not in erros_por_materia:
                erros_por_materia[materia] = {
                    'materia': materia,
                    'total_erros': 0,
                    'bibliografias': []
                }
            
            erros_por_materia[materia]['total_erros'] += item['total_erros']
            erros_por_materia[materia]['bibliografias'].append({
                'bibliografia_id': bibliografia_id,
                'titulo': bibliografia.get('titulo', 'Desconhecido'),
                'autor': bibliografia.get('autor'),
                'total_erros': item['total_erros']
            })
        
        # Ordenar por total de erros (decrescente)
        ranking_materias = sorted(
            erros_por_materia.values(),
            key=lambda x: x['total_erros'],
            reverse=True
        )
        
        # Estatísticas gerais
        total_erros_geral = QuestaoErradaAnonima.objects.count()
        total_bibliografias_com_erros = erros_por_bibliografia.count()
        total_materias_com_erros = len(erros_por_materia)
        
        # Erros por tipo de questão
        erros_por_tipo = QuestaoErradaAnonima.objects.values('pergunta_tipo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        return Response({
            'estatisticas_gerais': {
                'total_erros': total_erros_geral,
                'total_bibliografias_com_erros': total_bibliografias_com_erros,
                'total_materias_com_erros': total_materias_com_erros
            },
            'ranking_materias': ranking_materias,
            'erros_por_tipo': list(erros_por_tipo),
            'erros_por_bibliografia': [
                {
                    **item,
                    'bibliografia': bibliografias_info.get(item['bibliografia_id'], {})
                }
                for item in erros_por_bibliografia[:50]  # Top 50 bibliografias
            ]
        })