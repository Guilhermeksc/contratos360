from django.db import models


class Fornecedor(models.Model):
    cnpj_fornecedor = models.CharField("CNPJ do Fornecedor", max_length=20, primary_key=True)
    razao_social = models.CharField("Razão Social", max_length=255)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return f"{self.cnpj_fornecedor} - {self.razao_social}"


class Compra(models.Model):
    compra_id = models.CharField("ID da Compra", max_length=100, primary_key=True)
    ano_compra = models.IntegerField("Ano da Compra")
    sequencial_compra = models.IntegerField("Sequencial da Compra")
    numero_compra = models.CharField("Número da Compra", max_length=50)
    codigo_unidade = models.CharField("Código da Unidade", max_length=50)
    objeto_compra = models.TextField("Objeto da Compra")
    modalidade_nome = models.CharField("Modalidade", max_length=100)
    numero_processo = models.CharField("Número do Processo", max_length=100)
    data_publicacao_pncp = models.DateTimeField("Data de Publicação no PNCP", null=True, blank=True)
    data_atualizacao = models.DateTimeField("Data de Atualização", null=True, blank=True)
    valor_total_estimado = models.DecimalField("Valor Total Estimado", max_digits=19, decimal_places=4, null=True, blank=True)
    valor_total_homologado = models.DecimalField("Valor Total Homologado", max_digits=19, decimal_places=4, null=True, blank=True)
    percentual_desconto = models.DecimalField("Percentual de Desconto", max_digits=7, decimal_places=4, null=True, blank=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-ano_compra", "-sequencial_compra"]

    def __str__(self):
        return f"{self.numero_compra}/{self.ano_compra} - {self.objeto_compra[:50]}..."


class ItemCompra(models.Model):
    item_id = models.CharField("ID do Item", max_length=100, primary_key=True)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="itens", verbose_name="Compra")
    numero_item = models.IntegerField("Número do Item")
    descricao = models.TextField("Descrição")
    unidade_medida = models.CharField("Unidade de Medida", max_length=50)
    valor_unitario_estimado = models.DecimalField("Valor Unitário Estimado", max_digits=19, decimal_places=4, null=True, blank=True)
    valor_total_estimado = models.DecimalField("Valor Total Estimado", max_digits=19, decimal_places=4, null=True, blank=True)
    quantidade = models.DecimalField("Quantidade", max_digits=19, decimal_places=4)
    percentual_economia = models.DecimalField("Percentual de Economia", max_digits=7, decimal_places=4, null=True, blank=True)
    situacao_compra_item_nome = models.CharField("Situação do Item", max_length=100)
    tem_resultado = models.BooleanField("Tem Resultado", default=False)

    class Meta:
        verbose_name = "Item de Compra"
        verbose_name_plural = "Itens de Compra"
        ordering = ["compra", "numero_item"]

    def __str__(self):
        return f"Item {self.numero_item} - {self.compra.numero_compra}"


class ResultadoItem(models.Model):
    resultado_id = models.CharField("ID do Resultado", max_length=100, primary_key=True)
    item_compra = models.ForeignKey(ItemCompra, on_delete=models.CASCADE, related_name="resultados", verbose_name="Item de Compra")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name="resultados", verbose_name="Fornecedor")
    valor_total_homologado = models.DecimalField("Valor Total Homologado", max_digits=19, decimal_places=4)
    quantidade_homologada = models.IntegerField("Quantidade Homologada")
    valor_unitario_homologado = models.DecimalField("Valor Unitário Homologado", max_digits=19, decimal_places=4)
    status = models.CharField("Status", max_length=100)
    marca = models.CharField("Marca", max_length=100, null=True, blank=True)
    modelo = models.CharField("Modelo", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Resultado do Item"
        verbose_name_plural = "Resultados dos Itens"

    def __str__(self):
        return f"Resultado {self.resultado_id} - {self.item_compra}"
