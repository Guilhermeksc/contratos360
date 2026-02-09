from rest_framework import serializers

from .models import InlabsArticle, AvisoLicitacao, Credenciamento


class AvisoLicitacaoSerializer(serializers.ModelSerializer):
    """Serializer para Aviso de Licitação."""

    class Meta:
        model = AvisoLicitacao
        fields = [
            "id",
            "article_id",
            "modalidade",
            "numero",
            "ano",
            "uasg",
            "processo",
            "objeto",
            "itens_licitados",
            "publicacao",
            "entrega_propostas",
            "abertura_propostas",
            "nome_responsavel",
            "cargo",
        ]
        read_only_fields = ["id"]


class CredenciamentoSerializer(serializers.ModelSerializer):
    """Serializer para Credenciamento."""

    class Meta:
        model = Credenciamento
        fields = [
            "id",
            "article_id",
            "tipo",
            "numero",
            "ano",
            "uasg",
            "processo",
            "tipo_processo",
            "numero_processo",
            "ano_processo",
            "contratante",
            "contratado",
            "objeto",
            "fundamento_legal",
            "vigencia",
            "valor_total",
            "data_assinatura",
            "nome_responsavel",
            "cargo",
        ]
        read_only_fields = ["id"]


class InlabsArticleSerializer(serializers.ModelSerializer):
    """Serializer para artigos INLABS com relacionamentos opcionais."""

    uasg = serializers.SerializerMethodField()
    om_name = serializers.SerializerMethodField()
    aviso_licitacao = serializers.SerializerMethodField()
    credenciamento = serializers.SerializerMethodField()

    class Meta:
        model = InlabsArticle
        fields = [
            "id",
            "article_id",
            "name",
            "id_oficio",
            "pub_name",
            "art_type",
            "pub_date",
            "nome_om",
            "number_page",
            "pdf_page",
            "edition_number",
            "highlight_type",
            "highlight_priority",
            "highlight",
            "highlight_image",
            "highlight_image_name",
            "materia_id",
            "body_identifica",
            "uasg",
            "body_texto",
            "om_name",
            "aviso_licitacao",
            "credenciamento",
        ]

    def get_uasg(self, obj) -> str | None:
        """Retorna o número UASG extraído."""
        return obj.extract_uasg()

    def get_om_name(self, obj) -> str | None:
        """Retorna o nome da OM."""
        return obj.extract_om_name()

    def get_aviso_licitacao(self, obj) -> dict | None:
        """Retorna o aviso de licitação relacionado se existir."""
        try:
            aviso = AvisoLicitacao.objects.get(article_id=obj.article_id)
            return AvisoLicitacaoSerializer(aviso).data
        except AvisoLicitacao.DoesNotExist:
            return None

    def get_credenciamento(self, obj) -> dict | None:
        """Retorna o credenciamento relacionado se existir."""
        try:
            cred = Credenciamento.objects.get(article_id=obj.article_id)
            return CredenciamentoSerializer(cred).data
        except Credenciamento.DoesNotExist:
            return None
