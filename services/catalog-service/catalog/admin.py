from django.contrib import admin
from .models import Metier, Competence, Ressource
class CompetenceInline(admin.TabularInline): model = Competence; extra = 1
class RessourceInline(admin.TabularInline): model = Ressource; extra = 1
@admin.register(Metier)
class MetierAdmin(admin.ModelAdmin):
    list_display = ("nom","slug","prix_xaf","prix_promo_xaf","actif")
    prepopulated_fields = {"slug": ("nom",)}
    inlines = [CompetenceInline, RessourceInline]
