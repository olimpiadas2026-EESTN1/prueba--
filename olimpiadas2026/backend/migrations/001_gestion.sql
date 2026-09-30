BEGIN;
CREATE TABLE IF NOT EXISTS pedidos (
 id uuid PRIMARY KEY,
 uc_id integer NOT NULL REFERENCES usuario_comun(uc_id),
 creado_en timestamptz NOT NULL DEFAULT now(),
 estado text NOT NULL CHECK (estado IN ('creado','pendiente_pago','error_checkout')),
 total numeric(14,2) NOT NULL CHECK (total > 0),
 moneda text NOT NULL DEFAULT 'ARS',
 items jsonb NOT NULL,
 preferencia_id text UNIQUE
);
CREATE INDEX IF NOT EXISTS pedidos_usuario_fecha ON pedidos(uc_id, creado_en DESC);
CREATE TABLE IF NOT EXISTS admin_auditoria (
 id bigserial PRIMARY KEY,
 ua_id integer NOT NULL REFERENCES usuario_administrativo(ua_id),
 creado_en timestamptz NOT NULL DEFAULT now(),
 entidad text NOT NULL,
 registro_id integer NOT NULL,
 cambios jsonb NOT NULL
);
ALTER TABLE pedidos ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_auditoria ENABLE ROW LEVEL SECURITY;
COMMIT;
