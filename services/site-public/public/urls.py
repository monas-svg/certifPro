from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("metier/<slug:slug>/", views.metier, name="metier"),
    path("metier/<slug:slug>/formulaire/", views.formulaire, name="formulaire"),
    path("metier/<slug:slug>/payer/", views.payer, name="payer"),
    path("succes/", views.succes, name="succes"),
    path("mock-pay/<str:tx>/", views.mock_pay, name="mock_pay"),
    path("mock-pay/<str:tx>/confirm/", views.mock_pay_confirm, name="mock_pay_confirm"),
    path("politique-de-confidentialite/", views.politique_confidentialite, name="politique_confidentialite"),
    path("conditions-utilisation/", views.conditions_utilisation, name="conditions_utilisation"),
    path("renvoyer/", views.renvoyer, name="renvoyer"),
]
