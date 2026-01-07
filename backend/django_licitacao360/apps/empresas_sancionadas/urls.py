from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EmpresasSancionadasViewSet

router = DefaultRouter()
router.register(r"empresas-sancionadas", EmpresasSancionadasViewSet, basename="empresas-sancionadas")

urlpatterns = [
    path("", include(router.urls)),
]
