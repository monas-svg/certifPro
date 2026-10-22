from django.core.management import call_command
from django.test import TestCase

from .models import Metier


class SeedCatalogTests(TestCase):
    def test_seed_catalog_creates_expected_catalog(self):
        Metier.objects.create(
            slug="marketing-digital-ads",
            nom="Marketing digital & Ads",
            description="Ancien pack obsolète",
            prix_xaf=15000,
            actif=True,
        )

        call_command("seed_catalog")

        self.assertEqual(Metier.objects.filter(actif=True).count(), 10)
        self.assertNotIn("marketing-digital-ads", set(Metier.objects.filter(actif=True).values_list("slug", flat=True)))
        self.assertIn("Marketing digital", list(Metier.objects.filter(actif=True).values_list("nom", flat=True)))
        self.assertIn("Google Ads", list(Metier.objects.filter(actif=True).values_list("nom", flat=True)))
        self.assertIn("Facebook Ads", list(Metier.objects.filter(actif=True).values_list("nom", flat=True)))
