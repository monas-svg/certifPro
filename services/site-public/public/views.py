import requests
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render

ALLOWED_OPERATORS = {"mtn", "orange", "wave"}


def _request_json(method, url, *, json_data=None, params=None):
    try:
        response = requests.request(method, url, json=json_data, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Service indisponible pour {url}: {exc}") from exc


def _get_metier(slug):
    return _request_json("GET", f"{settings.CATALOG_URL}/api/metiers/{slug}/")


def _get_metiers():
    return _request_json("GET", f"{settings.CATALOG_URL}/api/metiers/")


def _sort_metiers_for_homepage(metiers):
    priority = {"marketing-digital": 0, "google-ads": 1, "facebook-ads": 2}
    return sorted(metiers, key=lambda m: priority.get((m or {}).get("slug"), 99))


def _validate_customer_data(post_data):
    nom = (post_data.get("nom") or "").strip()
    prenom = (post_data.get("prenom") or "").strip()
    email = (post_data.get("email") or "").strip()
    operateur = (post_data.get("operateur") or "").strip().lower()

    if not (nom and prenom and email and operateur):
        return None
    if operateur not in ALLOWED_OPERATORS:
        return None

    return {"nom": nom, "prenom": prenom, "email": email, "operateur": operateur}


def index(request):
    metiers = _sort_metiers_for_homepage(_get_metiers())
    return render(request, "index.html", {"metiers": metiers})


def metier(request, slug):
    return render(request, "metier.html", {"metier": _get_metier(slug)})


def formulaire(request, slug):
    return render(request, "formulaire.html", {"metier": _get_metier(slug)})


def payer(request, slug):
    if request.method != "POST":
        return redirect("metier", slug=slug)

    customer = _validate_customer_data(request.POST)
    if customer is None:
        return HttpResponseBadRequest("Champs invalides")

    try:
        commande = _request_json(
            "POST",
            f"{settings.ORDER_URL}/api/orders/",
            json_data={
                "nom": customer["nom"],
                "prenom": customer["prenom"],
                "email": customer["email"],
                "metier_slug": slug,
                "operateur": customer["operateur"],
            },
        )
        paiement = _request_json(
            "POST",
            f"{settings.PAYMENT_URL}/api/payments/initiate/",
            json_data={
                "commande_ref": commande["reference"],
                "operateur": customer["operateur"],
                "montant_xaf": commande["montant_xaf"],
                "email": customer["email"],
            },
        )
    except RuntimeError:
        return HttpResponseBadRequest("Service de paiement indisponible")

    return redirect(paiement["checkout_url"])


def succes(request):
    return render(request, "succes.html", {"reference": request.GET.get("ref", "")})


def mock_pay(request, tx):
    return render(request, "mock_pay.html", {"transaction_id": tx, "reference": request.GET.get("ref", "")})


def mock_pay_confirm(request, tx):
    if request.method != "POST":
        return redirect("mock_pay", tx=tx)

    reference = (request.POST.get("reference") or "").strip()
    try:
        _request_json(
            "POST",
            f"{settings.PAYMENT_URL}/api/payments/webhook/",
            json_data={"transaction_id": tx},
        )
    except RuntimeError:
        return HttpResponseBadRequest("Paiement non confirmé")

    return redirect(f"/succes/?ref={reference}")


def politique_confidentialite(request):
    return render(request, "politique_confidentialite.html")


def conditions_utilisation(request):
    return render(request, "conditions_utilisation.html")


def renvoyer(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        if email:
            return render(request, "renvoyer.html", {"message": f"Si une commande existe pour {email}, les liens ont été renvoyés."})

    return render(request, "renvoyer.html", {"message": None})
