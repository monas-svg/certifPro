from django.db import models
class Livraison(models.Model):
    STATUTS = [("en_attente","En attente"),("envoyee","Envoyée"),("echouee","Échouée")]
    commande_ref = models.CharField(max_length=32, unique=True)
    email_destinataire = models.EmailField()
    statut = models.CharField(max_length=20, choices=STATUTS, default="en_attente")
    tentatives = models.PositiveIntegerField(default=0)
    derniere_erreur = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le = models.DateTimeField(auto_now=True)
