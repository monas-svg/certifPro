from django.contrib import admin
from .models import Client, Commande
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("nom","prenom","email","cree_le")
    search_fields = ("email","nom","prenom")
@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("reference","client","metier_slug","montant_xaf","operateur","statut","cree_le")
    list_filter = ("statut","operateur","metier_slug")
    search_fields = ("reference","client__email")
