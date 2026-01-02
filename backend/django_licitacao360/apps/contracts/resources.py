# Recursos de import/export
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget, JSONWidget
from .models import (
    MateriaModel,
    BibliografiaModel, 
    FlashCardsModel,
    PerguntaMultiplaModel, 
    PerguntaVFModel, 
    PerguntaCorrelacaoModel
)


class BibliografiaResource(resources.ModelResource):
    materia = fields.Field(
        column_name='materia',
        attribute='materia',
        widget=ForeignKeyWidget(MateriaModel, 'materia')
    )
    
    class Meta:
        model = BibliografiaModel
        fields = ('id', 'titulo', 'autor', 'materia', 'descricao')
        export_order = ('id', 'titulo', 'autor', 'materia', 'descricao')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True

class FlashCardsResource(resources.ModelResource):
    bibliografia = fields.Field(
        column_name='bibliografia',
        attribute='bibliografia',
        widget=ForeignKeyWidget(BibliografiaModel, 'titulo')
    )
    prova = fields.Field(
        column_name='prova',
        attribute='prova',
        widget=BooleanWidget()
    )

    class Meta:
        model = FlashCardsModel
        fields = ('id', 'bibliografia', 'pergunta', 'resposta', 'assunto', 'prova', 'ano', 'caveira')
        export_order = ('id', 'bibliografia', 'pergunta', 'resposta', 'assunto', 'prova', 'ano', 'caveira')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True

class PerguntaMultiplaResource(resources.ModelResource):
    bibliografia = fields.Field(
        column_name='bibliografia',
        attribute='bibliografia',
        widget=ForeignKeyWidget(BibliografiaModel, 'titulo')
    )
    caiu_em_prova = fields.Field(
        column_name='caiu_em_prova',
        attribute='caiu_em_prova',
        widget=BooleanWidget()
    )

    class Meta:
        model = PerguntaMultiplaModel
        fields = (
            'id', 'bibliografia', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova', 'pergunta',
            'alternativa_a', 'alternativa_b', 'alternativa_c', 'alternativa_d',
            'resposta_correta', 'justificativa_resposta_certa', 'tipo'
        )
        export_order = (
            'id', 'bibliografia', 'pergunta', 'alternativa_a', 'alternativa_b',
            'alternativa_c', 'alternativa_d', 'resposta_correta', 'paginas', 'assunto',
            'caiu_em_prova', 'ano_prova', 'justificativa_resposta_certa', 'tipo'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


class PerguntaVFResource(resources.ModelResource):
    bibliografia = fields.Field(
        column_name='bibliografia',
        attribute='bibliografia',
        widget=ForeignKeyWidget(BibliografiaModel, 'titulo')
    )
    caiu_em_prova = fields.Field(
        column_name='caiu_em_prova',
        attribute='caiu_em_prova',
        widget=BooleanWidget()
    )

    class Meta:
        model = PerguntaVFModel
        fields = (
            'id', 'bibliografia', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova', 'pergunta',
            'afirmacao_verdadeira', 'afirmacao_falsa', 'justificativa_resposta_certa', 'tipo'
        )
        export_order = (
            'id', 'bibliografia', 'paginas', 'assunto', 'afirmacao_verdadeira', 'afirmacao_falsa', 
            'justificativa_resposta_certa', 'caiu_em_prova', 'ano_prova', 'tipo'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


class PerguntaCorrelacaoResource(resources.ModelResource):
    bibliografia = fields.Field(
        column_name='bibliografia',
        attribute='bibliografia',
        widget=ForeignKeyWidget(BibliografiaModel, 'titulo')
    )
    caiu_em_prova = fields.Field(
        column_name='caiu_em_prova',
        attribute='caiu_em_prova',
        widget=BooleanWidget()
    )
    coluna_a = fields.Field(
        column_name='coluna_a',
        attribute='coluna_a',
        widget=JSONWidget()
    )
    coluna_b = fields.Field(
        column_name='coluna_b',
        attribute='coluna_b',
        widget=JSONWidget()
    )
    resposta_correta = fields.Field(
        column_name='resposta_correta',
        attribute='resposta_correta',
        widget=JSONWidget()
    )

    class Meta:
        model = PerguntaCorrelacaoModel
        fields = (
            'id', 'bibliografia', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova', 'pergunta',
            'coluna_a', 'coluna_b', 'resposta_correta',
            'justificativa_resposta_certa', 'tipo'
        )
        export_order = (
            'id', 'bibliografia', 'pergunta', 'coluna_a', 'coluna_b',
            'resposta_correta', 'paginas', 'assunto', 'caiu_em_prova', 'ano_prova',
            'justificativa_resposta_certa', 'tipo'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True

