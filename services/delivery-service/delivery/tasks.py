import logging, requests
from django.conf import settings
from django.core.mail import send_mail
from .models import Livraison
import events
log = logging.getLogger(__name__)

def _fetch_order(ref):
    r = requests.get(f"{settings.ORDER_URL}/api/internal/orders/{ref}/",
                     headers={"X-Service-Token": settings.SERVICE_TOKEN}, timeout=10)
    r.raise_for_status(); return r.json()

def _fetch_ressources(slug):
    r = requests.get(f"{settings.CATALOG_URL}/api/internal/metiers/{slug}/ressources/",
                     headers={"X-Service-Token": settings.SERVICE_TOKEN}, timeout=10)
    r.raise_for_status(); return r.json()

def _build_body(order, ressources):
    lignes = [f"- [{r['type']}] {r['titre']} ({r['organisme']})\n  {r['url']}"
              for r in ressources["ressources"]]
    return (f"Bonjour {order['client']['prenom']},\n\n"
            f"Merci pour votre achat du pack « {ressources['metier']['nom']} ».\n"
            f"Voici vos liens :\n\n" + "\n".join(lignes) +
            "\n\nÀ bientôt sur Certifpro.\n")

def handle_payment_confirmed(payload):
    ref = payload["commande_ref"]
    log.info("delivery: %s", ref)

    if Livraison.objects.filter(commande_ref=ref, statut="envoyee").exists():
        return

    try:
        order = _fetch_order(ref)
    except Exception as exc:
        Livraison.objects.update_or_create(
            commande_ref=ref,
            defaults={"email_destinataire": "", "statut": "echouee", "derniere_erreur": str(exc)},
        )
        return

    email = order["client"]["email"]
    livraison, _ = Livraison.objects.get_or_create(
        commande_ref=ref,
        defaults={"email_destinataire": email, "statut": "en_attente"},
    )

    if livraison.statut == "envoyee":
        return

    try:
        ressources = _fetch_ressources(order["metier_slug"])
        send_mail(
            subject=f"Vos liens Certifpro — {ressources['metier']['nom']}",
            message=_build_body(order, ressources),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        livraison.email_destinataire = email
        livraison.statut = "envoyee"
        livraison.tentatives += 1
        livraison.derniere_erreur = ""
        livraison.save(update_fields=["email_destinataire", "statut", "tentatives", "derniere_erreur", "maj_le"])
        events.publish("delivery.sent", {"commande_ref": ref, "email": email})
    except Exception as exc:
        livraison.tentatives += 1
        livraison.statut = "echouee"
        livraison.derniere_erreur = str(exc)
        livraison.save(update_fields=["statut", "tentatives", "derniere_erreur", "maj_le"])
        raise
