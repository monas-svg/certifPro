"""Payment provider abstraction and Chariow adapter."""
import os
import uuid

import requests


class PaymentProvider:
    def initiate(self, *, commande_ref, montant_xaf, operateur, email):
        raise NotImplementedError

    def verify(self, transaction_id):
        raise NotImplementedError


class MockProvider(PaymentProvider):
    def __init__(self):
        self.site_url = os.environ.get("SITE_URL", "http://localhost:8080")

    def initiate(self, *, commande_ref, montant_xaf, operateur, email):
        tx = "MOCK-" + uuid.uuid4().hex[:12].upper()
        return {
            "transaction_id": tx,
            "checkout_url": f"{self.site_url}/mock-pay/{tx}?ref={commande_ref}",
            "statut": "en_attente",
        }

    def verify(self, transaction_id):
        return {"transaction_id": transaction_id, "statut": "confirme"}


class ChariowProvider(PaymentProvider):
    def __init__(self):
        self.base_url = os.environ.get("CHARIOW_BASE_URL", "https://api.chariow.com/v1").rstrip("/")
        self.api_key = os.environ.get("CHARIOW_API_KEY", "")
        self.secret = os.environ.get("CHARIOW_SECRET", "")
        self.enabled = os.environ.get("CHARIOW_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
        self.payment_endpoint = os.environ.get("CHARIOW_PAYMENT_ENDPOINT", "/payments")
        self.site_url = os.environ.get("SITE_URL", "http://localhost:8080")

    def _headers(self):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.secret:
            headers["X-API-Secret"] = self.secret
        return headers

    def initiate(self, *, commande_ref, montant_xaf, operateur, email):
        if not self.enabled or not self.api_key:
            return MockProvider().initiate(commande_ref=commande_ref, montant_xaf=montant_xaf, operateur=operateur, email=email)

        payload = {
            "reference": commande_ref,
            "amount": montant_xaf,
            "currency": "XAF",
            "operator": operateur,
            "email": email,
            "success_url": f"{self.site_url}/succes/?ref={commande_ref}",
            "cancel_url": f"{self.site_url}/formulaire/{commande_ref}/",
        }

        try:
            response = requests.post(
                f"{self.base_url}{self.payment_endpoint}",
                json=payload,
                headers=self._headers(),
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            tx = data.get("transaction_id") or data.get("id") or data.get("reference") or uuid.uuid4().hex[:12].upper()
            checkout_url = (
                data.get("checkout_url")
                or data.get("payment_url")
                or data.get("link")
                or f"{self.site_url}/mock-pay/{tx}?ref={commande_ref}"
            )
            return {"transaction_id": tx, "checkout_url": checkout_url, "statut": "en_attente"}
        except requests.RequestException:
            return MockProvider().initiate(commande_ref=commande_ref, montant_xaf=montant_xaf, operateur=operateur, email=email)

    def verify(self, transaction_id):
        if not self.enabled:
            return {"transaction_id": transaction_id, "statut": "confirme"}
        try:
            response = requests.get(
                f"{self.base_url}/payments/{transaction_id}",
                headers=self._headers(),
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            statut = data.get("status") or data.get("statut") or "confirme"
            return {"transaction_id": transaction_id, "statut": statut}
        except requests.RequestException:
            return {"transaction_id": transaction_id, "statut": "confirme"}
