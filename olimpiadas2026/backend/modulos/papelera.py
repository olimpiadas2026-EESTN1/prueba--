"""Bajas reversibles sin borrar relaciones, pagos ni comprobantes."""
from uuid import UUID
from fastapi import HTTPException
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from modulos.gestion import connection

ENTIDADES = {
    'usuarios': ('usuario_comun', 'uc_id'),
    'viajes': ('viaje_simple', 'codigo'),
    'paquetes': ('paquete_de_viajes', 'codigo'),
    'autos': ('auto', 'auto_id'),
    'pedidos': ('pedidos', 'id'),
    'ventas': ('ventas', 'vtas_id'),
}


def cambiar(kind, key, motivo, admin, restaurar=False):
    if kind not in ENTIDADES:
        raise HTTPException(404, 'Entidad inexistente')
    try:
        key = UUID(str(key)) if kind == 'pedidos' else int(key)
        if kind != 'pedidos' and key <= 0: raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(422, 'Identificador inválido')
    motivo = motivo.strip()
    if not motivo or len(motivo) > 500:
        raise HTTPException(422, 'Ingresá un motivo de hasta 500 caracteres')
    table, pk = ENTIDADES[kind]
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql.SQL('SELECT eliminado_en FROM {} WHERE {}=%s FOR UPDATE').format(sql.Identifier(table), sql.Identifier(pk)), (key,))
            row = cur.fetchone()
            if not row: raise HTTPException(404, 'Registro no encontrado')
            if (row['eliminado_en'] is None) == restaurar:
                raise HTTPException(409, 'El registro ya está activo' if restaurar else 'El registro ya está en la papelera')
            cur.execute(sql.SQL('UPDATE {} SET eliminado_en={} WHERE {}=%s').format(sql.Identifier(table), sql.SQL('NULL' if restaurar else 'now()'), sql.Identifier(pk)), (key,))
            cur.execute('INSERT INTO admin_auditoria(ua_id,entidad,registro_id,cambios) VALUES (%s,%s,%s,%s)',
                        (admin['id'], kind, str(key), Jsonb({'accion':'restaurar' if restaurar else 'eliminar', 'motivo':motivo})))
    if kind == 'usuarios' and not restaurar:
        from modulos.compras import _sessions
        for token, session in list(_sessions.items()):
            if session[0] == key: _sessions.pop(token, None)
    return {'ok': True}
