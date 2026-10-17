from django.contrib import admin
from .models import Livraison
@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ("commande_ref","email_destinataire","statut","tentatives","cree_le")
    list_filter = ("statut",)
    search_fields = ("commande_ref","email_destinataire")
