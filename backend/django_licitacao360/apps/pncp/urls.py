from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompraViewSet,
    ItemCompraViewSet,
    ResultadoItemViewSet,
    FornecedorViewSet,
    CompraDetalhadaView,
    CompraListagemView,
    UnidadesPorAnoView,
    AnosUnidadesComboView,
)

router = DefaultRouter()
router.register(r"fornecedores", FornecedorViewSet)
router.register(r"compras", CompraViewSet)
router.register(r"itens", ItemCompraViewSet)
router.register(r"resultados", ResultadoItemViewSet)

# URLs customizadas devem vir ANTES do router para terem prioridade
urlpatterns = [
    path("compras/detalhada/", CompraDetalhadaView.as_view(), name="compra-detalhada"),
    path("compras/listagem/", CompraListagemView.as_view(), name="compra-listagem"),
    path("unidades/por-ano/", UnidadesPorAnoView.as_view(), name="unidades-por-ano"),
    path("combo/anos-unidades/", AnosUnidadesComboView.as_view(), name="anos-unidades-combo"),
    path("", include(router.urls)),  # Router por último para não conflitar com rotas customizadas
]
