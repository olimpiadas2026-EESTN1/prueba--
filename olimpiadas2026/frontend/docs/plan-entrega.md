# Plan de entrega: 2 de octubre de 2026

Fecha límite informada por Santiago: 02/10. Hora límite pendiente de confirmar. La consigna y la rúbrica entregadas mantienen 2025 en el nombre, pero Santiago confirmó que son las vigentes para esta edición.

Este cronograma es una propuesta de trabajo desde el 30/09, no un registro inventado de actividades pasadas. No se envió a los integrantes; deben acordarlo como equipo.

## Equipo y criterio de distribución

| Integrante | Rol informado | Trabajo propuesto hasta la entrega | Criterio |
| --- | --- | --- | --- |
| Santiago López | Programador | Integración frontend, recorridos de comprador y jefe de ventas, correcciones y demostración | Continuidad con el desarrollo y pruebas locales actuales |
| Gadiel Yanelli | Programador | Backend, despliegue, Mercado Pago, webhook y configuración OAuth con el titular de las cuentas | Separar las integraciones externas de las correcciones de interfaz |
| Felipe Prida | Documentación y diagramas | DER actualizado, casos de uso, composición del PDF y anexos | Responsabilidad informada en diagramas y documentación |
| Juan Juárez | Analista y documentación | Validar reglas de negocio, relevamiento, matriz de cumplimiento, manual y guion de pruebas | Responsabilidad informada en análisis y documentación |

## Gantt propuesto

| Trabajo | Inicio | Duración (días calendario) | Responsable principal | Dependencia | 30/09 | 01/10 | 02/10 |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| Acordar alcance y reglas de modificación/anulación | 30/09 | 2 | Juan | Consigna | X | X | |
| Completar y probar pedidos, entregas y cuenta corriente | 30/09 | 2 | Santiago | Reglas de negocio | X | X | |
| Configurar y probar Mercado Pago y Gmail | 30/09 | 2 | Gadiel | Acceso a cuentas, URL pública | X | X | |
| DER y casos de uso contra la versión final | 01/10 | 1 | Felipe | Modelo 006 y revisión de Juan | | X | |
| Relevamiento, manual y matriz de evidencias | 01/10 | 1 | Juan | Recorrido funcional | | X | |
| Publicación y prueba completa con ambos perfiles | 01/10 | 2 | Gadiel y Santiago | Integraciones configuradas | | X | X |
| Capturas y video con la versión publicada | 02/10 | 1 | Santiago y Juan | Prueba completa aprobada | | | X |
| PDF, índice, referencias y anexos | 01/10 | 2 | Felipe | Aportes de todo el equipo | | X | X |
| Revisión de entrega, permisos de enlaces y respaldo | 02/10 | 1 | Los cuatro | PDF y URL final | | | X |

Los días se superponen porque se propone trabajar en paralelo. No expresan jornadas completas por tarea ni sustituyen el registro real del trabajo. Completar horas y avances con lo que efectivamente haga el equipo.

## Prioridades y criterio para detener mejoras

1. Corregir errores que impidan comprar, administrar o demostrar requisitos explícitos.
2. Cerrar pagos y comprobantes con una compra de prueba aprobada. No marcar pedidos reales como pagados para obtener capturas.
3. Completar evidencias y documentación de lo efectivamente probado.
4. El 02/10 evitar rediseños y funciones nuevas; corregir únicamente bloqueos de entrega.

## Bloqueos externos comprobados

En la revisión local faltan los archivos OAuth de Gmail (`google-oauth-client.json` y `gmail-token.json`), `MERCADOPAGO_WEBHOOK_URL` y `MERCADOPAGO_WEBHOOK_SECRET`. No compartir secretos por documentación ni versionarlos. El destinatario empresarial sí quedó configurado en la tabla `configuracion_empresa` a partir del valor local existente.

Pendientes del equipo: URL definitiva del frontend/backend, acceso del comprador de prueba de Mercado Pago, datos escolares y del docente, identificación del equipo, relevamiento, hora de cierre, enlace al video y evidencias reales. Los correos no se enviaron ni se aprobaron pagos durante el desarrollo.

## Entregable final

Un PDF con carátula, índice, distribución de tareas y criterio, Gantt, relevamiento, casos de uso, DER, referencia al código cliente/servidor, credencial interna de evaluación, URL publicada, capturas, enlace al video, manual y ayudas, referencias y anexos. Agregar registro de experiencia grupal de máximo una carilla. Formato: Arial 12, interlineado sencillo, encabezado con título, pie con página y total. El archivo lleva la identificación del equipo indicada en la consigna.

No incluir tokens de Mercado Pago, secretos de webhook, contraseñas de base de datos ni archivos OAuth. La credencial de evaluación debe ser una cuenta destinada a ese uso, comprobada por el equipo.
