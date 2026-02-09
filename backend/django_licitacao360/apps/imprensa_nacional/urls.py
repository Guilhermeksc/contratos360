from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    InlabsArticleViewSet,
    AvisoLicitacaoViewSet,
    CredenciamentoViewSet,
)

router = DefaultRouter()
router.register(r"articles", InlabsArticleViewSet, basename="inlabs-article")
router.register(r"avisos-licitacao", AvisoLicitacaoViewSet, basename="aviso-licitacao")
router.register(r"credenciamentos", CredenciamentoViewSet, basename="credenciamento")

urlpatterns = [
    path("", include(router.urls)),
]
