from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Compra, ItemCompra, ResultadoItem, Fornecedor

# Exemplo de sinal:
# @receiver(post_save, sender=Compra)
# def compra_pos_save(sender, instance, created, **kwargs):
#     if created:
#         pass
