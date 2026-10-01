# Eliminación y restauración administrativa

En Usuarios, Pedidos, Ventas, Vuelos y micros, Paquetes, Autos y Excursiones, cada fila tiene **Eliminar**. El formulario muestra el registro, explica el efecto y solicita un motivo. Confirmar envía el registro a la papelera. Activar **Ver papelera** permite consultar los eliminados y **Restaurar** los devuelve a la lista activa. Ambas acciones requieren sesión administrativa, confirmación y un motivo de hasta 500 caracteres.

Es una baja lógica (`eliminado_en`), no un borrado definitivo de la base. Las relaciones entre usuarios, pedidos, ventas y productos permanecen intactas. No hay eliminación en cascada. Auditoría y comprobantes se conservan; no tienen botón de borrado. La cuenta administrativa que ejecuta la operación tampoco forma parte de Usuarios, que lista compradores.

## Efectos

- **Usuarios:** se bloquea el login y se invalidan sus sesiones locales. Cada petición autenticada comprueba además en la base que la cuenta esté activa. Al restaurar, el comprador puede volver a iniciar sesión. Se conserva el correo registrado; restaurar no crea otra cuenta.
- **Catálogo:** los productos dejan de aparecer en las consultas públicas y el checkout rechaza viajes o paquetes dados de baja, aunque estuvieran en un carrito guardado. Los componentes eliminados dejan de aparecer en consultas de relaciones. Las reservas y ventas existentes no pierden sus referencias.
- **Pedidos:** desaparecen de las listas activas del administrador y del comprador. Se conserva la preferencia y el pago. Una preferencia ya abierta puede seguir pagándose: archivar no la cancela y el webhook continúa verificando el pago. Para anular un cobro o una preferencia se requiere gestionar esa operación con Mercado Pago.
- **Ventas:** desaparecen de la lista activa, pero permanecen en el total histórico del resumen. La baja no es un reembolso ni repone cupos.
- **Ficha de usuario:** conserva el historial completo de pedidos y ventas, incluidos los eliminados, identificados por `eliminado_en`.
- **Restauración:** afecta únicamente al registro seleccionado, no restaura automáticamente registros relacionados. No envía correos, repone cupos ni cambia estados de pago o gestión.

Cada acción guarda administrador, entidad, identificador, acción y motivo en Cambios. El bloqueo de fila evita que dos administradores eliminen o restauren simultáneamente el mismo registro; la segunda petición recibe 409. El estado y la auditoría se guardan en una misma transacción. Los registros de la papelera deben restaurarse antes de editarlos.

## API y migración

- `DELETE /admin/datos/{entidad}/{id}` con `{"motivo":"..."}`.
- `POST /admin/datos/{entidad}/{id}/restaurar` con el mismo cuerpo.
- Las listas administrativas admiten `?eliminados=true` (solo papelera); por defecto muestran solo activos.
- Entidades admitidas: `usuarios`, `pedidos`, `ventas`, `viajes`, `paquetes`, `autos`, `excursiones`. Pedidos usa UUID; las demás, un entero positivo.
- Los endpoints antiguos `/eliminar` y `/ventas/eliminarTVS` delegan en la misma baja lógica con un motivo de compatibilidad; dejan de hacer borrados físicos.
- Aplicar `backend/migrations/005_papelera.sql` después de las migraciones anteriores, antes de iniciar esta versión. Añade `eliminado_en` y convierte `admin_auditoria.registro_id` a texto para admitir UUID. No elimina registros ni cambia estados de pago.

## Validación

Pruebas automatizadas cubren las siete entidades, restauración, auditoría, validación, conflictos, registros inexistentes, protección administrativa, revocación de sesiones y rechazo del checkout de productos eliminados. Se verifica también la compilación del frontend. Las pruebas de borrado usan dobles de base de datos; no eliminan registros de clientes reales.

Prueba manual: crear un producto de demostración, eliminarlo con un motivo, comprobar su ausencia en el catálogo público, restaurarlo desde Ver papelera y consultar las dos entradas en Cambios. Para verificar usuarios, usar una cuenta de prueba. No utilizar un pago real para comprobar la papelera.
