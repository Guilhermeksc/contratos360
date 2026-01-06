from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CalendarioEventoViewSet

router = DefaultRouter()
router.register(r"eventos", CalendarioEventoViewSet, basename="calendario-evento")

urlpatterns = [
    path("", include(router.urls)),
]
