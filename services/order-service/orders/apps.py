import logging
from django.apps import AppConfig
log = logging.getLogger(__name__)

class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"
    def ready(self):
        from .models import Commande
        import events

        def on_payment_confirmed(payload):
            ref = payload["commande_ref"]
            try:
                cmd = Commande.objects.get(reference=ref)
            except Commande.DoesNotExist:
                return

            if cmd.statut == "payee":
                return

            from django.utils import timezone
            cmd.statut = "payee"
            cmd.date_paiement = timezone.now()
            cmd.save(update_fields=["statut", "date_paiement"])

        try:
            events.subscribe("payment.confirmed", "order-service.payment-confirmed", on_payment_confirmed)
        except Exception:
            log.exception("souscription impossible")
