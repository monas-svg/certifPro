from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import MetierViewSet, internal_ressources
router = DefaultRouter()
router.register("metiers", MetierViewSet, basename="metier")
urlpatterns = [
    path("api/", include(router.urls)),
    path("api/internal/metiers/<slug:slug>/ressources/", internal_ressources),
]
