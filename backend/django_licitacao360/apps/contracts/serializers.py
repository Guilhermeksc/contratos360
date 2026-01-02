from rest_framework import serializers
from .models import (
    BibliografiaModel,
    MateriaModel,
    FlashCardsModel,
    PerguntaMultiplaModel, 
    PerguntaVFModel, 
    PerguntaCorrelacaoModel,
    RespostaUsuario,
    QuestaoErradaAnonima
)


class BibliografiaSerializer(serializers.ModelSerializer):
    perguntas_count = serializers.SerializerMethodField()
    flashcards_count = serializers.SerializerMethodField()
    materia_nome = serializers.CharField(source='materia.materia', read_only=True, allow_null=True)
    
    class Meta:
        model = BibliografiaModel
        fields = [
            'id', 'titulo', 'autor', 'materia', 'materia_nome', 'descricao',
            'perguntas_count', 'flashcards_count'
        ]
        read_only_fields = ['id']
    
    def get_perguntas_count(self, obj):
        """Retorna o número total de perguntas desta bibliografia"""
        from .models import PerguntaMultiplaModel, PerguntaVFModel, PerguntaCorrelacaoModel
        count = 0
        count += PerguntaMultiplaModel.objects.filter(bibliografia=obj).count()
        count += PerguntaVFModel.objects.filter(bibliografia=obj).count()
        count += PerguntaCorrelacaoModel.objects.filter(bibliografia=obj).count()
        return count
    
    def get_flashcards_count(self, obj):
        """Retorna o número total de flashcards desta bibliografia"""
        return FlashCardsModel.objects.filter(bibliografia=obj).count()


class FlashCardsSerializer(serializers.ModelSerializer):
    bibliografia_titulo = serializers.CharField(source='bibliografia.titulo', read_only=True)
    
    class Meta:
        model = FlashCardsModel
        fields = [
            'id', 'bibliografia', 'bibliografia_titulo', 
            'pergunta', 'resposta', 'assunto', 'prova', 'ano', 'caveira'
        ]
        read_only_fields = ['id']


class PerguntaMultiplaSerializer(serializers.ModelSerializer):
    bibliografia_titulo = serializers.CharField(source='bibliografia.titulo', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    resposta_correta_display = serializers.CharField(source='get_resposta_correta_display', read_only=True)
    
    class Meta:
        model = PerguntaMultiplaModel
        fields = [
            'id', 'bibliografia', 'bibliografia_titulo', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova',
            'pergunta', 'alternativa_a', 'alternativa_b', 'alternativa_c', 'alternativa_d',
            'resposta_correta', 'resposta_correta_display', 'justificativa_resposta_certa',
            'tipo', 'tipo_display'
        ]
        read_only_fields = ['tipo']
    
    def validate_resposta_correta(self, value):
        """Valida se a resposta correta está entre as opções válidas"""
        if value not in ['a', 'b', 'c', 'd']:
            raise serializers.ValidationError("Resposta correta deve ser 'a', 'b', 'c' ou 'd'")
        return value


class PerguntaVFSerializer(serializers.ModelSerializer):
    bibliografia_titulo = serializers.CharField(source='bibliografia.titulo', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    resposta_correta = serializers.ReadOnlyField()
    resposta_correta_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PerguntaVFModel
        fields = [
            'id', 'bibliografia', 'bibliografia_titulo', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova',
            'pergunta', 'afirmacao_verdadeira', 'afirmacao_falsa', 'resposta_correta', 'resposta_correta_display',
            'justificativa_resposta_certa', 'tipo', 'tipo_display'
        ]
        read_only_fields = ['tipo', 'resposta_correta']
    
    def get_resposta_correta_display(self, obj):
        """Retorna 'Verdadeiro' pois a afirmacao_verdadeira é sempre a correta"""
        return "Verdadeiro"


class PerguntaCorrelacaoSerializer(serializers.ModelSerializer):
    bibliografia_titulo = serializers.CharField(source='bibliografia.titulo', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = PerguntaCorrelacaoModel
        fields = [
            'id', 'bibliografia', 'bibliografia_titulo', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova',
            'pergunta', 'coluna_a', 'coluna_b', 'resposta_correta',
            'justificativa_resposta_certa', 'tipo', 'tipo_display'
        ]
        read_only_fields = ['tipo']
    
    def validate_coluna_a(self, value):
        """Valida se coluna_a é uma lista"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Coluna A deve ser uma lista de itens")
        if len(value) == 0:
            raise serializers.ValidationError("Coluna A não pode estar vazia")
        return value
    
    def validate_coluna_b(self, value):
        """Valida se coluna_b é uma lista"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Coluna B deve ser uma lista de itens")
        if len(value) == 0:
            raise serializers.ValidationError("Coluna B não pode estar vazia")
        return value
    
    def validate_resposta_correta(self, value):
        """Valida se resposta_correta é um dicionário válido"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Resposta correta deve ser um dicionário de pares")
        return value


class PerguntaResumoSerializer(serializers.Serializer):
    """Serializer para resumo de perguntas (usado em listagens)"""
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    tipo_display = serializers.CharField()
    bibliografia_titulo = serializers.CharField()
    pergunta = serializers.CharField()
    paginas = serializers.CharField()
    assunto = serializers.CharField(allow_null=True)
    caiu_em_prova = serializers.BooleanField()
    ano_prova = serializers.IntegerField()


# Serializers para criação/edição
class BibliografiaCreateUpdateSerializer(BibliografiaSerializer):
    """Serializer específico para criação e edição de bibliografia"""
    class Meta(BibliografiaSerializer.Meta):
        fields = ['id', 'titulo', 'autor', 'materia', 'descricao']


class PerguntaMultiplaCreateUpdateSerializer(PerguntaMultiplaSerializer):
    """Serializer específico para criação e edição de pergunta múltipla escolha"""
    class Meta(PerguntaMultiplaSerializer.Meta):
        fields = [
            'bibliografia', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova', 'pergunta',
            'alternativa_a', 'alternativa_b', 'alternativa_c', 'alternativa_d',
            'resposta_correta', 'justificativa_resposta_certa'
        ]


class PerguntaVFCreateUpdateSerializer(PerguntaVFSerializer):
    """Serializer específico para criação e edição de pergunta V/F"""
    class Meta(PerguntaVFSerializer.Meta):
        fields = [
            'bibliografia', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova', 'pergunta',
            'afirmacao_verdadeira', 'afirmacao_falsa', 'justificativa_resposta_certa'
        ]


class PerguntaCorrelacaoCreateUpdateSerializer(PerguntaCorrelacaoSerializer):
    """Serializer específico para criação e edição de pergunta de correlação"""
    class Meta(PerguntaCorrelacaoSerializer.Meta):
        fields = [
            'bibliografia', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova', 'pergunta',
            'coluna_a', 'coluna_b', 'resposta_correta', 'justificativa_resposta_certa'
        ]


class FlashCardsCreateUpdateSerializer(FlashCardsSerializer):
    """Serializer específico para criação e edição de flash cards"""
    class Meta(FlashCardsSerializer.Meta):
        fields = ['bibliografia', 'pergunta', 'resposta', 'assunto', 'prova', 'ano', 'caveira']


class RespostaUsuarioSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = RespostaUsuario
        fields = [
            'id',
            'usuario',
            'usuario_username',
            'pergunta_id',
            'pergunta_tipo',
            'resposta_usuario',
            'acertou',
            'timestamp',
            'bibliografia_id',
            'assunto'
        ]
        read_only_fields = ['id', 'timestamp']

class RespostaUsuarioCreateSerializer(serializers.ModelSerializer):
    afirmacao_sorteada_eh_verdadeira = serializers.BooleanField(required=False, allow_null=True, write_only=True)
    acertou = serializers.BooleanField(required=False, write_only=True)
    
    class Meta:
        model = RespostaUsuario
        fields = [
            'pergunta_id',
            'pergunta_tipo',
            'resposta_usuario',
            'bibliografia_id',
            'assunto',
            'afirmacao_sorteada_eh_verdadeira',
            'acertou'  # Incluído mas será ignorado se não vier do cliente
        ]
    
    def create(self, validated_data):
        # Remover campo auxiliar antes de salvar (não é um campo do modelo)
        validated_data.pop('afirmacao_sorteada_eh_verdadeira', None)
        # O usuário é automaticamente definido pelo request.user
        validated_data['usuario'] = self.context['request'].user
        # acertou será definido na view antes de chamar create()
        # Se não estiver em validated_data, será None e causará erro, então garantimos que está
        return super().create(validated_data)


class QuestaoErradaAnonimaSerializer(serializers.ModelSerializer):
    """Serializer para questões erradas anônimas"""
    
    class Meta:
        model = QuestaoErradaAnonima
        fields = [
            'id',
            'pergunta_id',
            'pergunta_tipo',
            'bibliografia_id',
            'assunto',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
