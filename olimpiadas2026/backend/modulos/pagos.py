"""Confirma el pago desde la API del proveedor y genera un solo comprobante por pedido."""
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException
from psycopg import sql
from psycopg.rows import dict_row
from modulos.gestion import connection
from modulos.circuito import correo_empresa
from modulos.correos import compose, compose_admin


def validate_payment(payment, order, preference):
    if payment.get('status') != 'approved': return False
    if (str(payment.get('external_reference')) != str(order['id']) or
        payment.get('currency_id') != order['moneda'] or
        Decimal(str(payment.get('transaction_amount',0))) != Decimal(str(order['total'])) or
        not payment.get('collector_id') or
        str(payment['collector_id']) != str(preference.get('collector_id')) or
        str(preference.get('external_reference')) != str(order['id']) or
        Decimal(str(payment.get('transaction_amount_refunded',0))) != 0):
        raise HTTPException(409,'El pago no coincide con el pedido')
    return True


def process_payment(payment_id,sdk):
    if sdk is None: raise HTTPException(503,'Mercado Pago no configurado')
    response=sdk.payment().get(str(payment_id))
    if response.get('status') != 200: raise HTTPException(502,'No se pudo consultar el pago')
    payment=response['response']
    if str(payment.get('id')) != str(payment_id): raise HTTPException(409,'Pago inconsistente')
    try: order_id=str(UUID(str(payment.get('external_reference'))))
    except ValueError: return None
    if payment.get('status') != 'approved': return None
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT * FROM pedidos WHERE id=%s FOR UPDATE',(order_id,))
            order=cur.fetchone()
            if not order: return None
            if order.get('anulado_en'): raise HTTPException(409,'Pago de un pedido anulado: requiere revisión administrativa')
            if order['pago_id']:
                if order['pago_id'] != str(payment_id): raise HTTPException(409,'El pedido ya tiene otro pago')
                return order_id
            if not order['preferencia_id']: raise HTTPException(409,'El pedido aún no tiene preferencia')
            pref=sdk.preference().get(order['preferencia_id'])
            if pref.get('status') != 200: raise HTTPException(502,'No se pudo validar la preferencia')
            validate_payment(payment,order,pref['response'])
            # Conserva compatibilidad con IDs manuales del esquema original.
            cur.execute('LOCK TABLE ventas IN SHARE ROW EXCLUSIVE MODE')
            cur.execute('SELECT COALESCE(MAX(vtas_id),0)+1 AS id FROM ventas')
            sale_id=cur.fetchone()['id']
            for renglon,item in enumerate(sorted(order['items'],key=lambda i:(i['tipo'],i['id'],i.get('fecha_retiro',''),i.get('fecha_devolucion',''))),start=1):
                if item['tipo']=='auto':
                    cur.execute('SELECT disponibles FROM auto WHERE auto_id=%s AND eliminado_en IS NULL FOR UPDATE',(item['id'],))
                    auto=cur.fetchone()
                    if not auto: raise HTTPException(409,'El auto ya no está disponible: requiere revisión administrativa')
                    cur.execute('SELECT COALESCE(SUM(cantidad),0) AS reservados FROM alquileres_auto WHERE auto_id=%s AND fecha_retiro<%s AND fecha_devolucion>%s',(item['id'],item['fecha_devolucion'],item['fecha_retiro']))
                    if cur.fetchone()['reservados']+item['quantity']>auto['disponibles']:
                        raise HTTPException(409,'El auto ya no tiene disponibilidad para esas fechas: requiere revisión administrativa')
                    cur.execute('INSERT INTO alquileres_auto(pedido_id,renglon,auto_id,fecha_retiro,fecha_devolucion,cantidad,precio_diario) VALUES(%s,%s,%s,%s,%s,%s,%s)',(order_id,renglon,item['id'],item['fecha_retiro'],item['fecha_devolucion'],item['quantity'],item['precio_diario']))
                    continue
                table={'viaje':'viaje_simple','paquete':'paquete_de_viajes'}[item['tipo']]
                cur.execute(sql.SQL("UPDATE {} SET cupos=cupos-%s,estado=CASE WHEN cupos-%s=0 THEN 'No disponible' ELSE estado END WHERE codigo=%s AND cupos>=%s RETURNING codigo").format(sql.Identifier(table)),(item['quantity'],item['quantity'],item['id'],item['quantity']))
                if not cur.fetchone(): raise HTTPException(409,'Pago recibido sin cupos suficientes: requiere revisión administrativa')
                cur.execute('''INSERT INTO ventas(vtas_id,fecha,hora,medio_de_pago,cuotas,cantidad,codigo_vs,codigo_pv,precio)
                    VALUES(%s,CURRENT_DATE,LOCALTIME,%s,%s,%s,%s,%s,%s)''',
                    (sale_id,payment.get('payment_method_id','Mercado Pago'),(payment.get('installments') or 1)>1,item['quantity'],item['id'] if item['tipo']=='viaje' else None,item['id'] if item['tipo']=='paquete' else None,Decimal(str(item['unit_price']))*item['quantity']))
                cur.execute('INSERT INTO vtas_uc(vtas_id,uc_id) VALUES(%s,%s)',(sale_id,order['uc_id']))
                cur.execute('INSERT INTO pedido_ventas(pedido_id,venta_id) VALUES(%s,%s)',(order_id,sale_id))
                sale_id+=1
            cur.execute('SELECT nombre,correo_electronico FROM usuario_comun WHERE uc_id=%s',(order['uc_id'],))
            user=cur.fetchone()
            subject,body=compose(order,user['nombre'],payment_id,payment.get('live_mode',False))
            cur.execute('INSERT INTO correos_compra(pedido_id,destinatario,asunto,cuerpo) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING',(order_id,user['correo_electronico'],subject,body))
            admin_subject,admin_body=compose_admin(order,user,payment_id,payment.get('live_mode',False))
            cur.execute("INSERT INTO correos_compra(pedido_id,tipo,destinatario,asunto,cuerpo) VALUES(%s,'administrador',%s,%s,%s) ON CONFLICT DO NOTHING",(order_id,correo_empresa(cur),admin_subject,admin_body))
            cur.execute("UPDATE pedidos SET estado='confirmado',pago_id=%s WHERE id=%s",(str(payment_id),order_id))
    return order_id
