from django.urls import path
from .api import get_livraison, renvoyer
urlpatterns = [
    path("api/delivery/<str:commande_ref>/", get_livraison),
    path("api/delivery/renvoyer/", renvoyer),
]
