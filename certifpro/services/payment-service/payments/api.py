import hmac, hashlib, json
from django.conf import settings
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Paiement
from .providers import ChariowProvider
import events

provider = ChariowProvider()

class InitiateSerializer(serializers.Serializer):
    commande_ref = serializers.CharField(max_length=32)
    operateur = serializers.ChoiceField(choices=["mtn","orange","wave"])
    montant_xaf = serializers.IntegerField(min_value=1)
    email = serializers.EmailField()

class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = ["commande_ref","operateur","montant_xaf","transaction_id","statut","cree_le","maj_le"]

@api_view(["POST"])
def initiate(request):
    ser = InitiateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    paiement, created = Paiement.objects.get_or_create(
        commande_ref=d["commande_ref"],
        defaults={
            "operateur": d["operateur"],
            "montant_xaf": d["montant_xaf"],
            "statut": "initie",
        },
    )

    if not created and paiement.statut == "confirme":
        return Response({"detail": "déjà payé", "transaction_id": paiement.transaction_id}, status=409)

    if not created and paiement.statut in {"en_attente", "initie"} and paiement.transaction_id:
        return Response(
            {
                "transaction_id": paiement.transaction_id,
                "checkout_url": paiement.payload.get("checkout_url") or f"/mock-pay/{paiement.transaction_id}?ref={paiement.commande_ref}",
            },
            status=200,
        )

    res = provider.initiate(
        commande_ref=paiement.commande_ref,
        montant_xaf=paiement.montant_xaf,
        operateur=paiement.operateur,
        email=d["email"],
    )
    paiement.transaction_id = res["transaction_id"]
    paiement.statut = "en_attente"
    paiement.payload = {"checkout_url": res.get("checkout_url"), "provider": "chariow"}
    paiement.save(update_fields=["transaction_id", "statut", "payload", "maj_le"])
    events.publish("payment.initiated", {
        "commande_ref": paiement.commande_ref,
        "transaction_id": paiement.transaction_id,
    })
    return Response(
        {"transaction_id": paiement.transaction_id, "checkout_url": res["checkout_url"]},
        status=201,
    )

def _signature_ok(request):
    raw_body = request.body
    sig = request.headers.get("X-Signature", "")
    if not sig:
        dev_secret = settings.WEBHOOK_SECRET in {"", "dev-webhook-secret", "change-me-in-production"}
        return bool(settings.DEBUG) or dev_secret
    expected = hmac.new(
        settings.WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(sig, expected)

@api_view(["POST"])
def webhook(request):
    if not _signature_ok(request):
        return Response({"detail": "signature invalide"}, status=403)

    payload = {}
    raw_body = request.body
    if raw_body:
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (TypeError, ValueError, UnicodeDecodeError):
            payload = {}

    tx = payload.get("transaction_id") if isinstance(payload, dict) else None
    if not tx:
        return Response({"detail": "transaction_id manquant"}, status=400)

    try:
        paiement = Paiement.objects.get(transaction_id=tx)
    except Paiement.DoesNotExist:
        return Response({"detail": "transaction inconnue"}, status=404)

    if paiement.statut == "confirme":
        return Response({"status": "already_confirmed", "transaction_id": tx})

    verif = provider.verify(tx)
    if verif.get("statut") != "confirme":
        paiement.statut = "echoue"
        paiement.payload = payload
        paiement.save(update_fields=["statut", "payload", "maj_le"])
        return Response({"status": "failed", "transaction_id": tx})

    paiement.statut = "confirme"
    paiement.payload = payload
    paiement.save(update_fields=["statut", "payload", "maj_le"])
    events.publish("payment.confirmed", {
        "commande_ref": paiement.commande_ref,
        "transaction_id": paiement.transaction_id,
        "montant_xaf": paiement.montant_xaf,
    })
    return Response({"status": "ok", "transaction_id": tx})

@api_view(["GET"])
def get_paiement(request, commande_ref):
    try: p = Paiement.objects.get(commande_ref=commande_ref)
    except Paiement.DoesNotExist: return Response({"detail":"introuvable"}, status=404)
    return Response(PaiementSerializer(p).data)
