from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.urls import resolve

from .api import get_livraison, renvoyer
from .models import Livraison
from .tasks import handle_payment_confirmed


class DeliveryRouteTests(SimpleTestCase):
    def test_renvoyer_route_is_specific_before_generic_reference_route(self):
        self.assertEqual(resolve("/api/delivery/renvoyer/").func, renvoyer)
        self.assertEqual(resolve("/api/delivery/CP-ABC123/").func, get_livraison)


class DeliveryIdempotenceTests(TestCase):
    @patch("delivery.tasks.events.publish")
    @patch("delivery.tasks.send_mail")
    @patch("delivery.tasks._fetch_ressources")
    @patch("delivery.tasks._fetch_order")
    def test_handle_payment_confirmed_sends_links_once_and_uses_idempotence(
        self, mock_fetch_order, mock_fetch_ressources, mock_send_mail, mock_publish
    ):
        mock_fetch_order.return_value = {
            "reference": "CP-ABC123",
            "client": {"prenom": "Alice", "email": "alice@example.com"},
            "metier_slug": "google-ads",
        }
        mock_fetch_ressources.return_value = {
            "metier": {"nom": "Google Ads"},
            "ressources": [
                {"type": "Cours", "titre": "Google Ads Basics", "organisme": "Certifpro", "url": "https://example.com/ads"},
                {"type": "Certification", "titre": "Google Ads Certification", "organisme": "Google", "url": "https://example.com/cert"},
            ],
        }

        Livraison.objects.create(
            commande_ref="CP-ABC123",
            email_destinataire="alice@example.com",
            statut="en_attente",
            tentatives=0,
        )

        handle_payment_confirmed({"commande_ref": "CP-ABC123"})
        handle_payment_confirmed({"commande_ref": "CP-ABC123"})

        self.assertEqual(mock_send_mail.call_count, 1)
        body = mock_send_mail.call_args.kwargs["message"]
        self.assertIn("Google Ads", body)
        self.assertIn("https://example.com/ads", body)
        self.assertIn("https://example.com/cert", body)

        livraison = Livraison.objects.get(commande_ref="CP-ABC123")
        self.assertEqual(livraison.statut, "envoyee")
        self.assertEqual(livraison.tentatives, 1)
        self.assertEqual(mock_publish.call_count, 1)
