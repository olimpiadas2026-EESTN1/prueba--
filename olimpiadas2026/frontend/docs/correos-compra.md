# Comprobantes mediante Gmail API oficial

## Envío

Se reemplazó FastAPI-Mail/SMTP por las bibliotecas oficiales de Google y `gmail.users.messages.send`. Cada compra confirmada genera dos mensajes independientes:

- Comprador: correo registrado de su cuenta, identificado desde el pedido en la base.
- Empresa: `ADMIN_NOTIFICATION_EMAIL`, con datos del comprador, productos y total.

El mensaje MIME se codifica en base64url. Solo se solicita el permiso OAuth `https://www.googleapis.com/auth/gmail.send`, sin permisos de lectura del buzón. El remitente debe ser la cuenta autorizada o un alias permitido por Gmail. Las credenciales de comprador/administrador del sitio no son credenciales de Google.

## Configuración inicial

1. Crear o seleccionar un proyecto en Google Cloud y habilitar **Gmail API**.
2. Configurar la pantalla de consentimiento OAuth; durante las pruebas, agregar la cuenta remitente como usuario de prueba.
3. Crear un cliente OAuth de tipo **Aplicación de escritorio** para autorizar desde tu computadora.
4. Descargar su JSON y guardarlo en `prueba--/.secrets/google-oauth-client.json`.
5. Revisar las variables del `.env`:

```dotenv
GMAIL_FROM=Lopezbacha07@gmail.com
GMAIL_CLIENT_SECRET_FILE=.secrets/google-oauth-client.json
GMAIL_TOKEN_FILE=.secrets/gmail-token.json
ADMIN_NOTIFICATION_EMAIL=Lopezbacha07@gmail.com
```

6. Desde `backend`, instalar dependencias y autorizar:

```sh
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python autorizar_gmail.py
```

El comando abre Google para iniciar sesión con la cuenta remitente y aprobar el envío. Guarda el token OAuth con permisos restringidos. **No envía correos**. Reiniciar el backend al terminar. No compartir el JSON ni los tokens: `.secrets/` está excluido de Git. No se usan contraseñas habituales ni contraseñas de aplicación de Gmail, ni campos `MAIL_*` de SMTP.

El refresco del acceso es automático mientras la autorización siga vigente. Si Google revoca o vence la autorización, repetir el comando. El modo de pruebas OAuth puede requerir reautorizar; antes de producción revisar requisitos de publicación/verificación y cuotas de Google. Las bibliotecas instaladas funcionan en el entorno actual, pero Google advierte que Python 3.9 está fuera de soporte: migrar el entorno a una versión vigente antes de producción.

## Confirmación de pagos

Se mantiene el flujo implementado: webhook firmado de Mercado Pago, consulta del pago al proveedor, validación de estado aprobado/total/moneda/vendedor/referencia, transacción que registra ventas y descuenta cupos, y persistencia de los dos comprobantes. El correo no se envía al abrir el checkout ni por confiar en parámetros de retorno del navegador.

Para el webhook siguen siendo necesarios `MERCADOPAGO_WEBHOOK_SECRET` y `MERCADOPAGO_WEBHOOK_URL` (HTTPS público). `localhost` no es accesible desde Mercado Pago. Las migraciones `001_gestion.sql`, `002_comprobantes.sql` y `003_correo_administrador.sql` ya fueron aplicadas a la base compartida; esta sustitución del transporte no modifica esos datos.

Administración permite verificar un pago en Pedidos y consultar/reintentar mensajes en Correos de compra. También existe `reintentar_correos.py`: ejecutarlo **sí envía** los comprobantes confirmados pendientes, usando la cuenta autorizada.

## Reintentos y límites

Se conservan destinatario, tipo, estado e intentos por pedido. Un envío ya marcado como enviado no se repite. No hay garantía absoluta de exactamente una entrega: si Gmail acepta y el proceso falla antes de guardar el estado, un reintento puede duplicar el mensaje. No se habilitan reintentos automáticos de la petición de envío HTTP; los reintentos se gestionan mediante la cola persistida.

Si falta OAuth o Google rechaza el envío, queda registrado como error para reintentar, sin revertir la venta confirmada. Una respuesta de aceptación no prueba lectura ni llegada a la bandeja principal. Compras de prueba llevan `[PRUEBA]`. No se envían contraseñas ni tokens en el comprobante. Si faltan cupos al confirmar, se requiere intervención administrativa; devoluciones y contracargos no están automatizados.

## Validación

Pruebas con Gmail API simulada verifican destinatario, remitente, MIME/base64url, permiso de envío, ausencia de autorización y reintentos independientes. No se realizó OAuth ni se enviaron correos reales durante la implementación. La aceptación final requiere autorizar la cuenta y probar una compra de prueba.

## Documentación oficial

## Diagnóstico del checkout de prueba (30/09/2026)

La consulta de solo lectura a Mercado Pago confirmó que la credencial local es válida, corresponde a una cuenta de prueba argentina y tiene habilitada la venta. La última preferencia registrada existe, no tiene vencimiento activado ni tipos de pago excluidos efectivos. Los seis pedidos consultados siguen en `pendiente_pago`; esto no demuestra por sí solo que el proveedor haya rechazado los pagos.

Para probar, abrir la tienda en una ventana de incógnito e ingresar en el checkout con un **comprador de prueba distinto del vendedor**, del mismo país. El saldo debe corresponder a ese comprador de prueba. Usar el `init_point` devuelto por la preferencia. No mezclar cuentas habituales con esta credencial de prueba. Si el botón sigue bloqueado, registrar el texto exacto y si aparece en nuestra tienda o en Mercado Pago antes de atribuirlo al correo.

En la configuración local revisada faltan `MERCADOPAGO_WEBHOOK_URL` y `MERCADOPAGO_WEBHOOK_SECRET`. Para la confirmación automática, publicar el endpoint `/webhooks/mercadopago` mediante HTTPS, configurar las notificaciones de pagos en la aplicación de Mercado Pago y guardar su secreto de firma en el backend. Reiniciar el backend y generar un checkout nuevo. No inventar el secreto ni marcar pedidos como pagados para probar los correos. Como alternativa de diagnóstico, un administrador puede verificar el identificador de un pago realmente aprobado desde Pedidos.

Crear el checkout no invoca Gmail. Los correos se procesan después de verificar el pago. Las 16 pruebas automatizadas existentes pasan con servicios externos simulados; no sustituyen una compra completa en Mercado Pago. El bloqueo del botón y el mensaje reportado siguen pendientes de reproducir con la cuenta compradora y el texto exacto del error.

- [Pruebas oficiales de Checkout Pro](https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-preferences/integration-test/test-purchases).

## Referencias de Gmail

- [Gmail API](https://developers.google.com/workspace/gmail/api/reference/rest?hl=es-419).
- [Inicio rápido Python y configuración OAuth](https://developers.google.com/workspace/gmail/api/quickstart/python).
- [Crear y enviar mensajes](https://developers.google.com/workspace/gmail/api/guides/sending).

## Actualización: destinatario empresarial en base

Desde la migración 006, el destinatario del sector se guarda en `configuracion_empresa` y se edita en Administración → Pedidos, entregas y cobros → Correo del sector de ventas. El valor local anterior se conservó en la tabla durante la migración. `ADMIN_NOTIFICATION_EMAIL` ya no se consulta al preparar/enviar comprobantes; los secretos OAuth siguen fuera de la base y del repositorio.
