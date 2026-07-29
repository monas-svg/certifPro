# CertifPass — Dockerisation

L'application (site + backend K-PAY + notifications) tourne maintenant dans
un seul conteneur Docker.

## Structure du projet

```
.
├── Dockerfile
├── docker-compose.yml   ← lance l'app ET une base PostgreSQL
├── .dockerignore
├── .env.example        ← à copier en .env avec vos vraies valeurs
├── package.json
├── server.js            ← backend Express (API K-PAY, webhook, notifications)
├── db.js                ← connexion PostgreSQL + accès à la table "orders"
├── db/
│   └── schema.sql        ← schéma de la table "orders" (créé automatiquement au démarrage)
├── public/
│   └── index.html       ← le site, servi automatiquement par server.js
├── README.md
└── GUIDE_KPAY.md
```

## 1. Préparer votre fichier `.env`

```bash
cp .env.example .env
```

Ouvrez `.env` et remplissez vos vraies valeurs (clé K-PAY, Gmail, CallMeBot
— voir `README.md` et `GUIDE_KPAY.md` pour savoir où les récupérer).

`.env` ne doit **jamais** être commité dans Git ni copié dans l'image Docker
— `.dockerignore` l'exclut déjà automatiquement.

## 2. Lancer avec Docker Compose (recommandé)

```bash
docker compose up --build
```

Le site est alors accessible sur **http://localhost:3000**.

Pour l'arrêter :
```bash
docker compose down
```

Pour relancer après une modification du code :
```bash
docker compose up --build
```

Pour voir les logs en continu (utile pour suivre les paiements et
notifications) :
```bash
docker compose logs -f
```

## 3. Ou lancer avec Docker seul (sans compose)

```bash
docker build -t certifpass .
docker run -d \
  --name certifpass \
  -p 3000:3000 \
  --env-file .env \
  --restart unless-stopped \
  certifpass
```

## 4. Vérifier que tout fonctionne

- Le site : http://localhost:3000
- Le healthcheck : http://localhost:3000/healthz → doit répondre `{"status":"ok"}`
- `docker compose ps` doit afficher le conteneur en `healthy` après ~10-40s.

## 5. Déployer sur un serveur / VPS

1. Copiez tout le dossier du projet sur votre serveur (hors `.env` si vous
   préférez le recréer directement là-bas pour éviter de transporter des
   secrets).
2. Installez Docker et Docker Compose sur le serveur si nécessaire.
3. Créez le `.env` sur le serveur (jamais transmis par e-mail/chat).
4. Lancez `docker compose up -d --build`.
5. Placez un reverse proxy devant (Nginx, Caddy ou Traefik) pour gérer votre
   nom de domaine et le certificat HTTPS — indispensable pour que K-PAY
   puisse appeler votre webhook en `https://` et pour rassurer vos clients
   au moment du paiement.
6. Configurez l'URL de webhook (`https://votre-domaine.com/webhooks/kpay`)
   dans le tableau de bord K-PAY, comme décrit dans `GUIDE_KPAY.md`.

## 6. Mettre à jour l'application

```bash
git pull            # ou copiez les nouveaux fichiers
docker compose up --build -d
```

Le conteneur redémarre avec le nouveau code ; `.env` n'est pas affecté.

## Notes

- L'image utilise `node:20-alpine` (légère) et exécute l'application avec un
  utilisateur non-root (`USER node`) par sécurité.
- Le healthcheck Docker interroge `/healthz` toutes les 30 secondes (et
  vérifie désormais aussi que PostgreSQL répond).
- Les commandes sont persistées dans PostgreSQL (voir `db.js` et
  `db/schema.sql`) : un redémarrage du conteneur `certifpass` n'efface plus
  rien. Les données PostgreSQL elles-mêmes vivent dans le volume Docker
  `certifpass_pgdata`, qui survit à `docker compose down` (utilisez
  `docker compose down -v` si vous voulez vraiment tout effacer, y compris
  la base).
- Pour sauvegarder la base : `docker compose exec postgres pg_dump -U certifpass certifpass > backup.sql`.
