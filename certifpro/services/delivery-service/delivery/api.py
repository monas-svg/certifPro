from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Livraison
from .tasks import handle_payment_confirmed

@api_view(["GET"])
def get_livraison(request, commande_ref):
    try: l = Livraison.objects.get(commande_ref=commande_ref)
    except Livraison.DoesNotExist: return Response({"detail":"introuvable"}, status=404)
    return Response({"commande_ref": l.commande_ref, "email": l.email_destinataire,
                     "statut": l.statut, "tentatives": l.tentatives})

@api_view(["POST"])
def renvoyer(request):
    ref = request.data.get("commande_ref")
    if not ref: return Response({"detail":"commande_ref requis"}, status=400)
    handle_payment_confirmed({"commande_ref": ref})
    return Response({"status":"ok"})
