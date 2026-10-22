from django.core.management.base import BaseCommand

from catalog.models import Competence, Metier, Ressource


METIERS = [
    {
        "nom": "Cybersécurité",
        "slug": "cybersecurite",
        "description": "Parcours complet pour sécuriser les systèmes, réseaux et applications.",
        "prix_xaf": 25000,
        "visuel": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "Sécurité des réseaux",
            "Analyse des vulnérabilités",
            "Sécurisation des applications",
            "Gestion des incidents",
            "Bonnes pratiques SOC",
        ],
        "ressources": [
            ("Introduction à la cybersécurité", "Cisco", "https://www.cisco.com/c/en/us/training-events/training-certifications/cybersecurity.html", "formation"),
            ("CompTIA Security+", "CompTIA", "https://www.comptia.org/certifications/security", "certification"),
            ("CEH v12", "EC-Council", "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/", "certification"),
        ],
    },
    {
        "nom": "Ingénieur DevOps",
        "slug": "ingenieur-devops",
        "description": "Automation, CI/CD, conteneurisation et infrastructure cloud pour livrer plus vite.",
        "prix_xaf": 29000,
        "visuel": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "Linux & automation",
            "Docker & Kubernetes",
            "CI/CD",
            "Terraform",
            "Monitoring & observabilité",
        ],
        "ressources": [
            ("Docker for Developers", "Docker", "https://docs.docker.com/", "formation"),
            ("Kubernetes Fundamentals", "Kubernetes", "https://kubernetes.io/training/", "formation"),
            ("CKA", "Linux Foundation", "https://training.linuxfoundation.org/certification/exam/cka/", "certification"),
        ],
    },
    {
        "nom": "Ingénieur Cloud",
        "slug": "ingenieur-cloud",
        "description": "Architecture cloud, scalabilité, sécurité et opérations sur AWS, Azure et GCP.",
        "prix_xaf": 27000,
        "visuel": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "Architecture cloud",
            "Scalabilité et disponibilité",
            "Systèmes distribués",
            "Sécurité cloud",
            "FinOps",
        ],
        "ressources": [
            ("AWS Cloud Practitioner", "AWS Training", "https://aws.amazon.com/training/", "formation"),
            ("Azure Fundamentals", "Microsoft Learn", "https://learn.microsoft.com/azure/architecture/", "formation"),
            ("AWS Solutions Architect", "AWS", "https://aws.amazon.com/certification/certified-solutions-architect-associate/", "certification"),
        ],
    },
    {
        "nom": "Développeur Backend",
        "slug": "developpeur-backend",
        "description": "API, bases de données, services métier et robustesse applicative.",
        "prix_xaf": 24000,
        "visuel": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "Python & Django",
            "API REST",
            "Modélisation SQL",
            "Tests et qualité",
            "Sécurité backend",
        ],
        "ressources": [
            ("Django for Professionals", "Django Software Foundation", "https://www.djangoproject.com/start/", "formation"),
            ("PostgreSQL Fundamentals", "PostgreSQL", "https://www.postgresql.org/docs/", "formation"),
            ("API Design Patterns", "Google Cloud", "https://cloud.google.com/apis/design", "formation"),
        ],
    },
    {
        "nom": "Développeur Full Stack",
        "slug": "developpeur-full-stack",
        "description": "Applications web complètes du frontend à l'API, en passant par la persistance.",
        "prix_xaf": 20000,
        "visuel": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "Frontend moderne",
            "API REST",
            "Base de données",
            "DevOps basique",
            "Déploiement",
        ],
        "ressources": [
            ("Modern JavaScript", "MDN", "https://developer.mozilla.org/fr/docs/Web/JavaScript", "formation"),
            ("React Fundamentals", "Meta Open Source", "https://react.dev/learn", "formation"),
            ("Node.js Certified Developer", "OpenJS", "https://training.linuxfoundation.org/certification/", "certification"),
        ],
    },
    {
        "nom": "Data Analyste",
        "slug": "data-analyste",
        "description": "Décodage des données, dashboards, reporting et prise de décision.",
        "prix_xaf": 18000,
        "visuel": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "SQL avancé",
            "Power BI",
            "Python Data",
            "Analyse statistique",
            "Tableaux de bord",
        ],
        "ressources": [
            ("SQL for Data Analysis", "Mode Analytics", "https://mode.com/sql-tutorial/", "formation"),
            ("Power BI Training", "Microsoft Learn", "https://learn.microsoft.com/power-bi/", "formation"),
            ("Google Data Analytics", "Coursera", "https://www.coursera.org/professional-certificates/google-data-analytics", "formation"),
        ],
    },
    {
        "nom": "Développeur IA",
        "slug": "developpeur-ia",
        "description": "Conception d'applications intelligentes, LLM et pipelines de données augmentées.",
        "prix_xaf": 32000,
        "visuel": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "LLM & RAG",
            "PyTorch",
            "Evaluation des modèles",
            "MLOps de base",
            "Agentic workflows",
        ],
        "ressources": [
            ("Introduction to AI", "Google AI", "https://ai.google/", "formation"),
            ("Prompt Engineering Guide", "OpenAI", "https://platform.openai.com/docs/guides/prompt-engineering", "formation"),
            ("LangChain tutorial", "LangChain", "https://python.langchain.com/docs/", "formation"),
        ],
    },
    {
        "nom": "Marketing digital",
        "slug": "marketing-digital",
        "description": "Acquisition, performance marketing et optimisation des campagnes digitales.",
        "prix_xaf": 15000,
        "visuel": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "SEO & contenu",
            "Stratégie de marque",
            "Analytics & attribution",
            "Funnels marketing",
            "Social media",
        ],
        "ressources": [
            ("HubSpot Academy", "HubSpot", "https://academy.hubspot.com/", "formation"),
            ("Google Analytics Academy", "Google", "https://analytics.google.com/analytics/academy/", "formation"),
            ("Meta Blueprint", "Meta", "https://www.facebook.com/business/learn", "formation"),
        ],
    },
    {
        "nom": "Google Ads",
        "slug": "google-ads",
        "description": "Gestion de campagnes Google Ads, recherche, shopping et optimisation des conversions.",
        "prix_xaf": 18000,
        "visuel": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "Stratégie Search & Display",
            "Campagnes Shopping",
            "Rédaction d'annonces",
            "Optimisation des conversions",
            "Analyse de performance",
        ],
        "ressources": [
            ("Google Ads Certification", "Google Skillshop", "https://skillshop.withgoogle.com/", "certification"),
            ("Google Ads Help Center", "Google", "https://support.google.com/google-ads/", "formation"),
            ("Google Analytics Academy", "Google", "https://analytics.google.com/analytics/academy/", "formation"),
        ],
    },
    {
        "nom": "Facebook Ads",
        "slug": "facebook-ads",
        "description": "Campagnes Meta Ads, ciblage d'audience, création de messages et optimisation du retour sur investissement.",
        "prix_xaf": 17000,
        "visuel": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=900&q=80",
        "competences": [
            "Ciblage et audience",
            "Publicités Meta",
            "Création de visuels & messages",
            "A/B testing",
            "Optimisation du ROAS",
        ],
        "ressources": [
            ("Meta Blueprint", "Meta", "https://www.facebook.com/business/learn", "formation"),
            ("Meta Ads Manager Guide", "Meta", "https://www.facebook.com/business/help", "formation"),
            ("HubSpot Academy", "HubSpot", "https://academy.hubspot.com/", "formation"),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the catalog with the default 8 training packs."

    def handle(self, *args, **options):
        stale_slugs = ["marketing-digital-ads", "marketing-digital-et-ads"]
        Metier.objects.filter(slug__in=stale_slugs).delete()

        created = 0
        for payload in METIERS:
            metier, metier_created = Metier.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "nom": payload["nom"],
                    "description": payload["description"],
                    "prix_xaf": payload["prix_xaf"],
                    "visuel": payload["visuel"],
                    "actif": True,
                },
            )
            if metier_created:
                created += 1

            metier.competences.all().delete()
            metier.ressources.all().delete()

            for order, libelle in enumerate(payload["competences"], start=1):
                Competence.objects.create(metier=metier, libelle=libelle, ordre=order)

            for order, (titre, organisme, url, type_name) in enumerate(payload["ressources"], start=1):
                Ressource.objects.create(
                    metier=metier,
                    titre=titre,
                    organisme=organisme,
                    url=url,
                    type=type_name,
                    ordre=order,
                )

        self.stdout.write(self.style.SUCCESS(f"Catalogue initialisé avec {Metier.objects.filter(actif=True).count()} métiers (nouveaux: {created})."))
