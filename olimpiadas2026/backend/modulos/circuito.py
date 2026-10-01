"""Pedidos editables, entrega, solicitudes y cuenta corriente interna."""
from collections import defaultdict
from datetime import date
from decimal import Decimal
from uuid import uuid4
from fastapi import HTTPException
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from modulos.gestion import connection, query


def cotizar(cur, items):
    if not items or len(items)>100: raise HTTPException(422,'Seleccioná entre 1 y 100 artículos')
    cantidades=defaultdict(int)
    for item in items:
        pickup=getattr(item,'fecha_retiro',None)
        dropoff=getattr(item,'fecha_devolucion',None)
        try:
            if isinstance(pickup,str): pickup=date.fromisoformat(pickup)
            if isinstance(dropoff,str): dropoff=date.fromisoformat(dropoff)
        except ValueError: raise HTTPException(422,'Ingresá fechas válidas de retiro y devolución para cada alquiler')
        if item.tipo=='auto':
            if not pickup or not dropoff or pickup<date.today() or dropoff<=pickup: raise HTTPException(422,'Ingresá fechas futuras válidas de retiro y devolución para cada alquiler')
        elif pickup or dropoff:
            raise HTTPException(422,'Las fechas de alquiler solo corresponden a autos')
        cantidades[(item.tipo,item.id,pickup,dropoff)]+=item.quantity
    snapshot=[]; total=Decimal('0')
    for (tipo,code,pickup,dropoff),cantidad in sorted(cantidades.items(),key=lambda row:(row[0][0],row[0][1],row[0][2] or '',row[0][3] or '')):
        if cantidad<1 or cantidad>50: raise HTTPException(422,'Máximo 50 unidades por producto')
        if tipo=='auto':
            cur.execute('SELECT modelo,disponibles,precio_por_dia FROM auto WHERE auto_id=%s AND eliminado_en IS NULL',(code,))
            p=cur.fetchone()
            if not p or p['disponibles']<1: raise HTTPException(409,'Auto no disponible')
            cur.execute('SELECT COALESCE(SUM(cantidad),0) AS reservados FROM alquileres_auto WHERE auto_id=%s AND fecha_retiro<%s AND fecha_devolucion>%s',(code,dropoff,pickup))
            reserved=cur.fetchone()['reservados']
            if reserved+cantidad>p['disponibles']: raise HTTPException(409,'El auto no tiene disponibilidad para esas fechas')
            daily_price=Decimal(str(p['precio_por_dia']))
            precio=daily_price*(dropoff-pickup).days
            name=p['modelo']
        else:
            table={'viaje':'viaje_simple','paquete':'paquete_de_viajes'}[tipo]
            cur.execute(sql.SQL('SELECT nombre,precio,cupos,estado FROM {} WHERE codigo=%s AND eliminado_en IS NULL').format(sql.Identifier(table)),(code,))
            p=cur.fetchone()
            if not p or p['cupos']<cantidad or p['estado']!='Disponible': raise HTTPException(409,'Producto no disponible o sin cupos suficientes')
            precio=Decimal(str(p['precio']))
            daily_price=None
            name=p['nombre']
        if not precio.is_finite() or precio<=0: raise HTTPException(409,'Precio inválido')
        snapshot.append({'tipo':tipo,'id':code,'title':name,'unit_price':float(precio),'quantity':cantidad,**({'fecha_retiro':pickup.isoformat(),'fecha_devolucion':dropoff.isoformat(),'precio_diario':float(daily_price)} if tipo=='auto' else {})})
        total+=precio*cantidad
    return snapshot,total


def crear(items,user_id):
    order_id=str(uuid4())
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            snapshot,total=cotizar(cur,items)
            cur.execute("INSERT INTO pedidos(id,uc_id,estado,total,items) VALUES(%s,%s,'creado',%s,%s)",(order_id,user_id,total,Jsonb(snapshot)))
    return {'pedido_id':order_id,'total':total}


def bloquear(cur,order_id,user_id=None):
    cur.execute('SELECT * FROM pedidos WHERE id=%s AND (%s::integer IS NULL OR uc_id=%s) AND eliminado_en IS NULL FOR UPDATE',(order_id,user_id,user_id))
    order=cur.fetchone()
    if not order: raise HTTPException(404,'Pedido no encontrado')
    if order['anulado_en']: raise HTTPException(409,'El pedido está anulado')
    return order


def editable(order):
    if order['estado_gestion'] not in ('pendiente','en_revision'):
        raise HTTPException(409,'El pedido ya está en preparación o entregado')
    if order['checkout_iniciado'] or order['preferencia_id'] or order['pago_id']:
        raise HTTPException(409,'El pago ya fue iniciado. Enviá una solicitud a ventas para modificar o anular el pedido.')


def modificar(order_id,items,version,user_id):
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            order=bloquear(cur,order_id,user_id); editable(order)
            if order['version']!=version: raise HTTPException(409,'El pedido cambió. Actualizá la lista.')
            snapshot,total=cotizar(cur,items)
            cur.execute('UPDATE pedidos SET items=%s,total=%s,version=version+1 WHERE id=%s',(Jsonb(snapshot),total,order_id))
    return {'ok':True,'total':total}


def anular(order_id,motivo,user_id=None,admin=None):
    motivo=texto(motivo)
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            order=bloquear(cur,order_id,user_id); editable(order)
            cur.execute('UPDATE pedidos SET anulado_en=now(),motivo_anulacion=%s,version=version+1 WHERE id=%s',(motivo,order_id))
            if admin: audit(cur,admin,'pedidos',order_id,{'accion':'anular','motivo':motivo})
    return {'ok':True}


def texto(value):
    value=value.strip()
    if not value or len(value)>1000: raise HTTPException(422,'Ingresá un texto de entre 1 y 1000 caracteres')
    return value


def audit(cur,admin,entity,key,data):
    cur.execute('INSERT INTO admin_auditoria(ua_id,entidad,registro_id,cambios) VALUES(%s,%s,%s,%s)',(admin['id'],entity,str(key),Jsonb(data)))


def entregar(order_id,observaciones,admin):
    observaciones=texto(observaciones)
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            order=bloquear(cur,order_id)
            if order['estado']!='confirmado' or order['estado_gestion'] not in ('listo','completado'):
                raise HTTPException(409,'La entrega requiere pago confirmado y pedido listo')
            cur.execute('SELECT 1 FROM pedidos_entregados WHERE pedido_id=%s',(order_id,))
            if cur.fetchone(): raise HTTPException(409,'La entrega ya está registrada')
            cur.execute('SELECT 1 FROM solicitudes_pedido WHERE pedido_id=%s AND estado=\'pendiente\'',(order_id,))
            if cur.fetchone(): raise HTTPException(409,'Resolvé primero la solicitud pendiente del cliente')
            cur.execute('INSERT INTO pedidos_entregados(pedido_id,uc_id,ua_id,observaciones,total,articulos) VALUES(%s,%s,%s,%s,%s,%s)',(order_id,order['uc_id'],admin['id'],observaciones,order['total'],Jsonb(order['items'])))
            cur.execute("UPDATE pedidos SET estado_gestion='completado',version=version+1 WHERE id=%s",(order_id,))
            cur.execute("INSERT INTO pedido_estados(pedido_id,ua_id,anterior,nuevo,motivo) VALUES(%s,%s,%s,'completado',%s)",(order_id,admin['id'],order['estado_gestion'],observaciones))
            audit(cur,admin,'pedidos',order_id,{'accion':'entregar','observaciones':observaciones})
    return {'ok':True}


def solicitar(order_id,tipo,detalle,user_id):
    detalle=texto(detalle)
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            order=bloquear(cur,order_id,user_id)
            if order['estado_gestion']=='completado': raise HTTPException(409,'El pedido ya fue entregado')
            cur.execute("SELECT 1 FROM solicitudes_pedido WHERE pedido_id=%s AND estado='pendiente'",(order_id,))
            if cur.fetchone(): raise HTTPException(409,'Ya tenés una solicitud pendiente para este pedido')
            cur.execute('INSERT INTO solicitudes_pedido(pedido_id,uc_id,tipo,detalle) VALUES(%s,%s,%s,%s)',(order_id,user_id,tipo,detalle))
    return {'ok':True}


def resolver(solicitud_id,estado,respuesta,admin):
    respuesta=texto(respuesta)
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("UPDATE solicitudes_pedido SET estado=%s,respuesta=%s,ua_id=%s,resuelto_en=now() WHERE id=%s AND estado='pendiente' RETURNING id",(estado,respuesta,admin['id'],solicitud_id))
            if not cur.fetchone(): raise HTTPException(409,'La solicitud no existe o ya fue respondida')
            audit(cur,admin,'solicitudes',solicitud_id,{'estado':estado,'respuesta':respuesta})
    return {'ok':True}


def cuenta(orden='fecha',solo_pendientes=True):
    order='u.apellido,u.nombre,u.uc_id,f.emitida_en,f.numero' if orden=='cliente' else 'f.emitida_en,f.numero'
    return query('''SELECT f.numero,f.pedido_id,f.emitida_en,u.uc_id,u.nombre,u.apellido,
    f.importe,p.estado AS estado_pago,p.anulado_en,
    CASE WHEN p.estado='confirmado' OR p.anulado_en IS NOT NULL THEN 0 ELSE f.importe END AS saldo,
    p.eliminado_en AS archivado_en
    FROM facturas_internas f JOIN pedidos p ON p.id=f.pedido_id JOIN usuario_comun u ON u.uc_id=p.uc_id
    WHERE (NOT %s OR (p.estado<>'confirmado' AND p.anulado_en IS NULL)) ORDER BY '''+order+' LIMIT 500',(solo_pendientes,))


def correo_empresa(cur):
    cur.execute('SELECT correo_ventas FROM configuracion_empresa WHERE id=1')
    row=cur.fetchone()
    return row['correo_ventas'] if row else ''


def guardar_correo(correo,admin):
    correo=correo.strip()
    if len(correo)>254 or correo.count('@')!=1 or any(c.isspace() for c in correo) or not all(correo.split('@')):
        raise HTTPException(422,'Correo inválido')
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('INSERT INTO configuracion_empresa(id,correo_ventas) VALUES(1,%s) ON CONFLICT(id) DO UPDATE SET correo_ventas=EXCLUDED.correo_ventas,actualizado_en=now()',(correo,))
            audit(cur,admin,'configuracion_empresa',1,{'correo_ventas':correo})
    return {'ok':True}


def pagar(order_id,user_id,sdk):
    """Una sola preferencia por pedido; los fallos inciertos requieren conciliación."""
    import os
    if sdk is None: raise HTTPException(503,'Mercado Pago no configurado')
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            order=bloquear(cur,order_id,user_id)
            if order['estado']=='confirmado': raise HTTPException(409,'Este pedido ya está pagado')
            if order['preferencia_id']:
                response=sdk.preference().get(order['preferencia_id'])
                data=response.get('response',{})
                if response.get('status')!=200 or not data.get('init_point'): raise HTTPException(502,'No se pudo recuperar el checkout')
                return {'init_point':data['init_point']}
            editable(order)
            # Verificar disponibilidad sin cambiar el precio acordado del pedido.
            from types import SimpleNamespace
            cotizar(cur,[SimpleNamespace(tipo=i['tipo'],id=i['id'],quantity=i['quantity'],fecha_retiro=i.get('fecha_retiro'),fecha_devolucion=i.get('fecha_devolucion')) for i in order['items']])
            cur.execute('UPDATE pedidos SET checkout_iniciado=true,version=version+1 WHERE id=%s',(order_id,))
    try:
        base=(os.getenv('FRONTEND_URL') or 'http://localhost:5173').rstrip('/')
        pref={'external_reference':str(order_id),'items':[{'title':i['title'],'quantity':i['quantity'],'unit_price':i['unit_price'],'id':f"{i['tipo']}:{i['id']}",'currency_id':'ARS'} for i in order['items']], 'back_urls':{k:base+'/mis-pedidos' for k in ('success','failure','pending')}}
        url=os.getenv('MERCADOPAGO_WEBHOOK_URL','').strip()
        if url:
            if not url.startswith('https://'): raise ValueError('Webhook inválido')
            pref['notification_url']=url
        response=sdk.preference().create(pref); data=response.get('response',{})
        if response.get('status') not in (200,201) or not data.get('id') or not data.get('init_point'): raise ValueError('Preferencia rechazada')
    except Exception:
        with connection() as conn: conn.execute("UPDATE pedidos SET estado='error_checkout' WHERE id=%s",(order_id,))
        raise HTTPException(502,'No se pudo iniciar el pago. Pedí a ventas que revise el intento antes de reintentar.')
    with connection() as conn:
        conn.execute("UPDATE pedidos SET preferencia_id=%s,estado=CASE WHEN estado='confirmado' THEN estado ELSE 'pendiente_pago' END WHERE id=%s",(data['id'],order_id))
    return {'init_point':data['init_point']}
