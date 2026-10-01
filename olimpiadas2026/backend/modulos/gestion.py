"""Consultas relacionales y edición administrativa con auditoría transaccional."""
from fastapi import HTTPException
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg import sql


def connection():
    from main import get_connection
    return get_connection()


def query(statement, params=()):
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(statement, params)
            return cur.fetchall()


def users(search='', eliminados=False):
    return query('''SELECT u.uc_id AS id, u.nombre, u.apellido, u.correo_electronico AS email, u.eliminado_en,
        (SELECT count(*) FROM pedidos p WHERE p.uc_id=u.uc_id) AS pedidos,
        (SELECT count(*) FROM vtas_uc v WHERE v.uc_id=u.uc_id) AS ventas
        FROM usuario_comun u WHERE concat_ws(' ',u.nombre,u.apellido,u.correo_electronico) ILIKE %s AND (u.eliminado_en IS NOT NULL)=%s
        ORDER BY u.uc_id DESC LIMIT 200''', ('%'+search+'%',eliminados))


def orders(user_id=None, eliminados=False):
    return query('''SELECT p.*, u.nombre, u.apellido, u.correo_electronico AS email
        FROM pedidos p JOIN usuario_comun u ON u.uc_id=p.uc_id
        WHERE (%s::boolean IS NULL OR (p.eliminado_en IS NOT NULL)=%s) AND (%s::integer IS NULL OR p.uc_id=%s) ORDER BY p.creado_en DESC LIMIT 200''', (eliminados,eliminados,user_id,user_id))


def sales(user_id=None, eliminados=False):
    return query('''SELECT v.vtas_id AS id, v.fecha, v.hora, v.medio_de_pago, v.cantidad,
        v.precio, v.eliminado_en, v.codigo_vs, v.codigo_pv, x.uc_id, u.nombre, u.apellido,
        u.correo_electronico AS email, COALESCE(vs.nombre,pv.nombre) AS producto
        FROM ventas v LEFT JOIN vtas_uc x ON x.vtas_id=v.vtas_id
        LEFT JOIN usuario_comun u ON u.uc_id=x.uc_id
        LEFT JOIN viaje_simple vs ON vs.codigo=v.codigo_vs
        LEFT JOIN paquete_de_viajes pv ON pv.codigo=v.codigo_pv
        WHERE (%s::boolean IS NULL OR (v.eliminado_en IS NOT NULL)=%s) AND (%s::integer IS NULL OR x.uc_id=%s)
        ORDER BY v.fecha DESC,v.vtas_id DESC LIMIT 200''', (eliminados,eliminados,user_id,user_id))


def profile(user_id):
    rows=query('SELECT uc_id AS id,nombre,apellido,correo_electronico AS email FROM usuario_comun WHERE uc_id=%s',(user_id,))
    if not rows: raise HTTPException(404,'Usuario no encontrado')
    return {'usuario':rows[0], 'pedidos':orders(user_id, None), 'ventas':sales(user_id, None)}


def summary():
    return query('''SELECT (SELECT count(*) FROM usuario_comun WHERE eliminado_en IS NULL) AS usuarios,
        (SELECT count(*) FROM pedidos WHERE eliminado_en IS NULL) AS pedidos,
        (SELECT count(*) FROM pedidos WHERE estado='pendiente_pago' AND eliminado_en IS NULL) AS pendientes,
        (SELECT count(*) FROM ventas) AS ventas,
        (SELECT COALESCE(sum(precio),0) FROM ventas) AS importe_ventas_registradas''')[0]


CATALOGS={'viajes':('viaje_simple','codigo'), 'paquetes':('paquete_de_viajes','codigo'),
          'autos':('auto','auto_id'), 'excursiones':('excursiones','excursion_id')}


def catalog(kind, eliminados=False):
    if kind not in CATALOGS: raise HTTPException(404,'Catálogo inexistente')
    table,key=CATALOGS[kind]
    return query(sql.SQL('SELECT * FROM {} WHERE (eliminado_en IS NOT NULL)=%s ORDER BY {} DESC LIMIT 200').format(sql.Identifier(table),sql.Identifier(key)), (eliminados,))


def update(kind, key, changes, admin):
    allowed={
        'usuarios':('usuario_comun','uc_id',{'nombre','apellido','correo_electronico'}),
        'viajes':('viaje_simple','codigo',{'nombre','descripcion','precio','cupos','estado'}),
        'paquetes':('paquete_de_viajes','codigo',{'nombre','descripcion','precio','cupos','estado'}),
        'autos':('auto','auto_id',{'modelo','disponibles','precio_por_dia'}),
        'excursiones':('excursiones','excursion_id',{'nombre','descripcion','lugar'}),
    }
    if kind not in allowed: raise HTTPException(404,'Entidad inexistente')
    table,pk,fields=allowed[kind]
    if not changes or not set(changes)<=fields: raise HTTPException(422,'Campos no permitidos')
    from decimal import Decimal, InvalidOperation
    for field,value in changes.items():
        if field in {'precio','precio_por_dia','cupos','disponibles'}:
            try: number=Decimal(str(value))
            except InvalidOperation: raise HTTPException(422,'Valor numérico inválido')
            if not number.is_finite() or number<0 or (field in {'cupos','disponibles'} and number!=int(number)):
                raise HTTPException(422,'Cantidad o precio inválido')
        elif not isinstance(value,str) or not value.strip() or len(value)>2000:
            raise HTTPException(422,'Texto inválido')
        if field=='estado' and value not in ['Disponible','No disponible']: raise HTTPException(422,'Estado inválido')
        if field=='correo_electronico' and ('@' not in value or len(value)>254): raise HTTPException(422,'Correo inválido')
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql.SQL('SELECT {} FROM {} WHERE {}=%s AND eliminado_en IS NULL FOR UPDATE').format(sql.SQL(',').join(map(sql.Identifier,changes)),sql.Identifier(table),sql.Identifier(pk)),(key,))
            old=cur.fetchone()
            if not old: raise HTTPException(404,'Registro no encontrado')
            if kind=='usuarios' and 'correo_electronico' in changes:
                changes['correo_electronico']=changes['correo_electronico'].strip().lower()
                cur.execute('SELECT 1 FROM usuario_comun WHERE lower(correo_electronico)=%s AND uc_id<>%s',(changes['correo_electronico'],key))
                if cur.fetchone(): raise HTTPException(409,'Ese correo ya está registrado')
            cur.execute(sql.SQL('UPDATE {} SET {} WHERE {}=%s').format(sql.Identifier(table),sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(f)) for f in changes),sql.Identifier(pk)),(*changes.values(),key))
            audit={f:{'antes':str(old[f]),'despues':str(v)} for f,v in changes.items()}
            cur.execute('INSERT INTO admin_auditoria(ua_id,entidad,registro_id,cambios) VALUES (%s,%s,%s,%s)',(admin['id'],kind,key,Jsonb(audit)))
    return {'ok':True}
