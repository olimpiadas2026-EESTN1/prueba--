BEGIN;
ALTER TABLE correos_compra ADD COLUMN IF NOT EXISTS tipo text NOT NULL DEFAULT 'comprador';
ALTER TABLE correos_compra DROP CONSTRAINT IF EXISTS correos_compra_pkey;
ALTER TABLE correos_compra ADD PRIMARY KEY (pedido_id,tipo);
ALTER TABLE correos_compra DROP CONSTRAINT IF EXISTS correos_compra_tipo_check;
ALTER TABLE correos_compra ADD CONSTRAINT correos_compra_tipo_check CHECK (tipo IN ('comprador','administrador'));
COMMIT;
