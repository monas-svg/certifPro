import uuid, requests
from django.conf import settings
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Client, Commande
import events

class OrderCreateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=80)
    prenom = serializers.CharField(max_length=80)
    email = serializers.EmailField()
    metier_slug = serializers.SlugField()
    operateur = serializers.ChoiceField(choices=["mtn","orange","wave"], required=False, allow_blank=True)

class CommandeSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    def get_client(self, obj):
        return {"nom": obj.client.nom, "prenom": obj.client.prenom, "email": obj.client.email}
    class Meta:
        model = Commande
        fields = ["reference","metier_slug","montant_xaf","operateur","statut",
                  "date_paiement","cree_le","client"]

def _check_token(request):
    return request.headers.get("X-Service-Token") == settings.SERVICE_TOKEN

@api_view(["POST"])
def create_order(request):
    ser = OrderCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    r = requests.get(f"{settings.CATALOG_URL}/api/metiers/{d['metier_slug']}/", timeout=10)
    if r.status_code != 200:
        return Response({"detail": "métier introuvable"}, status=400)
    metier = r.json()

    client, _ = Client.objects.get_or_create(
        email=d["email"],
        defaults={"nom": d["nom"], "prenom": d["prenom"]},
    )

    existing = (
        Commande.objects.filter(
            client=client,
            metier_slug=metier["slug"],
            montant_xaf=metier.get("prix_actuel") or metier["prix_xaf"],
            operateur=d.get("operateur", ""),
        )
        .order_by("-cree_le")
        .first()
    )
    if existing and existing.statut != "payee":
        return Response(CommandeSerializer(existing).data, status=200)
    if existing and existing.statut == "payee":
        return Response({"detail": "commande déjà payée", "reference": existing.reference}, status=409)

    ref = "CP-" + uuid.uuid4().hex[:10].upper()
    cmd = Commande.objects.create(
        reference=ref,
        client=client,
        metier_slug=metier["slug"],
        montant_xaf=metier.get("prix_actuel") or metier["prix_xaf"],
        operateur=d.get("operateur", ""),
    )
    events.publish("order.created", {
        "reference": ref,
        "metier_slug": cmd.metier_slug,
        "montant_xaf": cmd.montant_xaf,
        "email": client.email,
    })
    return Response(CommandeSerializer(cmd).data, status=201)

@api_view(["GET"])
def get_order(request, reference):
    try: cmd = Commande.objects.select_related("client").get(reference=reference)
    except Commande.DoesNotExist: return Response({"detail":"introuvable"}, status=404)
    return Response(CommandeSerializer(cmd).data)

@api_view(["GET"])
def internal_order(request, reference):
    if not _check_token(request):
        return Response({"detail":"forbidden"}, status=403)
    try: cmd = Commande.objects.select_related("client").get(reference=reference)
    except Commande.DoesNotExist: return Response({"detail":"introuvable"}, status=404)
    return Response({
        "reference": cmd.reference, "metier_slug": cmd.metier_slug,
        "montant_xaf": cmd.montant_xaf, "statut": cmd.statut,
        "client": {"nom": cmd.client.nom, "prenom": cmd.client.prenom, "email": cmd.client.email}})
