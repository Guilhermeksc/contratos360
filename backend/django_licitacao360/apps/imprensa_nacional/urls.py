from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import InlabsArticleViewSet

router = DefaultRouter()
router.register(r"articles", InlabsArticleViewSet, basename="inlabs-article")

urlpatterns = [
    path("", include(router.urls)),
]
