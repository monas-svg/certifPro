/**
 * db.js
 * -----
 * Connexion PostgreSQL + fonctions d'accès à la table "orders".
 * Remplace le stockage en mémoire (Map) utilisé précédemment dans server.js.
 *
 * Variables d'environnement attendues (voir .env.example) :
 *   DATABASE_URL=postgres://user:password@host:5432/dbname
 *   (ou bien PGHOST / PGPORT / PGUSER / PGPASSWORD / PGDATABASE séparément)
 */

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');

const pool = new Pool(
  process.env.DATABASE_URL
    ? {
        connectionString: process.env.DATABASE_URL,
        // Certains hébergeurs (Render, Railway, Supabase...) exigent SSL.
        // PGSSL=true dans .env pour l'activer.
        ssl: process.env.PGSSL === 'true' ? { rejectUnauthorized: false } : false
      }
    : {
        host: process.env.PGHOST || 'localhost',
        port: Number(process.env.PGPORT) || 5432,
        user: process.env.PGUSER || 'certifpass',
        password: process.env.PGPASSWORD || 'certifpass',
        database: process.env.PGDATABASE || 'certifpass'
      }
);

pool.on('error', (err) => {
  console.error('Erreur inattendue du pool PostgreSQL', err);
});

/**
 * Crée la table "orders" si elle n'existe pas encore (à appeler une fois au
 * démarrage du serveur). Idempotent — sans danger à ré-exécuter.
 */
async function initSchema() {
  const schemaPath = path.join(__dirname, 'db', 'schema.sql');
  const schemaSql = fs.readFileSync(schemaPath, 'utf8');
  await pool.query(schemaSql);
}

/** Vérifie que la base répond (utilisé par /healthz). */
async function ping() {
  await pool.query('SELECT 1');
}

/** Crée une nouvelle commande à l'état "pending". */
async function createOrder({ orderId, fullname, email, phone, quantity, amount, currency, kpayPaymentId }) {
  const { rows } = await pool.query(
    `INSERT INTO orders (order_id, status, fullname, email, phone, quantity, amount, currency, kpay_payment_id)
     VALUES ($1, 'pending', $2, $3, $4, $5, $6, $7, $8)
     RETURNING *`,
    [orderId, fullname, email, phone, quantity || 1, amount, currency || 'XAF', kpayPaymentId || null]
  );
  return rows[0];
}

/** Récupère une commande par son identifiant interne (order_id). */
async function getOrder(orderId) {
  const { rows } = await pool.query('SELECT * FROM orders WHERE order_id = $1', [orderId]);
  return rows[0] || null;
}

/** Met à jour le statut d'une commande (et optionnellement les codes coupon). */
async function updateOrderStatus(orderId, status, couponCodes) {
  const { rows } = await pool.query(
    `UPDATE orders
     SET status = $2,
         coupon_codes = COALESCE($3, coupon_codes),
         updated_at = now()
     WHERE order_id = $1
     RETURNING *`,
    [orderId, status, couponCodes || null]
  );
  return rows[0] || null;
}

module.exports = {
  pool,
  initSchema,
  ping,
  createOrder,
  getOrder,
  updateOrderStatus
};
