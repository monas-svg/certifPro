from django.db import models
class Paiement(models.Model):
    STATUTS = [("initie","Initié"),("en_attente","En attente"),
               ("confirme","Confirmé"),("echoue","Échoué")]
    commande_ref = models.CharField(max_length=32, unique=True)
    operateur = models.CharField(max_length=20)
    montant_xaf = models.PositiveIntegerField()
    transaction_id = models.CharField(max_length=64, blank=True, db_index=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="initie")
    payload = models.JSONField(default=dict, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le = models.DateTimeField(auto_now=True)
