"""
Views para Status de Contratos
"""

from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import StatusContrato, RegistroStatus, RegistroMensagem, Contrato
from ..serializers import (
    StatusContratoSerializer,
    RegistroStatusSerializer,
    RegistroMensagemSerializer,
)


class StatusContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para StatusContrato
    Sempre faz update_or_create no POST para lidar com relacionamento OneToOne
    """
    queryset = StatusContrato.objects.select_related('contrato', 'contrato__uasg').all()
    serializer_class = StatusContratoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['uasg_code', 'status']
    search_fields = ['status', 'objeto_editado']
    ordering_fields = ['data_registro']
    ordering = ['-data_registro']
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescreve create para sempre fazer update_or_create
        Isso evita erro de unicidade quando já existe um status para o contrato
        """
        serializer = self.get_serializer(data=request.data)
        
        # Valida os dados, mas captura erro de unicidade
        is_valid = serializer.is_valid(raise_exception=False)
        errors = serializer.errors.copy() if hasattr(serializer, 'errors') else {}
        
        # Se não é válido, verifica se é apenas erro de unicidade
        if not is_valid and 'contrato' in errors:
            contrato_errors = errors['contrato']
            is_only_uniqueness_error = all(
                'já existe' in str(msg) or 'already exists' in str(msg).lower() 
                for msg in contrato_errors
            )
            
            if is_only_uniqueness_error:
                # Remove o erro de unicidade
                errors_copy = dict(errors)
                errors_copy.pop('contrato', None)
                
                # Se há outros erros além de unicidade, levanta eles
                if errors_copy:
                    raise serializers.ValidationError(errors_copy)
                
                # Se só tinha erro de unicidade, força a validação dos dados
                # Criando um novo serializer e validando sem o campo contrato primeiro
                # para obter os validated_data
                data_copy = request.data.copy()
                contrato_id = data_copy.pop('contrato', None)
                
                # Valida os outros campos
                serializer_partial = self.get_serializer(data=data_copy, partial=True)
                if not serializer_partial.is_valid():
                    raise serializers.ValidationError(serializer_partial.errors)
                
                # Agora faz update_or_create diretamente
                try:
                    contrato = Contrato.objects.get(id=contrato_id)
                except Contrato.DoesNotExist:
                    raise serializers.ValidationError({
                        'contrato': f'Contrato com ID {contrato_id} não encontrado.'
                    })
                
                # Prepara os dados para update_or_create
                defaults = serializer_partial.validated_data.copy()
                if 'status' not in defaults or not defaults.get('status'):
                    defaults['status'] = 'SEÇÃO CONTRATOS'
                
                # Faz update_or_create diretamente
                instance, created = StatusContrato.objects.update_or_create(
                    contrato=contrato,
                    defaults=defaults
                )
                
                # Retorna a resposta
                response_serializer = self.get_serializer(instance)
                headers = self.get_success_headers(response_serializer.data)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK,
                    headers=headers
                )
            else:
                # Se há outros erros no campo contrato, levanta eles
                raise serializers.ValidationError(errors)
        elif not is_valid:
            # Se há outros erros que não são de unicidade, levanta eles
            raise serializers.ValidationError(errors)
        
        # Se chegou aqui, o serializer está válido
        # Usa o método create do serializer que já faz update_or_create
        instance = serializer.save()
        
        # Cria um novo serializer com a instância para retornar os dados atualizados
        response_serializer = self.get_serializer(instance)
        
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,  # Sempre retorna 200 pois pode ser update ou create
            headers=headers
        )


class RegistroStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet para RegistroStatus
    """
    queryset = RegistroStatus.objects.select_related('contrato').all()
    serializer_class = RegistroStatusSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato', 'uasg_code']
    search_fields = ['texto']
    ordering_fields = ['id']
    ordering = ['-id']
    pagination_class = None  # Desabilita paginação para retornar array direto


class RegistroMensagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para RegistroMensagem
    """
    queryset = RegistroMensagem.objects.select_related('contrato').all()
    serializer_class = RegistroMensagemSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contrato']
    search_fields = ['texto']
    ordering_fields = ['id']
    ordering = ['-id']
    pagination_class = None  # Desabilita paginação para retornar array direto

