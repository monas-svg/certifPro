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

const path = require('path');

const app = express();

// Nécessaire pour que req.ip reflète la vraie IP du client quand le serveur
// tourne derrière un reverse proxy (Nginx, Docker, etc.) — sinon le
// rate-limiter ci-dessous verrait toujours la même IP interne.
app.set('trust proxy', 1);

// Restreignez CORS à votre propre domaine en production via CORS_ORIGIN
// (ex: CORS_ORIGIN=https://certifpass.com). Par défaut ("*") tout le monde
// peut appeler l'API depuis n'importe quel site — à éviter en production.
const CORS_ORIGIN = process.env.CORS_ORIGIN || '*';
app.use(cors({ origin: CORS_ORIGIN }));
app.use(express.json());

// Sert index.html (et tout autre fichier statique du dossier) — un seul
// conteneur héberge donc à la fois le site et l'API.
app.use(express.static(path.join(__dirname, 'public')));

// SebPay configuration using the official documentation contract.
const SEBPAY_API_URL = process.env.SEBPAY_API_URL || 'https://newapi.sebpay.bj/api/v1/collections';
const SEBPAY_PUBLIC_KEY = process.env.SEBPAY_PUBLIC_KEY;
const SEBPAY_SECRET_KEY = process.env.SEBPAY_SECRET_KEY;
const SEBPAY_CALLBACK_URL = process.env.SEBPAY_CALLBACK_URL || 'http://localhost:3000/webhooks/sebpay';
const SEBPAY_OPERATOR = process.env.SEBPAY_OPERATOR || 'mtn';
const SEBPAY_COUNTRY = process.env.SEBPAY_COUNTRY || 'BJ';
const SEBPAY_WEBHOOK_HEADER = process.env.SEBPAY_WEBHOOK_HEADER || 'x-sebpay-signature';
const SEBPAY_WEBHOOK_ALGO = process.env.SEBPAY_WEBHOOK_ALGO || 'sha256';
const SEBPAY_FETCH_TIMEOUT_MS = Number(process.env.SEBPAY_FETCH_TIMEOUT_MS || 15000);
const SEBPAY_MOCK = String(process.env.SEBPAY_MOCK || '').toLowerCase() === 'true' || String(process.env.SEBPAY_API_URL || '').toLowerCase() === 'mock';

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

// Warn early if critical SebPay config is missing.
if (!SEBPAY_PUBLIC_KEY) {
  console.warn('ATTENTION: SEBPAY_PUBLIC_KEY non configurée — paiements impossibles');
}
if (!SEBPAY_SECRET_KEY) {
  console.warn('ATTENTION: SEBPAY_SECRET_KEY non configurée — paiements et webhooks non sécurisés');
}

// Très simple "base" en mémoire pour la démo — remplacez par une vraie base
// de données (Postgres, MySQL, etc.) en production.
const orders = new Map();

// --- Prix de référence, connu UNIQUEMENT du serveur ---
// Le front-end peut afficher ce qu'il veut, mais c'est CETTE valeur qui sert
// à calculer le montant réellement envoyé à K-PAY. Ne jamais faire confiance
// au champ "amount" envoyé par le navigateur.
const UNIT_PRICE_FCFA = 50000;
const CURRENCY = 'XOF';
const MAX_QUANTITY = 20; // garde-fou anti-abus

// --- Limiteur de débit minimal, sans dépendance externe ---
// Empêche un même client de spammer la création de paiements ou le webhook.
function makeRateLimiter({ windowMs, max }) {
  const hits = new Map(); // ip -> [timestamps]
  return (req, res, next) => {
    const ip = req.ip || req.socket.remoteAddress || 'unknown';
    const now = Date.now();
    const arr = (hits.get(ip) || []).filter((t) => now - t < windowMs);
    arr.push(now);
    hits.set(ip, arr);
    if (arr.length > max) {
      return res.status(429).json({ error: 'too_many_requests' });
    }
    next();
  };
}
const paymentRateLimiter = makeRateLimiter({ windowMs: 60_000, max: 10 }); // 10 req/min/IP
const webhookRateLimiter = makeRateLimiter({ windowMs: 60_000, max: 60 });

/**
 * 1) Le front-end appelle cette route quand l'utilisateur clique
 *    "Payer avec K-PAY".
 */
app.post('/api/create-payment', paymentRateLimiter, async (req, res) => {
  // IMPORTANT : on n'accepte PAS "amount" ni "currency" venant du client.
  // Le prix est recalculé ici, côté serveur, à partir d'UNIT_PRICE_FCFA.
  // Un client ne peut donc plus modifier la requête réseau pour payer moins.
  const { fullname, email, phone, quantity } = req.body;

  const qty = Number.parseInt(quantity, 10);

  if (!fullname || !email || !phone || !Number.isInteger(qty)) {
    return res.status(400).json({ error: 'missing_fields' });
  }
  if (qty < 1 || qty > MAX_QUANTITY) {
    return res.status(400).json({ error: 'invalid_quantity' });
  }
  // Validation basique du format e-mail pour éviter les envois SMTP invalides.
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'invalid_email' });
  }

  const amount = UNIT_PRICE_FCFA * qty;
  const currency = CURRENCY;
  const orderId = 'order_' + crypto.randomBytes(6).toString('hex');
  const normalizedPhone = String(phone).replace(/\D/g, '');

  try {
    const sebpayFetch = async (url, opts = {}) => {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), SEBPAY_FETCH_TIMEOUT_MS);
      try {
        return await fetch(url, { signal: controller.signal, ...opts });
      } finally {
        clearTimeout(id);
      }
    };

    if (SEBPAY_MOCK) {
      const payment = {
        id: 'mock_' + crypto.randomBytes(6).toString('hex'),
        status: 'approved',
        data: { transaction_id: 'mock_' + crypto.randomBytes(6).toString('hex') },
        provider_link: null
      };

      orders.set(orderId, {
        status: 'approved',
        fullname,
        email,
        phone: normalizedPhone,
        quantity: qty,
        amount,
        sebpay_payment_id: payment.id
      });

      try {
        const order = orders.get(orderId);
        deliverCoupon(order);
        await notifyAdmin(order);
      } catch (err) {
        console.error('Erreur lors du mock delivery/notify:', err && err.message ? err.message : err);
      }

      return res.json({ id: payment.id, status: payment.status, checkout_url: payment.provider_link || null, order_id: orderId, mock: true });
    }

    if (!SEBPAY_PUBLIC_KEY || !SEBPAY_SECRET_KEY) {
      return res.status(500).json({ error: 'sebpay_not_configured' });
    }

    const sebpayRes = await sebpayFetch(SEBPAY_API_URL, {
      method: 'POST',
      headers: {
        'X-Public-Key': SEBPAY_PUBLIC_KEY,
        'X-Secret-Key': SEBPAY_SECRET_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount,
        currency,
        phone: normalizedPhone,
        operator: SEBPAY_OPERATOR,
        country: SEBPAY_COUNTRY,
        external_reference: orderId,
        callback_url: SEBPAY_CALLBACK_URL,
        metadata: { fullname, email, quantity: qty }
      })
    });

    if (!sebpayRes.ok) {
      const errBody = await sebpayRes.text();
      console.error('SEBPAY error', sebpayRes.status, errBody);
      return res.status(502).json({ error: 'sebpay_error' });
    }

    const payment = await sebpayRes.json();
    const paymentId = payment?.data?.transaction_id || payment?.transaction_id || payment?.id || orderId;
    const paymentStatus = payment?.data?.status || payment?.status || 'pending';
    const checkoutUrl = payment?.data?.provider_link || payment?.provider_link || payment?.checkout_url || payment?.payment_url || null;

    orders.set(orderId, {
      status: paymentStatus,
      fullname,
      email,
      phone: normalizedPhone,
      quantity: qty,
      amount,
      sebpay_payment_id: paymentId
    });

    return res.json({
      id: paymentId,
      status: paymentStatus,
      checkout_url: checkoutUrl,
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
function handleSebpayWebhook(req, res) {
  const signatureHeader = req.headers[SEBPAY_WEBHOOK_HEADER] || req.headers['x-sebpay-signature'] || req.headers['signature'];

  if (!SEBPAY_SECRET_KEY || !signatureHeader) {
    console.warn('Webhook SebPay rejeté : signature absente ou secret non configuré');
    return res.status(401).send('signature required');
  }

  const normalizedHeader = String(signatureHeader).replace(/^sha256=/i, '').trim();
    const rawBodyStr = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    const expected = crypto
      .createHmac(SEBPAY_WEBHOOK_ALGO, SEBPAY_SECRET_KEY)
      .update(rawBodyStr, 'utf8')
      .digest('hex');

  const expectedBuf = Buffer.from(expected, 'utf8');
  const receivedBuf = Buffer.from(normalizedHeader, 'utf8');

  const signatureValid =
    expectedBuf.length === receivedBuf.length &&
    crypto.timingSafeEqual(expectedBuf, receivedBuf);

  if (!signatureValid) {
    console.warn('Signature de webhook SebPay invalide');
    return res.status(401).send('invalid signature');
  }

  let event;
  try {
    if (Buffer.isBuffer(req.body)) {
      event = JSON.parse(req.body.toString('utf8'));
    } else if (typeof req.body === 'object') {
      event = req.body;
    } else {
      event = JSON.parse(String(req.body));
    }
  } catch (e) {
    console.warn('Webhook parse error:', e && e.message);
    return res.status(400).send('invalid payload');
  }

  const status = event?.status || event?.data?.status || event?.transaction?.status || '';
  const orderId = String(
    event?.external_reference ||
    event?.data?.external_reference ||
    event?.transaction?.external_reference ||
    event?.metadata?.order_id ||
    ''
  ).trim();

  if (orderId && orders.has(orderId)) {
    const order = orders.get(orderId);
    const normalizedStatus = status === 'approved' ? 'approved' : status === 'rejected' ? 'rejected' : 'pending';
    const alreadyProcessed = order.status === 'approved' || order.status === 'success' || order.status === 'succeeded';

    order.status = normalizedStatus;
    orders.set(orderId, order);

    if ((normalizedStatus === 'approved' || normalizedStatus === 'success' || normalizedStatus === 'succeeded') && !alreadyProcessed) {
      deliverCoupon(order);
      notifyAdmin(order);
    }
  }

  return res.status(200).send('ok');
}

app.post(
  '/webhooks/sebpay',
  webhookRateLimiter,
  express.raw({ type: '*/*' }),
  handleSebpayWebhook
);

app.post('/webhooks/kpay', webhookRateLimiter, express.raw({ type: '*/*' }), handleSebpayWebhook);

/**
 * 3) Une fois le paiement confirmé, on génère et on envoie le(s) code(s) de
 *    coupon. Remplacez ce stub par votre propre logique (génération de codes
 *    uniques + envoi email/SMS via votre prestataire).
 */
function deliverCoupon(order) {
  const codes = Array.from({ length: order.quantity || 1 }, () =>
    'CERTIF-' + crypto.randomBytes(4).toString('hex').toUpperCase()
  );

  console.log(`Envoi de ${codes.length} coupon(s) à ${order.email} / ${order.phone}:`, codes);

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
    `Référence SEBPAY : ${order.sebpay_payment_id || order.kpay_payment_id || 'non disponible'}`;

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
app.get('/api/order-status/:orderId', (req, res) => {
  const order = orders.get(req.params.orderId);
  if (!order) return res.status(404).json({ error: 'not_found' });
  res.json({ status: order.status });
});

// Route de santé, utile pour Docker HEALTHCHECK / orchestrateurs
app.get('/healthz', (req, res) => res.status(200).json({ status: 'ok' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () =>
  console.log(`Serveur CertifPass démarré sur le port ${PORT}`)
);
