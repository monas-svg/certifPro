#!/usr/bin/env bash
# create_structure.sh — Crée l'arborescence complète du projet Certifpro
set -euo pipefail

ROOT="${1:-certifpro}"

# --- Transformer ROOT en chemin ABSOLU, une fois pour toutes -----------------
mkdir -p "$ROOT"
ABS_ROOT="$(cd "$ROOT" && pwd)"
echo "▶ Création de l'arborescence dans $ABS_ROOT"

# --- 1. Dossiers -------------------------------------------------------------
mkdir -p "$ABS_ROOT"/scripts
mkdir -p "$ABS_ROOT"/services/gateway
mkdir -p "$ABS_ROOT"/services/catalog-service/catalog
mkdir -p "$ABS_ROOT"/services/order-service/orders
mkdir -p "$ABS_ROOT"/services/payment-service/payments
mkdir -p "$ABS_ROOT"/services/delivery-service/delivery
mkdir -p "$ABS_ROOT"/services/site-public/public
mkdir -p "$ABS_ROOT"/services/site-public/templates

# --- 2. Fichiers racine ------------------------------------------------------
touch "$ABS_ROOT"/docker-compose.yml
touch "$ABS_ROOT"/README.md
touch "$ABS_ROOT"/.gitignore
touch "$ABS_ROOT"/scripts/init-db.sql

# --- 3. Gateway --------------------------------------------------------------
touch "$ABS_ROOT"/services/gateway/nginx.conf

# --- 4. catalog-service ------------------------------------------------------
touch "$ABS_ROOT"/services/catalog-service/{Dockerfile,requirements.txt,manage.py,settings.py,urls.py,events.py}
touch "$ABS_ROOT"/services/catalog-service/catalog/{__init__.py,apps.py,models.py,api.py,admin.py,urls.py}

# --- 5. order-service --------------------------------------------------------
touch "$ABS_ROOT"/services/order-service/{Dockerfile,requirements.txt,manage.py,settings.py,urls.py,events.py}
touch "$ABS_ROOT"/services/order-service/orders/{__init__.py,apps.py,models.py,api.py,admin.py,urls.py}

# --- 6. payment-service ------------------------------------------------------
touch "$ABS_ROOT"/services/payment-service/{Dockerfile,requirements.txt,manage.py,settings.py,urls.py,events.py}
touch "$ABS_ROOT"/services/payment-service/payments/{__init__.py,apps.py,models.py,providers.py,api.py,admin.py,urls.py}

# --- 7. delivery-service -----------------------------------------------------
touch "$ABS_ROOT"/services/delivery-service/{Dockerfile,requirements.txt,manage.py,settings.py,urls.py,events.py}
touch "$ABS_ROOT"/services/delivery-service/delivery/{__init__.py,apps.py,models.py,tasks.py,api.py,admin.py,urls.py}

# --- 8. site-public ----------------------------------------------------------
touch "$ABS_ROOT"/services/site-public/{Dockerfile,requirements.txt,manage.py,settings.py,urls.py,events.py}
touch "$ABS_ROOT"/services/site-public/public/{__init__.py,apps.py,views.py,urls.py}
touch "$ABS_ROOT"/services/site-public/templates/{base.html,index.html,metier.html,formulaire.html,mock_pay.html,succes.html,renvoyer.html}

# --- 9. Permissions ----------------------------------------------------------
chmod +x "$ABS_ROOT"/services/*/manage.py 2>/dev/null || true

# --- 10. Récapitulatif -------------------------------------------------------
echo ""
echo "✅ Arborescence créée :"
echo ""
cd "$ABS_ROOT"
find . -print | sort | sed 's|[^/]*/|  |g'
echo ""
echo "Total fichiers : $(find . -type f | wc -l)"
echo "Total dossiers : $(find . -type d | wc -l)"