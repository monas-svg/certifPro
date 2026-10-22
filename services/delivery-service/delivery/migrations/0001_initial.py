from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Livraison",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("commande_ref", models.CharField(max_length=32, unique=True)),
                ("email_destinataire", models.EmailField(max_length=254)),
                ("statut", models.CharField(choices=[("en_attente", "En attente"), ("envoyee", "Envoyée"), ("echouee", "Échouée")], default="en_attente", max_length=20)),
                ("tentatives", models.PositiveIntegerField(default=0)),
                ("derniere_erreur", models.TextField(blank=True)),
                ("cree_le", models.DateTimeField(auto_now_add=True)),
                ("maj_le", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
