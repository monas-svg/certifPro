# Certifpro

Ce projet est une plateforme de vente et de paiement en architecture microservices, avec une interface publique et plusieurs services Django séparés.

Il est pensé pour fonctionner localement avec Docker et PostgreSQL.

## Ce que contient le projet

Le dépôt comprend plusieurs services :

- site-public : site vitrine et parcours client
- catalog-service : gestion du catalogue
- order-service : gestion des commandes
- payment-service : gestion des paiements et confirmation webhook
- delivery-service : gestion de la livraison et envoi des mails
- postgres : base de données PostgreSQL
- rabbitmq : broker de messages pour les événements
- gateway : point d’entrée Nginx

## Prérequis

Avant de lancer le projet, vérifie que tu as installé :

- Docker
- Docker Compose
- Git
- Python (si tu veux lancer un service directement hors Docker)

## Démarrage rapide

À la racine du projet, exécute :

```bash
docker compose up --build
```

Tu peux ensuite ouvrir les services suivants dans le navigateur :

- Site public : http://localhost:8010
- Gateway Nginx : http://localhost:8090
- RabbitMQ UI : http://localhost:15672
- PostgreSQL : localhost:5432

## Comptes de démonstration

Les identifiants par défaut sont configurés dans le fichier .env et dans le docker-compose :

- admin Django : admin / admin12345
- RabbitMQ : guest / guest

## Variables d’environnement

Un fichier .env est présent à la racine du projet. Il contient les paramètres de configuration comme :

- DEBUG
- SECRET_KEY
- DB_USER / DB_PASSWORD
- URLs internes des services
- configuration Chariow
- paramètres d’email

Tu peux modifier ce fichier selon ton environnement local.

## Structure du dépôt

```text
certifpro/
├── docker-compose.yml
├── .env
├── .env.example
├── README.md
├── scripts/
│   └── init-db.sql
├── services/
│   ├── catalog-service/
│   ├── delivery-service/
│   ├── gateway/
│   ├── order-service/
│   ├── payment-service/
│   └── site-public/
└── design/
```

## Services importants

### site-public
C’est le frontend public du site. Il affiche le catalogue, le formulaire d’inscription et le parcours de paiement.

### catalog-service
Il gère les produits et les données du catalogue.

### order-service
Il traite les commandes et les validations de commande.

### payment-service
Il centralise les paiements, la confirmation de transaction et le traitement webhooks.

### delivery-service
Il est responsable de la livraison et de l’envoi des messages liés à la commande.

## Gestion des données

Les données sont stockées dans PostgreSQL. Le conteneur est initialisé avec le fichier :

- scripts/init-db.sql

## Redémarrer proprement

Si tu veux relancer tout le projet après des changements :

```bash
docker compose down
docker compose up --build
```

## Dépannage rapide

### Un service ne démarre pas
Vérifie :

- que Docker tourne bien
- que le .env est présent
- que les ports ne sont pas déjà utilisés
- que les images se reconstruisent correctement

### La base ne répond pas
Tu peux relancer uniquement PostgreSQL :

```bash
docker compose up -d postgres
```

### Le site ne s’ouvre pas
Vérifie que le service site-public est bien démarré puis ouvre :

```text
http://localhost:8010
```

## Notes

Ce projet est un environnement de développement local. Pour une mise en production, il faudra revoir les secrets, les URLs, la sécurité et les configurations réseau.

---

Cette version est plus complète et plus claire pour démarrer le projet.
