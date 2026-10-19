from django.db import models
class Client(models.Model):
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=80)
    email = models.EmailField()
    cree_le = models.DateTimeField(auto_now_add=True)

class Commande(models.Model):
    STATUTS = [("en_attente","En attente"),("payee","Payée"),("echouee","Échouée"),
               ("expiree","Expirée"),("remboursee","Remboursée")]
    reference = models.CharField(max_length=32, unique=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    metier_slug = models.CharField(max_length=120)
    montant_xaf = models.PositiveIntegerField()
    operateur = models.CharField(max_length=20, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="en_attente")
    date_paiement = models.DateTimeField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
