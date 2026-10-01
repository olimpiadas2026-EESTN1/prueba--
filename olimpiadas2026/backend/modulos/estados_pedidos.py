"""Seguimiento operativo independiente de la aprobación financiera."""
from fastapi import HTTPException
from psycopg.rows import dict_row
from modulos.gestion import connection

TRANSICIONES = {
    'pendiente': {'en_preparacion', 'en_revision'},
    'en_preparacion': {'listo', 'en_revision'},
    'listo': {'en_revision'},
    'completado': set(),
    'en_revision': {'pendiente', 'en_preparacion', 'listo'},
}


def cambiar(order_id, nuevo, esperado, motivo, admin):
    motivo = motivo.strip()
    if not motivo or len(motivo) > 500:
        raise HTTPException(422, 'Ingresá un motivo de hasta 500 caracteres')
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT estado,estado_gestion FROM pedidos WHERE id=%s AND eliminado_en IS NULL AND anulado_en IS NULL FOR UPDATE', (order_id,))
            pedido = cur.fetchone()
            if not pedido:
                raise HTTPException(404, 'Pedido no encontrado')
            actual = pedido['estado_gestion']
            if actual != esperado:
                raise HTTPException(409, 'Otro administrador actualizó el pedido. Actualizá los datos.')
            if nuevo not in TRANSICIONES.get(actual, set()):
                raise HTTPException(409, 'Cambio de estado no permitido')
            if nuevo in {'en_preparacion', 'listo', 'completado'} and pedido['estado'] != 'confirmado':
                raise HTTPException(409, 'Primero debe confirmarse el pago mediante Mercado Pago')
            cur.execute('UPDATE pedidos SET estado_gestion=%s WHERE id=%s', (nuevo, order_id))
            cur.execute('INSERT INTO pedido_estados(pedido_id,ua_id,anterior,nuevo,motivo) VALUES (%s,%s,%s,%s,%s)',
                        (order_id, admin['id'], actual, nuevo, motivo))
    return {'ok': True, 'estado_gestion': nuevo}
