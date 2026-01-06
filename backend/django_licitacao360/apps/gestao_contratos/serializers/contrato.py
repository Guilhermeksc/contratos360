"""
Serializers para Contrato
"""

from rest_framework import serializers
from ..models import Contrato


class ContratoSerializer(serializers.ModelSerializer):
    """Serializer básico para listagem de contratos"""
    uasg = serializers.CharField(source='uasg.uasg', read_only=True)  # Retorna código UASG ao invés de ID
    uasg_nome = serializers.CharField(source='uasg.nome_om', read_only=True)
    uasg_sigla = serializers.CharField(source='uasg.sigla_om', read_only=True)
    status_atual = serializers.CharField(source='status.status', read_only=True)
    
    class Meta:
        model = Contrato
        fields = [
            'id',
            'numero',
            'uasg',
            'uasg_nome',
            'uasg_sigla',
            'licitacao_numero',
            'processo',
            'fornecedor_nome',
            'fornecedor_cnpj',
            'objeto',
            'valor_global',
            'vigencia_inicio',
            'vigencia_fim',
            'tipo',
            'modalidade',
            'manual',
            'status_atual',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'uasg', 'uasg_sigla']


class ContratoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo com dados relacionados"""
    from .status import StatusContratoSerializer
    from .links import LinksContratoSerializer
    from .fiscalizacao import FiscalizacaoContratoSerializer
    
    uasg = serializers.CharField(source='uasg.uasg', read_only=True)  # Retorna código UASG ao invés de ID
    uasg_nome = serializers.CharField(source='uasg.nome_om', read_only=True)
    uasg_sigla = serializers.CharField(source='uasg.sigla_om', read_only=True)
    status = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    fiscalizacao = serializers.SerializerMethodField()
    registros_status = serializers.SerializerMethodField()
    registros_mensagem = serializers.SerializerMethodField()
    historicos_count = serializers.SerializerMethodField()
    empenhos_count = serializers.SerializerMethodField()
    itens_count = serializers.SerializerMethodField()
    arquivos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Contrato
        fields = [
            'id',
            'numero',
            'uasg',
            'uasg_nome',
            'uasg_sigla',
            'licitacao_numero',
            'processo',
            'fornecedor_nome',
            'fornecedor_cnpj',
            'objeto',
            'valor_global',
            'vigencia_inicio',
            'vigencia_fim',
            'tipo',
            'modalidade',
            'contratante_orgao_unidade_gestora_codigo',
            'contratante_orgao_unidade_gestora_nome_resumido',
            'manual',
            'raw_json',
            'status',
            'links',
            'fiscalizacao',
            'registros_status',
            'registros_mensagem',
            'historicos_count',
            'empenhos_count',
            'itens_count',
            'arquivos_count',
            'historico_atualizado_em',
            'empenhos_atualizados_em',
            'itens_atualizados_em',
            'arquivos_atualizados_em',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'uasg', 'uasg_sigla']
    
    def get_status(self, obj):
        """Retorna status do contrato ou None"""
        try:
            if hasattr(obj, 'status') and obj.status:
                from .status import StatusContratoSerializer
                return StatusContratoSerializer(obj.status).data
            return None
        except Exception:
            return None
    
    def get_links(self, obj):
        """Retorna links do contrato ou None"""
        try:
            if hasattr(obj, 'links') and obj.links:
                from .links import LinksContratoSerializer
                return LinksContratoSerializer(obj.links).data
            return None
        except Exception:
            return None
    
    def get_fiscalizacao(self, obj):
        """Retorna fiscalização do contrato ou None"""
        try:
            if hasattr(obj, 'fiscalizacao') and obj.fiscalizacao:
                from .fiscalizacao import FiscalizacaoContratoSerializer
                return FiscalizacaoContratoSerializer(obj.fiscalizacao).data
            return None
        except Exception:
            return None
    
    def get_registros_status(self, obj):
        """Retorna lista de textos dos registros de status"""
        try:
            return [reg.texto for reg in obj.registros_status.all()]
        except Exception:
            return []
    
    def get_registros_mensagem(self, obj):
        """Retorna lista de textos dos registros de mensagem"""
        try:
            return [reg.texto for reg in obj.registros_mensagem.all()]
        except Exception:
            return []
    
    def get_historicos_count(self, obj):
        """Retorna contagem de históricos"""
        try:
            return obj.historicos.count()
        except Exception:
            return 0
    
    def get_empenhos_count(self, obj):
        """Retorna contagem de empenhos"""
        try:
            return obj.empenhos.count()
        except Exception:
            return 0
    
    def get_itens_count(self, obj):
        """Retorna contagem de itens"""
        try:
            return obj.itens.count()
        except Exception:
            return 0
    
    def get_arquivos_count(self, obj):
        """Retorna contagem de arquivos"""
        try:
            return obj.arquivos.count()
        except Exception:
            return 0


class ContratoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de contratos"""
    from django_licitacao360.apps.uasgs.models import Uasg
    
    class Meta:
        model = Contrato
        fields = [
            'id',
            'uasg',
            'numero',
            'licitacao_numero',
            'processo',
            'fornecedor_nome',
            'fornecedor_cnpj',
            'objeto',
            'valor_global',
            'vigencia_inicio',
            'vigencia_fim',
            'tipo',
            'modalidade',
            'contratante_orgao_unidade_gestora_codigo',
            'contratante_orgao_unidade_gestora_nome_resumido',
            'manual',
            'raw_json',
        ]
    
    def validate_uasg(self, value):
        """Valida e converte código UASG (string) para objeto Uasg"""
        from django_licitacao360.apps.uasgs.models import Uasg
        
        # Se já é um objeto Uasg, retorna como está
        if isinstance(value, Uasg):
            return value
        
        # Se é um ID (número), busca por id_uasg
        if isinstance(value, (int, str)) and str(value).isdigit():
            try:
                uasg_int = int(value)
                uasg_obj = Uasg.objects.filter(uasg=uasg_int).first()
                if not uasg_obj:
                    # Tenta buscar por id_uasg como fallback
                    uasg_obj = Uasg.objects.filter(id_uasg=uasg_int).first()
                if uasg_obj:
                    return uasg_obj
            except (ValueError, TypeError):
                pass
        
        raise serializers.ValidationError(f'UASG inválida: {value}')
    
    def validate(self, attrs):
        """Validações customizadas"""
        if attrs.get('manual') and not attrs.get('numero'):
            raise serializers.ValidationError({
                'numero': 'Contratos manuais devem ter número'
            })
        return attrs


class ContratoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de contratos"""
    
    class Meta:
        model = Contrato
        fields = [
            'numero',
            'licitacao_numero',
            'processo',
            'fornecedor_nome',
            'fornecedor_cnpj',
            'objeto',
            'valor_global',
            'vigencia_inicio',
            'vigencia_fim',
            'tipo',
            'modalidade',
            'contratante_orgao_unidade_gestora_codigo',
            'contratante_orgao_unidade_gestora_nome_resumido',
            'raw_json',
        ]

