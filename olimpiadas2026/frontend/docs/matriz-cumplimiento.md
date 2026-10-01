# Matriz de cumplimiento de la consigna vigente

Fuente: ONETP_2025_Programacion_Estudiantes.pdf, páginas 4–8, y Rúbrica PROGRAMACION 2025.xlsx, hoja Programación. Santiago confirmó que ambas corresponden a la edición actual pese al año de los nombres. Revisión del 30/09/2026; entrega 02/10/2026.

Implementado significa código disponible, no aprobación de la evaluación. Verificado indica evidencia concreta de prueba. Pendiente y parcial no deben presentarse como completos en el video ni en el informe.

| Referencia | Requisito | Situación | Evidencia y pendiente |
| --- | --- | --- | --- |
| 1.1, 2.1 | Alta y autenticación de comprador | Implementado | Sesión separada de administración. Pruebas de permisos; sesión persistente entre reinicios pendiente. |
| 1.3.1 | Lista de productos sin imágenes | Implementado | Ruta /productos con viajes y paquetes; revisión visual publicada pendiente. |
| 1.3.2 | Carrito | Implementado | Categorías y lista agregan artículos. Registro conduce a Mis pedidos. |
| 1.3.3 | Pedido pendiente de entrega | Implementado | Pedido creado antes del pago; listas separadas de pendientes/entregados/anulados. |
| 1.3.4 | Consultar, modificar y eliminar pendientes | Parcial | Edición de cantidades y anulación antes del checkout. Después hay solicitudes; cambios/reembolsos tras iniciar pago no automatizados. |
| 1.4.1–2 | Alta y consulta de productos | Implementado | Altas de viajes, paquetes y autos; código generado en backend. Autos como componentes, no compra independiente. |
| 1.4.3 | Estado de pedidos pendientes | Implementado | Panel con pago y gestión separados; lista Pendientes de entrega. |
| 1.4.4 | Entrega | Implementado | Operación transaccional, requiere pago confirmado y estado listo; histórico persistido. |
| 1.4.5 | Facturas a cobrar por fecha y cliente | Parcial | Comprobantes internos y saldos con ambos órdenes. Sin facturación fiscal ni pagos parciales. Confirmar esta interpretación con docente/relevamiento. |
| 1.4.6 | Anulación administrativa | Parcial | Directa antes de checkout. Para pagos iniciados falta conciliar/cancelar/reembolsar con proveedor; papelera no sustituye anulación. |
| 2.2 | Número de pedido en todos los artículos | Implementado | pedido_articulos con FK pedido_id y renglon, sincronizado transaccionalmente. |
| 2.3 | Relación pedido-cliente | Implementado | FK uc_id y permisos que filtran por cuenta. |
| 2.4 | Histórico de entregados | Implementado | pedidos_entregados y consulta separada; conserva cabecera para referencias y excluye de pendientes. |
| 2.5 | Total y cobro por tercero | Parcial | Total calculado por servidor y SDK Mercado Pago. Prueba de checkout aprobado y webhook real pendiente. |
| 2.6 | Registrar ventas | Implementado, integración real pendiente | Pago verificado registra ventas y relaciones; no confiar en retorno del navegador. |
| Nota p.4–5 | Correo al comprador y sector empresarial | Parcial | Mensajes independientes preparados tras pago, Gmail API. Faltan OAuth y prueba de entrega. |
| Nota p.4–5 | Correo del sector en tabla | Implementado | configuracion_empresa, edición administrativa auditada; migración conserva correo previamente configurado. |
| Entregables 1–2 | Distribución de tareas y Gantt | Borrador | plan-entrega.md con roles aportados y fechas propuestas. Validar y registrar tiempos reales. |
| Entregable 3 | Relevamiento coloquial | Pendiente | Juan: aportar entrevista o relevamiento; no inventar respuestas del cliente. |
| Entregables 4–5 | Casos de uso y DER | Pendiente de consolidación | Felipe: diagramar con migraciones 001–006; incluir solicitudes, entregas, configuración y cuenta corriente. |
| Entregable 6 | Código fuente documentado | Parcial | Código y documentación locales; revisar normas, versiones, repositorio y paquete de entrega. |
| Entregables 7–8 | Credencial interna y URL | Pendiente de validación | Cuenta existente; preparar acceso de evaluación y comprobar la versión publicada. |
| Entregables 9–10 | Capturas y video | Pendiente | Producir sobre la versión funcional, con ambos actores y enlaces accesibles. |
| Entregable 11 | Ayudas y manual | Borrador implementado | /ayuda y circuito-comercial.md. Verificar con un usuario y llevar al PDF. |
| Páginas 6–8 | PDF, carátula, anexos, referencias, reflexión grupal | Pendiente | Faltan datos escolares/docente, CUE, identificador de equipo y experiencia real. |

## Orden de pruebas de aceptación

1. Registrar comprador y comprobar que no accede a rutas de administración ni pedidos de otra cuenta.
2. Agregar viaje y paquete desde lista sin imágenes, registrar pedido y comprobar artículos y total en base.
3. Modificar cantidades antes de pagar y anular otro pedido; verificar saldo y lista de pendientes.
4. Iniciar checkout con comprador de prueba distinto del vendedor; obtener pago aprobado y confirmación verificable.
5. Verificar una sola venta por artículo, descuento de cupos y dos comprobantes. Repetir webhook no debe duplicar ventas.
6. Preparar el pedido, marcar listo y registrar entrega; comprobar histórico y exclusión de pendientes.
7. Consultar cuenta corriente por fecha y por cliente, pendientes y todos; archivar no elimina deuda.
8. Enviar solicitud desde comprador y responder desde ventas; comprobar la respuesta solo en la cuenta correspondiente.
9. Eliminar/restaurar producto y cuenta de prueba; verificar catálogo y bloqueo de acceso.
10. Ejecutar el recorrido en la URL final y generar capturas/video sin secretos ni datos de personas ajenas a las pruebas.

## Bloqueos para declarar el circuito completo

No hay archivo OAuth de cliente ni token autorizado local de Gmail. No están configurados URL ni secreto del webhook. Sigue pendiente reproducir el bloqueo original del botón de pago de Mercado Pago. Estas tareas requieren configuración de cuentas y URL pública, y una compra de prueba real; las pruebas con SDK simulado no las reemplazan.
