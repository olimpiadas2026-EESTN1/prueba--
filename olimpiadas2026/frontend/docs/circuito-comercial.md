# Circuito comercial y manual

## Compra y pedidos

El carrito ahora registra primero un pedido sin abrir Mercado Pago y conduce a Mis pedidos. Desde allí el comprador revisa cantidades, quita artículos usando cantidad cero, anula con un motivo o inicia el pago. El backend recalcula precios y disponibilidad; no acepta precios del navegador. La modificación requiere la versión observada del pedido para evitar sobrescrituras desde otra pestaña.

La lista `/productos` presenta código, descripción, precio y cupos sin imágenes y permite agregar al carrito. `/ayuda` contiene ayuda al comprador y manual del jefe de ventas. Los formularios del catálogo administrativo permiten crear viajes, paquetes, autos y excursiones. El checkout sigue admitiendo viajes y paquetes: autos y excursiones se administran como componentes y no se compran individualmente en este flujo.

Una vez iniciado el pago, la modificación y la anulación directa se bloquean, incluso si el proveedor da un error incierto. El comprador puede enviar una solicitud a ventas. La respuesta queda vinculada a su cuenta y pedido. Resolver una solicitud NO ejecuta cambios de artículos, reembolsos o anulaciones del checkout. El procedimiento automatizado para cambiar o anular compras que ya iniciaron el pago sigue pendiente; esta limitación debe explicarse en la entrega y contrastarse con el relevamiento.

`/carrito` se conserva por compatibilidad con el flujo anterior. Los pedidos existentes con preferencia, pago o error de checkout quedan marcados como iniciados; no se intenta alterarlos automáticamente.

## Entrega

En Administración, Pedidos permite avanzar de pendiente a en preparación y listo. Registrar entrega se encuentra en Pedidos, entregas y cobros → Pendientes de entrega. Requiere pago confirmado, estado listo, ausencia de anulación y ninguna solicitud pendiente. Registra fecha, administrador, observaciones, importe y artículos en `pedidos_entregados` dentro de la misma transacción que marca completado. Deja de aparecer en pendientes y se consulta en Histórico de entregados. La fila original se conserva para no romper referencias de pagos, comprobantes y auditoría.

El selector genérico ya no permite completar ni reabrir entregados. Los completados anteriores sin registro histórico pueden registrar su entrega para incorporar fecha y responsable reales; no se inventan esos datos en la migración.

Anular es diferente de Eliminar: anular deja fecha y motivo y elimina el saldo pendiente del comprobante interno; Eliminar solo archiva. La anulación directa únicamente admite pedidos sin pago iniciado. Restaurar la papelera no revierte una anulación.

## Cuenta corriente

Cada pedido genera un comprobante en `facturas_internas` con número correlativo, fecha e importe. El backend permite ordenar por fecha o por cliente y mostrar solo saldos pendientes o todos. Un pedido pagado o anulado tiene saldo cero; archivar no borra la deuda. No se generan facturas fiscales, no se admiten pagos parciales ni se automatizan devoluciones. Los importes históricos conservan la moneda ARS del flujo actual.

## Configuración empresarial y correos

Correo del sector de ventas se edita en Administración y se guarda en `configuracion_empresa`, con auditoría. Los nuevos comprobantes y los reintentos que aún no tengan destinatario empresarial usan esa tabla. Cambiar la configuración no redirige mensajes ya preparados con un destinatario. `.env` conserva los parámetros OAuth y secretos de proveedores; el código de envío ya no obtiene el correo empresarial de `.env`.

## Base y endpoints

Aplicar migraciones 001 a 006 antes de usar esta versión. La 006 agrega artículos por pedido, histórico, comprobantes internos, solicitudes y configuración empresarial, además de versión y datos de anulación. Un trigger sincroniza los artículos y el importe interno con la instantánea JSON dentro de la transacción; los pedidos existentes se incorporan sin crear cobros o ventas.

- Comprador: `POST /clientes/pedidos`, `PATCH /clientes/pedidos/{id}`, `POST .../anular`, `POST .../pagar`, `POST .../solicitudes` y `GET /clientes/solicitudes`.
- Ventas: `GET /admin/pendientes-entrega`, `GET /admin/entregados`, `POST /admin/pedidos/{id}/entregar`, `POST .../anular`, `GET /admin/cuenta-corriente?orden=fecha|cliente&solo_pendientes=true|false`.
- Solicitudes: `GET /admin/solicitudes`, `PATCH /admin/solicitudes/{id}`.
- Empresa: `GET` y `PUT /admin/configuracion-empresa`.

Todas las operaciones del comprador filtran por su identidad autenticada. Las de administración requieren sesión interna. Los endpoints de pago no confían en parámetros del retorno del navegador para aprobar un cobro.

## Pruebas y límites

Pruebas unitarias cubren propiedad del pedido, precios del servidor, cantidades agregadas, conflictos de edición, restricciones por pago iniciado, prohibición de entregar sin pago, histórico y protección de rutas. `tests/verificar_circuito_db.py` es una prueba optativa con transacción siempre revertida: comprueba los triggers y operaciones reales de PostgreSQL, sin llamar a Mercado Pago ni Gmail.

Pendiente: prueba visual y funcional completa en la URL final, con una compra de prueba aprobada, webhook firmado y correos recibidos. Las sesiones siguen en memoria y se pierden al reiniciar el backend. No hay reserva de cupos antes del pago. Un pago aprobado sin cupos suficientes requiere revisión administrativa.
