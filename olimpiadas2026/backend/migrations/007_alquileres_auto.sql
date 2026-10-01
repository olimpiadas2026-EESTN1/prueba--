BEGIN;
ALTER TABLE pedido_articulos DROP CONSTRAINT IF EXISTS pedido_articulos_tipo_check;
ALTER TABLE pedido_articulos ADD CONSTRAINT pedido_articulos_tipo_check CHECK (tipo IN ('viaje','paquete','auto'));
ALTER TABLE pedido_articulos ADD COLUMN IF NOT EXISTS fecha_retiro date;
ALTER TABLE pedido_articulos ADD COLUMN IF NOT EXISTS fecha_devolucion date;
ALTER TABLE pedido_articulos ADD CONSTRAINT pedido_articulos_fechas_auto_check CHECK (
 (tipo='auto' AND fecha_retiro IS NOT NULL AND fecha_devolucion IS NOT NULL AND fecha_devolucion>fecha_retiro)
 OR (tipo<>'auto' AND fecha_retiro IS NULL AND fecha_devolucion IS NULL)
);

CREATE TABLE IF NOT EXISTS alquileres_auto (
 pedido_id uuid NOT NULL REFERENCES pedidos(id),
 renglon integer NOT NULL,
 auto_id integer NOT NULL REFERENCES auto(auto_id),
 fecha_retiro date NOT NULL,
 fecha_devolucion date NOT NULL,
 cantidad integer NOT NULL CHECK(cantidad>0),
 precio_diario numeric(14,2) NOT NULL CHECK(precio_diario>0),
 creado_en timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(pedido_id,renglon),
 CHECK(fecha_devolucion>fecha_retiro)
);
CREATE INDEX IF NOT EXISTS alquileres_auto_fechas ON alquileres_auto(auto_id,fecha_retiro,fecha_devolucion);

CREATE OR REPLACE FUNCTION sincronizar_detalle_pedido() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 DELETE FROM pedido_articulos WHERE pedido_id=NEW.id;
 INSERT INTO pedido_articulos(pedido_id,renglon,tipo,producto_id,descripcion,cantidad,precio_unitario,fecha_retiro,fecha_devolucion)
 SELECT NEW.id,n::integer,item->>'tipo',(item->>'id')::integer,item->>'title',(item->>'quantity')::integer,(item->>'unit_price')::numeric,
        NULLIF(item->>'fecha_retiro','')::date,NULLIF(item->>'fecha_devolucion','')::date
 FROM jsonb_array_elements(NEW.items) WITH ORDINALITY AS x(item,n);
 INSERT INTO facturas_internas(pedido_id,emitida_en,importe) VALUES(NEW.id,NEW.creado_en,NEW.total)
 ON CONFLICT(pedido_id) DO UPDATE SET importe=EXCLUDED.importe;
 RETURN NEW;
END; $$;

ALTER TABLE alquileres_auto ENABLE ROW LEVEL SECURITY;
COMMIT;