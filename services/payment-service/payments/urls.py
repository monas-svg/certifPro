from django.urls import path
from .api import initiate, webhook, get_paiement
urlpatterns = [
    path("api/payments/initiate/", initiate),
    path("api/payments/webhook/", webhook),
    path("api/payments/<str:commande_ref>/", get_paiement),
]
