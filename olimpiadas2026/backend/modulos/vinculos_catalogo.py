"""Relaciones de catálogo validadas, idempotentes y transaccionales."""
from fastapi import HTTPException
from psycopg import sql
from modulos.gestion import connection
RELACIONES={
 'vs_at':('viaje_simple','codigo','vs_id','auto','auto_id','at_id'),
 'exc_at':('paquete_de_viajes','codigo','pv_id','auto','auto_id','at_id'),
}
def vincular(tabla,origen,destino):
    if tabla not in RELACIONES: raise HTTPException(404,'Relación inexistente')
    parent,pk1,col1,child,pk2,col2=RELACIONES[tabla]
    with connection() as conn:
        with conn.cursor() as cur:
            for table,pk,key in [(parent,pk1,origen),(child,pk2,destino)]:
                cur.execute(sql.SQL('SELECT 1 FROM {} WHERE {}=%s AND eliminado_en IS NULL FOR SHARE').format(sql.Identifier(table),sql.Identifier(pk)),(key,))
                if not cur.fetchone(): raise HTTPException(404,'Uno de los productos no existe o está eliminado')
            cur.execute(sql.SQL('LOCK TABLE {} IN SHARE ROW EXCLUSIVE MODE').format(sql.Identifier(tabla)))
            cur.execute(sql.SQL('INSERT INTO {}(id,{},{}) SELECT (SELECT COALESCE(MAX(id),0)+1 FROM {}),%s,%s WHERE NOT EXISTS(SELECT 1 FROM {} WHERE {}=%s AND {}=%s)').format(*map(sql.Identifier,[tabla,col1,col2,tabla,tabla,col1,col2])),(origen,destino,origen,destino))
    return {'Mensaje':'Vínculo registrado'}
