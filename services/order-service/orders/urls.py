from django.urls import path
from .api import create_order, get_order, internal_order
urlpatterns = [
    path("api/orders/", create_order),
    path("api/orders/<str:reference>/", get_order),
    path("api/internal/orders/<str:reference>/", internal_order),
]
