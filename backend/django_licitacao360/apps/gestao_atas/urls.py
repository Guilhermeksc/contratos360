from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AtaViewSet

router = DefaultRouter()
router.register(r"atas", AtaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
