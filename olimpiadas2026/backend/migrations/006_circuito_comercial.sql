BEGIN;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS anulado_en timestamptz;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS motivo_anulacion text;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS checkout_iniciado boolean NOT NULL DEFAULT false;
UPDATE pedidos SET checkout_iniciado=true WHERE preferencia_id IS NOT NULL OR estado IN ('pendiente_pago','confirmado','error_checkout');
CREATE TABLE IF NOT EXISTS pedido_articulos (
 pedido_id uuid NOT NULL REFERENCES pedidos(id),
 renglon integer NOT NULL,
 tipo text NOT NULL CHECK(tipo IN ('viaje','paquete')),
 producto_id integer NOT NULL,
 descripcion text NOT NULL,
 cantidad integer NOT NULL CHECK(cantidad>0),
 precio_unitario numeric(14,2) NOT NULL CHECK(precio_unitario>0),
 PRIMARY KEY(pedido_id,renglon)
);
CREATE TABLE IF NOT EXISTS pedidos_entregados (
 pedido_id uuid PRIMARY KEY REFERENCES pedidos(id),
 uc_id integer NOT NULL REFERENCES usuario_comun(uc_id),
 entregado_en timestamptz NOT NULL DEFAULT now(),
 ua_id integer REFERENCES usuario_administrativo(ua_id),
 observaciones text NOT NULL,
 total numeric(14,2) NOT NULL,
 articulos jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS facturas_internas (
 numero bigserial PRIMARY KEY,
 pedido_id uuid NOT NULL UNIQUE REFERENCES pedidos(id),
 emitida_en timestamptz NOT NULL DEFAULT now(),
 importe numeric(14,2) NOT NULL CHECK(importe>0)
);
CREATE TABLE IF NOT EXISTS configuracion_empresa (
 id integer PRIMARY KEY CHECK(id=1),
 correo_ventas text NOT NULL,
 actualizado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS solicitudes_pedido (
 id bigserial PRIMARY KEY,
 pedido_id uuid NOT NULL REFERENCES pedidos(id),
 uc_id integer NOT NULL REFERENCES usuario_comun(uc_id),
 tipo text NOT NULL CHECK(tipo IN ('modificacion','anulacion')),
 detalle text NOT NULL,
 estado text NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','resuelta','rechazada')),
 creado_en timestamptz NOT NULL DEFAULT now(),
 resuelto_en timestamptz,
 ua_id integer REFERENCES usuario_administrativo(ua_id),
 respuesta text
);
CREATE UNIQUE INDEX IF NOT EXISTS solicitud_pendiente_unica ON solicitudes_pedido(pedido_id) WHERE estado='pendiente';
CREATE OR REPLACE FUNCTION sincronizar_detalle_pedido() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 DELETE FROM pedido_articulos WHERE pedido_id=NEW.id;
 INSERT INTO pedido_articulos(pedido_id,renglon,tipo,producto_id,descripcion,cantidad,precio_unitario)
 SELECT NEW.id,n::integer,item->>'tipo',(item->>'id')::integer,item->>'title',(item->>'quantity')::integer,(item->>'unit_price')::numeric
 FROM jsonb_array_elements(NEW.items) WITH ORDINALITY AS x(item,n);
 INSERT INTO facturas_internas(pedido_id,emitida_en,importe) VALUES(NEW.id,NEW.creado_en,NEW.total)
 ON CONFLICT(pedido_id) DO UPDATE SET importe=EXCLUDED.importe;
 RETURN NEW;
END; $$;
DROP TRIGGER IF EXISTS pedidos_detalle ON pedidos;
CREATE TRIGGER pedidos_detalle AFTER INSERT OR UPDATE OF items,total ON pedidos FOR EACH ROW EXECUTE FUNCTION sincronizar_detalle_pedido();
INSERT INTO pedido_articulos(pedido_id,renglon,tipo,producto_id,descripcion,cantidad,precio_unitario)
 SELECT p.id,n::integer,item->>'tipo',(item->>'id')::integer,item->>'title',(item->>'quantity')::integer,(item->>'unit_price')::numeric
 FROM pedidos p CROSS JOIN LATERAL jsonb_array_elements(p.items) WITH ORDINALITY AS x(item,n)
 ON CONFLICT DO NOTHING;
INSERT INTO facturas_internas(pedido_id,emitida_en,importe) SELECT id,creado_en,total FROM pedidos ON CONFLICT DO NOTHING;
-- Se preservan los completados anteriores; no se inventa fecha ni responsable de entrega.
ALTER TABLE pedido_articulos ENABLE ROW LEVEL SECURITY;
ALTER TABLE pedidos_entregados ENABLE ROW LEVEL SECURITY;
ALTER TABLE facturas_internas ENABLE ROW LEVEL SECURITY;
ALTER TABLE configuracion_empresa ENABLE ROW LEVEL SECURITY;
ALTER TABLE solicitudes_pedido ENABLE ROW LEVEL SECURITY;
COMMIT;
