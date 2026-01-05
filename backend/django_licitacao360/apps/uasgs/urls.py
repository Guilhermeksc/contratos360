"""URLs do app uasgs."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ComimSupViewSet, UasgViewSet

router = DefaultRouter()
router.register(r'uasgs', UasgViewSet, basename='uasg')
router.register(r'comimsups', ComimSupViewSet, basename='comimsup')

urlpatterns = [
    path('', include(router.urls)),
]

