from django.conf import settings
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Metier, Competence, Ressource

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta: model = Competence; fields = ["id","libelle","ordre"]

class PublicRessourceSerializer(serializers.ModelSerializer):
    class Meta: model = Ressource; fields = ["id","titre","organisme","type","ordre"]

class InternalRessourceSerializer(serializers.ModelSerializer):
    class Meta: model = Ressource; fields = ["id","titre","organisme","type","url","ordre"]

class MetierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metier
        fields = ["id","nom","slug","description","prix_xaf","prix_promo_xaf","prix_actuel","visuel"]

class MetierDetailSerializer(serializers.ModelSerializer):
    competences = CompetenceSerializer(many=True)
    ressources = PublicRessourceSerializer(many=True)
    class Meta:
        model = Metier
        fields = ["id","nom","slug","description","prix_xaf","prix_promo_xaf","prix_actuel","visuel","competences","ressources"]

class MetierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Metier.objects.filter(actif=True).prefetch_related("competences","ressources")
    lookup_field = "slug"
    def get_serializer_class(self):
        return MetierDetailSerializer if self.action == "retrieve" else MetierListSerializer

def _check_token(request):
    return request.headers.get("X-Service-Token") == settings.SERVICE_TOKEN

@api_view(["GET"])
def internal_ressources(request, slug):
    if not _check_token(request):
        return Response({"detail":"forbidden"}, status=403)
    metier = Metier.objects.prefetch_related("ressources").get(slug=slug)
    return Response({
        "metier": {"nom": metier.nom, "slug": metier.slug},
        "ressources": InternalRessourceSerializer(metier.ressources.all(), many=True).data,
    })
