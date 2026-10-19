from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from . import api
from .models import Paiement


class PaymentIdempotenceTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("payments.api.events.publish")
    def test_initiate_is_idempotent_for_same_order(self, mock_publish):
        provider = SimpleNamespace()
        provider.initiate = lambda **kwargs: {
            "transaction_id": "TX-123",
            "checkout_url": "https://example.test/pay/TX-123",
        }

        payload = {
            "commande_ref": "CP-ABC123",
            "operateur": "mtn",
            "montant_xaf": 50000,
            "email": "client@example.com",
        }

        with patch.object(api, "provider", provider):
            req1 = self.factory.post("/api/payments/initiate/", payload, format="json")
            resp1 = api.initiate(req1)

            req2 = self.factory.post("/api/payments/initiate/", payload, format="json")
            resp2 = api.initiate(req2)

        self.assertEqual(resp1.status_code, 201)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(Paiement.objects.filter(commande_ref="CP-ABC123").count(), 1)
        self.assertEqual(Paiement.objects.get(commande_ref="CP-ABC123").transaction_id, "TX-123")
        self.assertEqual(mock_publish.call_count, 1)

    @patch("payments.api.events.publish")
    def test_webhook_repeated_confirmation_is_ignored(self, mock_publish):
        paiement = Paiement.objects.create(
            commande_ref="CP-REPEATED",
            operateur="orange",
            montant_xaf=25000,
            transaction_id="TX-REPEATED",
            statut="en_attente",
        )

        provider = SimpleNamespace()
        provider.verify = lambda transaction_id: {"transaction_id": transaction_id, "statut": "confirme"}

        payload = {"transaction_id": "TX-REPEATED"}
        request = self.factory.post("/api/payments/webhook/", payload, format="json")

        with patch.object(api, "provider", provider):
            resp1 = api.webhook(request)
            resp2 = api.webhook(request)

        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.data["status"], "already_confirmed")
        paiement.refresh_from_db()
        self.assertEqual(paiement.statut, "confirme")
        self.assertEqual(mock_publish.call_count, 1)
