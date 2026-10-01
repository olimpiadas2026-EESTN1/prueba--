BEGIN;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS estado_gestion text NOT NULL DEFAULT 'pendiente' CHECK (estado_gestion IN ('pendiente','en_preparacion','listo','completado','en_revision'));
CREATE TABLE IF NOT EXISTS pedido_estados (
 id bigserial PRIMARY KEY,
 pedido_id uuid NOT NULL REFERENCES pedidos(id),
 ua_id integer NOT NULL REFERENCES usuario_administrativo(ua_id),
 creado_en timestamptz NOT NULL DEFAULT now(),
 anterior text NOT NULL,
 nuevo text NOT NULL,
 motivo text NOT NULL
);
ALTER TABLE pedido_estados ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS pedido_estados_pedido ON pedido_estados(pedido_id, creado_en);
COMMIT;
