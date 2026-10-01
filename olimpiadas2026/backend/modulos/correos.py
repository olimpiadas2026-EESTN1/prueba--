"""Entrega por Gmail API del comprobante persistido, al correo de la cuenta compradora."""
from modulos.circuito import correo_empresa
from modulos.gmail_api import send_email
from psycopg.rows import dict_row
from modulos.gestion import connection


def compose(order, name, payment_id, live_mode):
    test = '' if live_mode else '[PRUEBA] '
    subject = f'{test}Compra confirmada — AirTrip — pedido {order["id"]}'
    lines = [f'Hola {name},', '', 'Tu compra fue confirmada.', f'Pedido: {order["id"]}', f'Pago de Mercado Pago: {payment_id}', '']
    if not live_mode: lines += ['Esta es una compra de prueba, sin validez como reserva real.', '']
    for item in order['items']:
        lines.append(f'{item["title"]} — {item["quantity"]} x ARS {item["unit_price"]:.2f}')
    lines += ['', f'Total: ARS {order["total"]}', '', 'Gracias por elegir AirTrip.', 'Este comprobante no reemplaza una factura fiscal.']
    return subject, '\n'.join(lines)


def deliver_one(order_id, tipo):
    # Lock impide envíos simultáneos por notificaciones repetidas.
    # La API no ofrece exactly-once: una caída tras aceptar el mensaje puede duplicar un reintento.
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT * FROM correos_compra WHERE pedido_id=%s AND tipo=%s FOR UPDATE', (order_id,tipo))
            mail = cur.fetchone()
            if not mail: return 'sin_comprobante'
            if mail['estado'] == 'enviado': return 'enviado'
            try:
                recipient=mail['destinatario']
                if not recipient and tipo=='administrador':
                    recipient=correo_empresa(cur)
                if not recipient or '@' not in recipient or any(c in recipient for c in '\r\n'):
                    raise RuntimeError('Destinatario no configurado')
                send_email(recipient,mail['asunto'],mail['cuerpo'],f'<pedido-{order_id}-{tipo}@airtrip.local>')
                cur.execute("UPDATE correos_compra SET estado='enviado',intentos=intentos+1,enviado_en=now(),ultimo_error=NULL,destinatario=%s WHERE pedido_id=%s AND tipo=%s",(recipient,order_id,tipo))
                return 'enviado'
            except Exception as error:
                # No persistir respuestas del proveedor que puedan contener credenciales o destinatarios.
                cur.execute("UPDATE correos_compra SET estado='error',intentos=intentos+1,ultimo_error=%s WHERE pedido_id=%s AND tipo=%s",(type(error).__name__,order_id,tipo))
                return 'error'


def deliver(order_id):
    return {tipo: deliver_one(order_id,tipo) for tipo in ('comprador','administrador')}


def compose_admin(order, user, payment_id, live_mode):
    _, receipt=compose(order,user['nombre'],payment_id,live_mode)
    subject=f"{'' if live_mode else '[PRUEBA] '}Nueva venta — AirTrip — pedido {order['id']}"
    body=f"Aviso para administración\nCliente: {user['nombre']}\nCorreo registrado: {user['correo_electronico']}\n\n{receipt}"
    return subject,body
