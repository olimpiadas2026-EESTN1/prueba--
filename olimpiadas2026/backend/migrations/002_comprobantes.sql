BEGIN;
ALTER TABLE pedidos DROP CONSTRAINT IF EXISTS pedidos_estado_check;
ALTER TABLE pedidos ADD CONSTRAINT pedidos_estado_check CHECK (estado IN ('creado','pendiente_pago','error_checkout','confirmado'));
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS pago_id text UNIQUE;
CREATE TABLE IF NOT EXISTS pedido_ventas (
 pedido_id uuid NOT NULL REFERENCES pedidos(id),
 venta_id integer NOT NULL REFERENCES ventas(vtas_id),
 PRIMARY KEY(pedido_id,venta_id)
);
CREATE TABLE IF NOT EXISTS correos_compra (
 pedido_id uuid PRIMARY KEY REFERENCES pedidos(id),
 destinatario text NOT NULL,
 asunto text NOT NULL,
 cuerpo text NOT NULL,
 estado text NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente','enviado','error')),
 intentos integer NOT NULL DEFAULT 0,
 enviado_en timestamptz,
 ultimo_error text
);
ALTER TABLE pedido_ventas ENABLE ROW LEVEL SECURITY;
ALTER TABLE correos_compra ENABLE ROW LEVEL SECURITY;
COMMIT;
