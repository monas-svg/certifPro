/**
 * server-exemple.js
 * ------------------
 * Exemple minimal de backend Node/Express pour brancher K-PAY (https://kpay.site)
 * derrière le site statique index.html (CertifPass).
 *
 * POURQUOI UN BACKEND ?
 * Le front-end (index.html) ne doit JAMAIS contenir votre clé secrète K-PAY :
 * n'importe quel visiteur pourrait l'ouvrir dans l'inspecteur du navigateur et
 * l'utiliser. Ce petit serveur reçoit la demande du navigateur, appelle K-PAY
 * avec la clé secrète (gardée côté serveur, dans une variable d'environnement),
 * puis renvoie au navigateur seulement ce dont il a besoin (un lien de paiement
 * ou un statut).
 *
 * Installation :
 *   npm init -y
 *   npm install express cors dotenv nodemailer
 *   node server-exemple.js
 *
 * Variables d'environnement (.env) :
 *   KPAY_SECRET_KEY=kp_live_xxxxxxxxxxxxxxxx   (ou kp_test_... en sandbox)
 *   KPAY_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx
 *   PORT=3000
 *
 *   # Notification e-mail immédiate (Gmail SMTP)
 *   GMAIL_USER=sermoshop@gmail.com
 *   GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx        (mot de passe d'application, PAS votre mot de passe Gmail normal — à générer, voir plus bas)
 *   ADMIN_NOTIFY_EMAIL=sermoshop@gmail.com     (où recevoir les notifications — ici la même adresse que GMAIL_USER)
 *
 *   # Notification WhatsApp immédiate (CallMeBot)
 *   CALLMEBOT_PHONE=+237600000000              (VOTRE numéro WhatsApp, celui qui reçoit l'alerte)
 *   CALLMEBOT_APIKEY=xxxxxxx                   (obtenue en suivant les 3 étapes ci-dessous)
 *
 * COMMENT OBTENIR UN MOT DE PASSE D'APPLICATION GMAIL :
 *   1. Activez la validation en 2 étapes sur votre compte Google
 *      (myaccount.google.com/security).
 *   2. Allez sur myaccount.google.com/apppasswords, créez un mot de passe
 *      d'application "Mail", copiez la valeur générée dans GMAIL_APP_PASSWORD.
 *   Gmail refuse désormais l'envoi SMTP avec votre mot de passe normal — le
 *   mot de passe d'application est obligatoire.
 *
 * COMMENT OBTENIR UNE CLÉ CALLMEBOT (gratuit, ~2 minutes) :
 *   1. Ajoutez le numéro +34 644 51 95 23 à vos contacts WhatsApp.
 *   2. Envoyez-lui le message : "I allow callmebot to send me messages"
 *   3. Il vous répond avec votre clé API personnelle → copiez-la dans
 *      CALLMEBOT_APIKEY. CALLMEBOT_PHONE est le numéro depuis lequel vous
 *      avez envoyé ce message (au format international, avec le +).
 *
 * IMPORTANT :
 * - Récupérez votre clé API et le secret de webhook depuis votre tableau de
 *   bord K-PAY (https://kpay.site).
 * - Le corps de requête ci-dessous (amount, currency, provider, customer)
 *   reflète le format publié sur la page d'accueil de K-PAY. Confirmez les
 *   noms de champs exacts et l'URL de webhook dans VOTRE documentation K-PAY
 *   (onglet "Docs" de votre tableau de bord) avant la mise en production —
 *   certains agrégateurs distinguent sandbox et prod avec des hôtes différents.
 * - AUCUNE de ces clés (K-PAY, Gmail, CallMeBot) ne doit jamais apparaître
 *   dans index.html ni être partagée avec qui que ce soit : elles vivent
 *   uniquement dans le fichier .env de votre serveur.
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const crypto = require('crypto');
const nodemailer = require('nodemailer');
const db = require('./db');

const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Sert index.html (et tout autre fichier statique du dossier) — un seul
// conteneur héberge donc à la fois le site et l'API.
app.use(express.static(path.join(__dirname, 'public')));

const KPAY_API_URL = 'https://api.k-pay.app/v1/payments';
const KPAY_SECRET_KEY = process.env.KPAY_SECRET_KEY;
const KPAY_WEBHOOK_SECRET = process.env.KPAY_WEBHOOK_SECRET;

// --- Notification immédiate à VOUS (l'administrateur), pas au client ---
const GMAIL_USER = process.env.GMAIL_USER;
const GMAIL_APP_PASSWORD = process.env.GMAIL_APP_PASSWORD;
const ADMIN_NOTIFY_EMAIL = process.env.ADMIN_NOTIFY_EMAIL || GMAIL_USER;
const CALLMEBOT_PHONE = process.env.CALLMEBOT_PHONE;
const CALLMEBOT_APIKEY = process.env.CALLMEBOT_APIKEY;

const mailTransporter = (GMAIL_USER && GMAIL_APP_PASSWORD)
  ? nodemailer.createTransport({
      service: 'gmail',
      auth: { user: GMAIL_USER, pass: GMAIL_APP_PASSWORD }
    })
  : null;

// Les commandes sont désormais persistées dans PostgreSQL (voir db.js et
// db/schema.sql) au lieu d'être gardées en mémoire.

/**
 * 1) Le front-end appelle cette route quand l'utilisateur clique
 *    "Payer avec K-PAY".
 */
app.post('/api/create-payment', async (req, res) => {
  const { fullname, email, phone, quantity, amount, currency } = req.body;

  if (!fullname || !email || !phone || !amount) {
    return res.status(400).json({ error: 'missing_fields' });
  }

  const orderId = 'order_' + crypto.randomBytes(6).toString('hex');

  try {
    const kpayRes = await fetch(KPAY_API_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${KPAY_SECRET_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount,
        currency: currency || 'XAF',
        customer: phone,
        // "provider" dépend des moyens supportés dans votre pays — ex: orange_cmr,
        // mtn_cmr, card, etc. Consultez votre documentation K-PAY pour la liste
        // exacte des valeurs disponibles pour le Cameroun.
        metadata: { order_id: orderId, fullname, email, quantity }
      })
    });

    if (!kpayRes.ok) {
      const errBody = await kpayRes.text();
      console.error('K-PAY error', kpayRes.status, errBody);
      return res.status(502).json({ error: 'kpay_error' });
    }

    const payment = await kpayRes.json(); // ex: { id: "pay_8x2k", status: "pending", checkout_url: "..." }

    await db.createOrder({
      orderId,
      fullname,
      email,
      phone,
      quantity,
      amount,
      currency,
      kpayPaymentId: payment.id
    });

    return res.json({
      id: payment.id,
      status: payment.status,
      checkout_url: payment.checkout_url || null,
      order_id: orderId
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'server_error' });
  }
});

/**
 * 2) K-PAY appelle CETTE route (webhook) quand un paiement change de statut.
 *    Configurez cette URL publique (ex: https://votre-domaine.com/webhooks/kpay)
 *    dans votre tableau de bord K-PAY.
 */
app.post(
  '/webhooks/kpay',
  express.raw({ type: '*/*' }), // on garde le corps brut pour vérifier la signature
  async (req, res) => {
    const signatureHeader = req.headers['x-kpay-signature'] || req.headers['signature'];

    // Vérification de signature façon HMAC — ADAPTEZ le nom de l'en-tête et
    // l'algorithme exact d'après la documentation "Webhooks" de votre
    // tableau de bord K-PAY avant la mise en production.
    if (KPAY_WEBHOOK_SECRET && signatureHeader) {
      const expected = crypto
        .createHmac('sha256', KPAY_WEBHOOK_SECRET)
        .update(req.body)
        .digest('hex');

      if (expected !== signatureHeader) {
        console.warn('Signature de webhook invalide');
        return res.status(401).send('invalid signature');
      }
    }

    let event;
    try {
      event = JSON.parse(req.body.toString('utf8'));
    } catch {
      return res.status(400).send('invalid payload');
    }

    const orderId = event?.data?.metadata?.order_id;
    const status = event?.data?.status; // "success" | "failed" | "pending" ...

    if (orderId) {
      try {
        const order = await db.updateOrderStatus(orderId, status);

        if (order && (status === 'success' || status === 'succeeded')) {
          deliverCoupon(order);
          notifyAdmin(order); // vous envoie le formulaire d'inscription par e-mail + WhatsApp
        }
      } catch (err) {
        console.error('Erreur mise à jour commande en base :', err.message);
        return res.status(500).send('db_error');
      }
    }

    res.status(200).send('ok');
  }
);

/**
 * 3) Une fois le paiement confirmé, on génère et on envoie le(s) code(s) de
 *    coupon. Remplacez ce stub par votre propre logique (génération de codes
 *    uniques + envoi email/SMS via votre prestataire).
 */
async function deliverCoupon(order) {
  const codes = Array.from({ length: order.quantity || 1 }, () =>
    'CERTIF-' + crypto.randomBytes(4).toString('hex').toUpperCase()
  );

  console.log(`Envoi de ${codes.length} coupon(s) à ${order.email} / ${order.phone}:`, codes);

  try {
    await db.updateOrderStatus(order.order_id, order.status, codes);
  } catch (err) {
    console.error('Erreur enregistrement des codes coupon en base :', err.message);
  }

  // TODO: brancher votre service d'e-mail (ex: Resend, SendGrid) et/ou SMS
  // (ex: le service SMS Gateway de votre agrégateur) pour envoyer réellement
  // ces codes au client, avec les instructions d'activation Coursera.
}

/**
 * 3bis) Notifie l'ADMINISTRATEUR (vous) du formulaire d'inscription rempli
 *       par le client, par e-mail ET par WhatsApp, immédiatement après un
 *       paiement confirmé. Ceci est séparé de deliverCoupon(), qui envoie le
 *       code de coupon AU CLIENT.
 */
async function notifyAdmin(order) {
  const summary =
    `Nouvelle inscription payée — CertifPass\n` +
    `Nom : ${order.fullname}\n` +
    `E-mail : ${order.email}\n` +
    `Téléphone : ${order.phone}\n` +
    `Coupons : ${order.quantity}\n` +
    `Montant : ${order.amount} FCFA\n` +
    `Référence K-PAY : ${order.kpay_payment_id}`;

  // --- E-mail (Gmail SMTP) ---
  if (mailTransporter && ADMIN_NOTIFY_EMAIL) {
    try {
      await mailTransporter.sendMail({
        from: GMAIL_USER,
        to: ADMIN_NOTIFY_EMAIL,
        subject: `Nouvelle inscription payée — ${order.fullname}`,
        text: summary
      });
      console.log('Notification e-mail envoyée à', ADMIN_NOTIFY_EMAIL);
    } catch (err) {
      console.error('Échec envoi e-mail admin :', err.message);
    }
  } else {
    console.warn('GMAIL_USER / GMAIL_APP_PASSWORD non configurés — notification e-mail ignorée.');
  }

  // --- WhatsApp (CallMeBot) ---
  if (CALLMEBOT_PHONE && CALLMEBOT_APIKEY) {
    try {
      const url =
        `https://api.callmebot.com/whatsapp.php` +
        `?phone=${encodeURIComponent(CALLMEBOT_PHONE)}` +
        `&text=${encodeURIComponent(summary)}` +
        `&apikey=${encodeURIComponent(CALLMEBOT_APIKEY)}`;
      const res = await fetch(url);
      console.log('Notification WhatsApp envoyée, statut :', res.status);
    } catch (err) {
      console.error('Échec envoi WhatsApp admin :', err.message);
    }
  } else {
    console.warn('CALLMEBOT_PHONE / CALLMEBOT_APIKEY non configurés — notification WhatsApp ignorée.');
  }
}

/**
 * 4) (Optionnel) route pour que le front-end vérifie l'état d'une commande
 *    pendant qu'il attend la confirmation.
 */
app.get('/api/order-status/:orderId', async (req, res) => {
  try {
    const order = await db.getOrder(req.params.orderId);
    if (!order) return res.status(404).json({ error: 'not_found' });
    res.json({ status: order.status });
  } catch (err) {
    console.error('Erreur lecture commande en base :', err.message);
    res.status(500).json({ error: 'db_error' });
  }
});

// Route de santé, utile pour Docker HEALTHCHECK / orchestrateurs.
// Vérifie aussi que la base PostgreSQL répond.
app.get('/healthz', async (req, res) => {
  try {
    await db.ping();
    res.status(200).json({ status: 'ok' });
  } catch (err) {
    console.error('Healthcheck : base de données injoignable :', err.message);
    res.status(503).json({ status: 'db_unavailable' });
  }
});

const PORT = process.env.PORT || 3000;

// On s'assure que la table "orders" existe avant d'accepter des requêtes.
db.initSchema()
  .then(() => {
    app.listen(PORT, '0.0.0.0', () =>
      console.log(`Serveur CertifPass démarré sur le port ${PORT}`)
    );
  })
  .catch((err) => {
    console.error('Impossible d\'initialiser la base de données PostgreSQL :', err.message);
    process.exit(1);
  });
