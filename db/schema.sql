-- Schéma PostgreSQL pour CertifPass
-- Ce script est exécuté automatiquement au démarrage du serveur (voir db.js),
-- il peut donc aussi être lancé à la main si besoin :
--   psql "$DATABASE_URL" -f db/schema.sql

CREATE TABLE IF NOT EXISTS orders (
  order_id         TEXT PRIMARY KEY,
  status           TEXT NOT NULL DEFAULT 'pending',
  fullname         TEXT NOT NULL,
  email            TEXT NOT NULL,
  phone            TEXT NOT NULL,
  quantity         INTEGER NOT NULL DEFAULT 1,
  amount           NUMERIC NOT NULL,
  currency         TEXT NOT NULL DEFAULT 'XAF',
  kpay_payment_id  TEXT,
  coupon_codes     TEXT[],
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Recherche rapide par référence de paiement K-PAY (utilisé par le webhook)
CREATE INDEX IF NOT EXISTS idx_orders_kpay_payment_id ON orders (kpay_payment_id);
