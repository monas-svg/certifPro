# Guide d'installation et de configuration — Agrégateur de paiement K-PAY

Ce guide couvre uniquement la partie **K-PAY** (création de compte, clés API,
webhook). Pour le reste du site (installation du serveur, notifications
e-mail/WhatsApp), voir `README.md`.

---

## 1. Créer votre compte K-PAY

1. Rendez-vous sur **https://kpay.site**.
2. Cliquez sur "Créer un compte" / "Sign up".
3. Renseignez les informations de votre activité (nom de l'entreprise,
   e-mail, téléphone).
4. Confirmez votre e-mail via le lien reçu.

À l'inscription, vous obtenez immédiatement l'accès à l'environnement
**sandbox** (test) — pas besoin d'attendre une validation pour commencer à
intégrer et tester.

---

## 2. Récupérer vos clés API (mode test)

1. Connectez-vous à votre tableau de bord K-PAY.
2. Ouvrez la section **Développeurs / API Keys**.
3. Copiez votre **clé secrète de test** (généralement préfixée `kp_test_...`).
4. Collez-la dans le fichier `.env` de votre serveur :
   ```
   KPAY_SECRET_KEY=kp_test_xxxxxxxxxxxxxxxx
   ```

⚠️ Ne partagez cette clé avec personne, ne la mettez jamais dans
`index.html` ni dans un message : elle reste uniquement dans `.env`, sur
votre serveur.

---

## 3. Tester le paiement en sandbox

1. Démarrez votre serveur (`node server.js`) avec la clé de **test**
   dans `.env`.
2. Ouvrez `index.html`, cliquez sur "Obtenir mon coupon", remplissez le
   formulaire et lancez un paiement.
3. K-PAY simule la transaction (numéros de test Mobile Money / cartes de
   test disponibles dans votre tableau de bord, section Sandbox).
4. Vérifiez dans les logs de votre serveur (`console.log`) que :
   - la requête vers `https://api.k-pay.app/v1/payments` réussit (statut
     200) et renvoie un `id` de paiement,
   - le webhook `/webhooks/kpay` est bien appelé une fois le paiement simulé
     confirmé,
   - `deliverCoupon()` et `notifyAdmin()` se déclenchent.

Ne passez à l'étape 4 que lorsque ce cycle complet fonctionne sans erreur.

---

## 4. Configurer le webhook

1. Dans votre tableau de bord K-PAY, ouvrez la section **Webhooks**.
2. Ajoutez l'URL publique de votre serveur :
   ```
   https://votre-domaine.com/webhooks/kpay
   ```
   (Le serveur doit être accessible publiquement — pas `localhost` — pour
   que K-PAY puisse vous notifier. En développement local, utilisez un
   tunnel type ngrok pour obtenir une URL temporaire testable.)
3. Copiez le **secret de signature du webhook** fourni par K-PAY et
   ajoutez-le à `.env` :
   ```
   KPAY_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx
   ```
4. Vérifiez, dans la documentation K-PAY (onglet Docs de votre tableau de
   bord), le nom exact de l'en-tête de signature envoyé avec chaque webhook
   (ex. `X-KPAY-Signature`) et l'algorithme utilisé. Ajustez si besoin la
   ligne correspondante dans `server.js` :
   ```js
   const signatureHeader = req.headers['x-kpay-signature'] || req.headers['signature'];
   ```

---

## 5. Passer en production

1. Dans votre tableau de bord K-PAY, complétez la **vérification d'identité
   (KYC)** : documents d'entreprise, pièce d'identité du responsable, etc.
2. Une fois approuvé, K-PAY débloque vos clés **live** (`kp_live_...`).
3. Remplacez dans `.env` :
   ```
   KPAY_SECRET_KEY=kp_live_xxxxxxxxxxxxxxxx
   ```
4. Refaites un test réel avec un petit montant avant d'annoncer l'ouverture
   des ventes.
5. Confirmez que l'URL de webhook configurée à l'étape 4 est bien active en
   mode production (certains agrégateurs demandent de la reconfigurer
   séparément pour le live).

---

## 6. Moyens de paiement disponibles

K-PAY couvre le Mobile Money (MTN, Orange, Airtel selon le pays), les cartes
Visa/Mastercard, et d'autres méthodes selon les 23 pays couverts. Le champ
exact à envoyer pour choisir un opérateur (`provider` dans la requête, ex.
`orange_cmr`, `mtn_cmr`) est documenté dans votre tableau de bord — vérifiez
la liste à jour pour le Cameroun avant la mise en production, ces valeurs
pouvant changer.

---

## 7. Support K-PAY

- Messagerie intégrée à votre tableau de bord.
- Communauté WhatsApp K-PAY (lien disponible dans votre tableau de bord).
- Assistant en ligne sur https://kpay.site (bouton en bas à droite du site).

---

## Checklist rapide

- [ ] Compte K-PAY créé et e-mail confirmé
- [ ] Clé secrète de **test** copiée dans `.env`
- [ ] Paiement de test réussi de bout en bout (paiement → webhook → coupon → notification admin)
- [ ] URL de webhook configurée avec le bon secret de signature
- [ ] KYC complété et clés **live** obtenues
- [ ] Test réel en production avec un petit montant
- [ ] Vente ouverte
