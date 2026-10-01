from fastapi import HTTPException
from modulos.gestion import query
# ===============================
#   Conexión con la Base de Datos
# ===============================

from main import get_connection

# ===============================
#     funciones auxiliares
# ===============================

from types import SimpleNamespace

# ===============================
#           CRUD Autos
# ===============================


def agregarAuto(data):
    """
    Inserta un nuevo auto en la tabla 'auto'.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("LOCK TABLE auto IN SHARE ROW EXCLUSIVE MODE")
        cur.execute("SELECT MAX(auto_id) FROM auto")
        max_id = cur.fetchone()
        if max_id[0] is None:
            max_id = 1
        else:
            max_id = int(max_id[0]) + 1

        cur.execute(
            "INSERT INTO auto (auto_id, modelo, disponibles, precio_por_dia) VALUES(%s,%s,%s,%s)",
            (max_id, data.modelo, data.disponibles, data.precio_por_dia),
        )
        conn.commit()

        return {"mensaje": "Nuevo auto cargado exitosamente"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


def borrarAuto(auto_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM vs_at WHERE at_id = %s", (auto_id,))
        r = cur.fetchall()
        regAtVsIdDs = []
        for i in r:
            regAtVsIdDs.append(i[0])

        for registroId in regAtVsIdDs:
            cur.execute("DELETE FROM vs_at WHERE id = %s", (registroId,))
            conn.commit()

        cur.execute("SELECT id FROM exc_at WHERE at_id = %s", (auto_id,))
        n = cur.fetchall()
        regAtPVIdDs = []
        for i in n:
            regAtPVIdDs.append(i[0])

        for registroId in regAtPVIdDs:
            cur.execute("DELETE FROM exc_at WHERE id = %s", (registroId,))
            conn.commit()

        cur.execute("DELETE FROM auto WHERE auto_id = %s", (auto_id,))
        conn.commit()

        return {"Mensaje": "Auto eliminado exitosamente"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


def verAutos():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM auto WHERE eliminado_en IS NULL")
        respuesta = cur.fetchall()
        autos = []
        for auto in respuesta:
            at = {
                "auto id": auto[0],
                "modelo": auto[1],
                "disponibles": auto[2],
                "precio por dia": auto[3],
            }

            autos.append(at)

        return autos
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


# ===============================
#   Vincular autos a viajes
# ===============================


def vinculaVSaAuto(data):
    """Vincula productos activos sin duplicar la relación."""
    from modulos.vinculos_catalogo import vincular
    return vincular('vs_at',data.vs_id,data.at_id)

def vincularPVaAuto(data):
    """Vincula productos activos sin duplicar la relación."""
    from modulos.vinculos_catalogo import vincular
    return vincular('exc_at',data.pv_id,data.at_id)

def verAutoID(data):
    """Devuelve un auto activo o 404 sin exponer errores SQL."""
    rows=query('SELECT auto_id AS "auto id",modelo,disponibles,precio_por_dia AS "precio por dia" FROM auto WHERE auto_id=%s AND eliminado_en IS NULL',(data.auto_id,))
    if not rows: raise HTTPException(404,'Auto no encontrado')
    return rows[0]

def verAutoPV(data):
    """Consulta los autos relacionados en una sola conexión."""
    return query('SELECT DISTINCT a.auto_id AS "auto id",a.modelo,a.disponibles,a.precio_por_dia AS "precio por dia" FROM exc_at x JOIN auto a ON a.auto_id=x.at_id JOIN paquete_de_viajes p ON p.codigo=x.pv_id WHERE x.pv_id=%s AND a.eliminado_en IS NULL AND p.eliminado_en IS NULL ORDER BY a.auto_id',(data.pv_id,))

def verAutoVs(data):
    """Consulta los autos relacionados en una sola conexión."""
    return query('SELECT DISTINCT a.auto_id AS "auto id",a.modelo,a.disponibles,a.precio_por_dia AS "precio por dia" FROM vs_at x JOIN auto a ON a.auto_id=x.at_id JOIN viaje_simple p ON p.codigo=x.vs_id WHERE x.vs_id=%s AND a.eliminado_en IS NULL AND p.eliminado_en IS NULL ORDER BY a.auto_id',(data.vs_id,))
