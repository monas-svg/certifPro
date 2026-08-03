# CertifPass — site de vente de coupons (9 certifications Google / Coursera)

## Ce que contient ce dossier

- **public/index.html** — le site public : présentation de l'offre, les 9
  certifications (contenu tiré de votre catalogue PDF), et un tunnel de paiement.
- **server.js** — le backend Node/Express qui appelle K-PAY **en toute
  sécurité**, livre le coupon après paiement, et vous notifie par e-mail +
  WhatsApp.
- **Dockerfile / docker-compose.yml / .dockerignore / .env.example** — pour
  lancer toute l'application en un seul conteneur. Voir **DOCKER.md** pour le
  détail.
- **GUIDE_KPAY.md** — guide dédié pour la configuration de l'agrégateur K-PAY.

## Pourquoi un backend est indispensable

`index.html` est un fichier statique : tout ce qu'il contient est visible par
n'importe quel visiteur (clic droit → "Afficher le code source"). Une clé API
K-PAY placée dans ce fichier serait immédiatement récupérable et utilisable
par n'importe qui pour créer des paiements en votre nom.

C'est pourquoi le bouton "Payer avec K-PAY" appelle une route de **votre**
serveur (`/api/create-payment`), qui elle seule connaît la clé secrète K-PAY
(stockée dans une variable d'environnement, jamais dans le code envoyé au
navigateur).

```
Navigateur (public/index.html)
      │  POST /api/create-payment  (nom, email, tél., montant)
      ▼
Votre serveur (server.js)
      │  POST https://api.k-pay.app/v1/payments   Authorization: Bearer <clé secrète>
      ▼
K-PAY (traite le paiement Mobile Money / carte)
      │  Webhook → /webhooks/kpay  (statut : succès / échec)
      ▼
Votre serveur génère le(s) code(s) de coupon, les envoie au client,
et vous notifie (admin) par e-mail + WhatsApp
```

**Deux façons de lancer ce serveur :**
- **Avec Docker (recommandé)** — voir `DOCKER.md`, une seule commande
  (`docker compose up --build`) démarre tout.
- **Sans Docker** — voir les étapes ci-dessous.

## Mise en route

1. **Créer un compte K-PAY** sur https://kpay.site et récupérer :
   - votre clé API secrète (sandbox d'abord, puis production),
   - le secret utilisé pour signer les webhooks.
2. **Vérifier le format exact de l'API dans votre tableau de bord K-PAY**
   (onglet Documentation). Ce projet utilise le format publié publiquement sur
   la page d'accueil de K-PAY (`POST https://api.k-pay.app/v1/payments` avec
   `amount`, `currency`, `provider`, `customer`), mais les noms de champs pour
   les moyens de paiement (`provider`), le format exact du webhook et le nom
   de l'en-tête de signature peuvent varier — confirmez-les avant la mise en
   production. Adaptez `server.js` en conséquence.
3. **Installer et lancer le backend** (sans Docker) :
   ```bash
   npm install
   cp .env.example .env   # puis remplissez vos vraies valeurs
   node server.js
   ```
   Avec Docker, cette étape se résume à `docker compose up --build` — voir
   `DOCKER.md`.
4. `server.js` sert automatiquement `public/index.html` — pas besoin
   d'hébergement séparé. Configurez seulement l'URL de webhook
   (`https://votre-domaine.com/webhooks/kpay`) dans votre tableau de bord
   K-PAY.
5. Passer `KPAY_SECRET_KEY` en clé **live** et retester tout le tunnel avant
   d'annoncer l'ouverture des ventes.

## Modifier le contenu

- **Prix / quantités** : dans `public/index.html`, variable `UNIT_PRICE` (JS
  en bas de page) et les `<option>` du champ "Nombre de coupons".
- **Descriptions des 9 certifications** : section `#certifications`, une
  `.cert-card` par certificat — le texte vient de votre catalogue PDF.
- **FAQ** : section `#faq`, blocs `<details>` — ajoutez ou modifiez librement.

## Recevoir le formulaire d'inscription par e-mail + WhatsApp

Dès qu'un paiement est confirmé, `server.js` vous envoie (à vous,
l'administrateur — pas au client) un récapitulatif du formulaire rempli, par
e-mail **et** par WhatsApp. Cela ne demande pas votre clé K-PAY : deux autres
identifiants, distincts, à garder eux aussi uniquement dans `.env`.

`nodemailer` est déjà listé dans `package.json` — rien à installer à part
(`npm install`, ou automatique avec Docker).

**1. Créer un mot de passe d'application Gmail** (Gmail bloque désormais le
SMTP avec votre mot de passe habituel) :
- Activez la validation en 2 étapes sur votre compte Google.
- Allez sur `myaccount.google.com/apppasswords`, créez un mot de passe
  d'application "Mail", copiez la valeur générée.

**2. Obtenir une clé WhatsApp CallMeBot (gratuit, ~2 minutes)** :
- Ajoutez le contact `+34 644 51 95 23` sur WhatsApp.
- Envoyez-lui : `I allow callmebot to send me messages`.
- Il répond avec votre clé API personnelle.

**3. Compléter votre `.env`** (voir aussi `.env.example`) :
```
GMAIL_USER=sermoshop@gmail.com
GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx
ADMIN_NOTIFY_EMAIL=sermoshop@gmail.com
CALLMEBOT_PHONE=+237600000000
CALLMEBOT_APIKEY=xxxxxxx
```

Aucune de ces clés — K-PAY, Gmail ou CallMeBot — ne doit jamais être collée
dans une conversation, ni apparaître dans `public/index.html` : elles
restent uniquement dans le `.env` de votre serveur, qui n'est jamais envoyé
au navigateur (et exclu de l'image Docker par `.dockerignore`).

*Limite à connaître* : CallMeBot est pensé pour des alertes personnelles à
faible volume (quelques dizaines de messages/jour). Si votre volume de ventes
grandit, migrez vers l'API officielle WhatsApp Business (Meta Cloud API) ou
Twilio — je peux réécrire `notifyAdmin()` pour l'un ou l'autre le moment venu.

## Ce qui n'est pas inclus (à prévoir)

- Base de données réelle pour stocker les commandes (le fichier exemple
  utilise une simple `Map` en mémoire, effacée à chaque redémarrage).
- Envoi effectif des e-mails/SMS de coupon (stub `deliverCoupon()` à
  compléter avec votre prestataire d'e-mail/SMS).
- Génération et suivi des codes de coupon dans un vrai système de gestion
  (pour éviter la réutilisation d'un même code par plusieurs personnes).
