import logging
from django.apps import AppConfig
log = logging.getLogger(__name__)
class DeliveryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "delivery"
    def ready(self):
        import events
        from .tasks import handle_payment_confirmed
        try:
            events.subscribe("payment.confirmed","delivery-service.payment-confirmed",
                             handle_payment_confirmed)
        except Exception:
            log.exception("souscription impossible")
