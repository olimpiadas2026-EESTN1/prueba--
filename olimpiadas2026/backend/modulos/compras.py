"""Pedidos vinculados al comprador autenticado; no confirman ventas ni pagos."""
import os
import secrets
import time
from uuid import uuid4
from collections import defaultdict
from decimal import Decimal
from fastapi import HTTPException, Header
import bcrypt
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from modulos.gestion import connection

_sessions={}


def login(email,password):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT uc_id,contraseña FROM usuario_comun WHERE lower(correo_electronico)=%s AND eliminado_en IS NULL',(email.strip().lower(),))
            row=cur.fetchone()
    try: valid=bool(row) and bcrypt.checkpw(password.encode(),row[1].encode())
    except (ValueError,TypeError): valid=False
    if not valid: raise HTTPException(401,'Correo o contraseña incorrectos')
    now=time.time()
    for key in list(_sessions):
        if _sessions.get(key,(None,0))[1]<=now: _sessions.pop(key,None)
    token=secrets.token_urlsafe(32)
    _sessions[token]=(row[0],now+3600)
    return {'token':token,'expires_in':3600}


def require_buyer(authorization: str=Header(default='')):
    token=authorization.removeprefix('Bearer ')
    session=_sessions.get(token) if authorization.startswith('Bearer ') else None
    if not session or session[1]<=time.time():
        _sessions.pop(token,None)
        raise HTTPException(401,'Volvé a iniciar sesión para realizar el pedido')
    with connection() as conn:
        active = conn.execute('SELECT 1 FROM usuario_comun WHERE uc_id=%s AND eliminado_en IS NULL', (session[0],)).fetchone()
    if not active:
        _sessions.pop(token, None)
        raise HTTPException(401, 'La cuenta ya no está activa')
    return session[0]


def checkout(items,user_id,sdk):
    if sdk is None: raise HTTPException(503,'Mercado Pago no está configurado')
    if not items or len(items)>100: raise HTTPException(422,'Carrito inválido')
    amounts=defaultdict(int)
    for item in items:
        if item.quantity<1 or item.quantity>50: raise HTTPException(422,'Cantidad inválida')
        amounts[(item.tipo,item.id)]+=item.quantity
    order_id=str(uuid4()); snapshot=[]; total=Decimal('0')
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            for (kind,code),quantity in sorted(amounts.items()):
                table={'viaje':'viaje_simple','paquete':'paquete_de_viajes'}[kind]
                cur.execute(sql.SQL('SELECT codigo,nombre,precio,cupos,estado FROM {} WHERE codigo=%s AND eliminado_en IS NULL').format(sql.Identifier(table)),(code,))
                product=cur.fetchone()
                if not product or product['cupos']<quantity or str(product['estado']).lower()!='disponible':
                    raise HTTPException(409,'Un producto no está disponible o no tiene suficientes cupos')
                price=Decimal(str(product['precio']))
                if not price.is_finite() or price<=0: raise HTTPException(409,'Precio de catálogo inválido')
                snapshot.append({'id':code,'tipo':kind,'title':product['nombre'],'unit_price':float(price),'quantity':quantity})
                total+=price*quantity
            cur.execute('INSERT INTO pedidos(id,uc_id,estado,total,items,checkout_iniciado) VALUES (%s,%s,%s,%s,%s,true)',(order_id,user_id,'creado',total,Jsonb(snapshot)))
    try:
        preference={
            'external_reference':order_id,
            'items':[{**{k:v for k,v in item.items() if k!='tipo'},'id':f"{item['tipo']}:{item['id']}",'currency_id':'ARS'} for item in snapshot],
            'back_urls':{key:os.getenv('FRONTEND_URL','http://localhost:5173').rstrip('/')+'/' for key in ['success','failure','pending']},
        }
        webhook_url=os.getenv('MERCADOPAGO_WEBHOOK_URL','').strip()
        if webhook_url:
            if not webhook_url.startswith('https://'): raise ValueError('Webhook requiere HTTPS')
            preference['notification_url']=webhook_url
        response=sdk.preference().create(preference)
        data=response.get('response',{})
        if response.get('status') not in (200,201) or not data.get('id') or not data.get('init_point'):
            raise ValueError('Preferencia rechazada')
    except Exception:
        with connection() as conn:
            conn.execute("UPDATE pedidos SET estado='error_checkout' WHERE id=%s",(order_id,))
        raise HTTPException(502,'No se pudo iniciar el pago. El intento quedó registrado en tu pedido')
    with connection() as conn:
        conn.execute("UPDATE pedidos SET estado=CASE WHEN estado='confirmado' THEN estado ELSE 'pendiente_pago' END,preferencia_id=%s WHERE id=%s",(data['id'],order_id))
    return {'pedido_id':order_id,'id':data['id'],'init_point':data['init_point'],'total':total}
