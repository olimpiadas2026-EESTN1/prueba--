# Consulta y gestión de pedidos

El comprador accede a **Mis pedidos** desde la navegación principal (`/mis-pedidos`). Debe iniciar sesión como comprador. La pantalla muestra fecha, productos, cantidades, importe, estado del pago y estado de gestión. El botón Actualizar pedidos vuelve a consultar la base; no hay actualización en tiempo real. La API limita la consulta a los 200 pedidos más recientes de la cuenta autenticada, sin aceptar un identificador de usuario del navegador.

El administrador entra a Administración → Pedidos → Editar. Puede consultar el historial y guardar un nuevo estado con un motivo obligatorio (hasta 500 caracteres). El historial registra administrador, fecha, estado anterior y nuevo. Los motivos son internos y no aparecen en la pantalla del comprador. Los cambios no envían correos adicionales.

## Estados independientes

`estado` representa el flujo de pago existente: creado, pendiente_pago, error_checkout y confirmado. Confirmado sigue dependiendo de la verificación del pago con Mercado Pago; el formulario administrativo no lo modifica.

`estado_gestion` representa el trabajo de la empresa:

| Estado actual | Destinos permitidos |
| --- | --- |
| pendiente | en_preparacion, en_revision |
| en_preparacion | listo, en_revision |
| listo | completado, en_revision |
| completado | en_revision |
| en_revision | pendiente, en_preparacion, listo |

En preparación, listo y completado requieren pago confirmado. Un pedido sin pago puede pasar a revisión o volver de revisión a pendiente. Listo indica que la empresa terminó de preparar la reserva; completado indica que terminó la gestión. No implica automáticamente que haya transcurrido el viaje.

El cambio bloquea la fila dentro de una transacción y comprueba el estado que vio el administrador. Si otra persona ya lo cambió, devuelve 409 y pide actualizar. La escritura del estado y del historial es atómica. Esta función no cobra, devuelve dinero, cancela preferencias de Mercado Pago, modifica ventas ni altera cupos. Cancelaciones y devoluciones requieren un flujo específico y no están implementadas aquí.

## Backend y base

- `GET /clientes/mis-pedidos`: requiere sesión de comprador, filtra por su `uc_id`.
- `PATCH /admin/pedidos/{uuid}/estado`: requiere sesión administrativa; cuerpo con `estado`, `estado_esperado` y `motivo`.
- `GET /admin/pedidos/{uuid}/historial`: requiere sesión administrativa.
- Migración `backend/migrations/004_estados_pedidos.sql`: agrega `estado_gestion` (pendiente por defecto para pedidos existentes) y `pedido_estados`, con RLS habilitado. Aplicada a la base compartida durante esta implementación. En otra base, aplicarla después de las migraciones anteriores antes de arrancar esta versión.

## Comprobación

Pasaron 21 pruebas unitarias del backend y `npm run build`. Las nuevas pruebas cubren protección administrativa, aislamiento de la consulta del comprador, prohibición de preparar sin pago, transiciones inválidas, conflicto entre administradores y registro del cambio. No se modificaron estados de pedidos reales para probar.

Prueba manual pendiente: entrar como comprador, abrir Mis pedidos; entrar como administrador y pasar un pedido pendiente a en revisión con un motivo; actualizar la pantalla del comprador y comprobar el cambio. Para probar el avance de preparación a completado, usar un pedido con pago de prueba verificado. Si se reinició el backend, iniciar sesión nuevamente: las sesiones actuales se almacenan en memoria.

## Actualización: circuito comercial

La migración 006 y [Circuito comercial](circuito-comercial.md) sustituyen el paso manual de listo a completado: ahora se usa Registrar entrega, que crea el histórico. No se reabre un completado desde el selector. Anulación y archivo son operaciones distintas. Consultar la matriz de cumplimiento para las limitaciones pendientes.
