from django.contrib import admin
from .models import Paiement
@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("commande_ref","operateur","montant_xaf","transaction_id","statut","cree_le")
    list_filter = ("statut","operateur")
    search_fields = ("commande_ref","transaction_id")
