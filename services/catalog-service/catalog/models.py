from django.db import models

class Metier(models.Model):
    nom = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    prix_xaf = models.PositiveIntegerField(default=0)
    prix_promo_xaf = models.PositiveIntegerField(null=True, blank=True)
    visuel = models.URLField(blank=True)
    actif = models.BooleanField(default=True)
    @property
    def prix_actuel(self):
        return self.prix_promo_xaf if self.prix_promo_xaf else self.prix_xaf
    def __str__(self): return self.nom

class Competence(models.Model):
    metier = models.ForeignKey(Metier, related_name="competences", on_delete=models.CASCADE)
    libelle = models.CharField(max_length=200)
    ordre = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["ordre"]
    def __str__(self): return self.libelle

class Ressource(models.Model):
    TYPES = [("formation","Formation"),("certification","Certification")]
    metier = models.ForeignKey(Metier, related_name="ressources", on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    organisme = models.CharField(max_length=120)
    url = models.URLField()
    type = models.CharField(max_length=20, choices=TYPES, default="formation")
    ordre = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["ordre"]
    def __str__(self): return self.titre
