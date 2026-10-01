from fastapi import HTTPException
from modulos.gestion import query
# ===============================
#   Conexión con la Base de Datos
# ===============================

from main import get_connection

# ===============================
#     funciones auxiliares
# ===============================

from controladores.date import convertirHora
from types import SimpleNamespace

# ===============================
#             CRUD
# ===============================


# ---- Insertar Excursión ----
def agregarExcursiones(data):
    """
    Inserta una nueva excursión en la base de datos.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("LOCK TABLE excursiones IN SHARE ROW EXCLUSIVE MODE")
        cur.execute("SELECT MAX(excursion_id) FROM excursiones")
        max_id = cur.fetchone()
        if max_id[0] is None:
            max_id = 1
        else:
            max_id = int(max_id[0]) + 1

        horaInicio = convertirHora(data.inicio)
        horaFinal = convertirHora(data.final)

        cur.execute(
            "INSERT INTO excursiones (excursion_id, nombre, inicio, final, descripcion, lugar) VALUES(%s,%s,%s,%s,%s,%s)",
            (
                max_id,
                data.nombre,
                horaInicio,
                horaFinal,
                data.descripcion,
                data.lugar,
            ),
        )
        conn.commit()

        return {"Mensaje": "Se ha agregado la excursion exitosamente"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


# ---- Eliminar Excursión ----
def eliminarExcursion(excursion_id):
    """
    Elimina las excurisones
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM pv_exc WHERE exc_id = %s", (excursion_id,))
        n = cur.fetchall()
        regExcPvIDs = []
        for i in n:

            regExcPvIDs.append(i[2])

        for id in regExcPvIDs:
            cur.execute("DELETE FROM pv_exc WHERE id = %s", (id,))
            conn.commit()

        cur.execute("DELETE FROM excursiones WHERE excursion_id = %s", (excursion_id,))
        conn.commit()

        return {"Mensaje": "Borrado exitosamente"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        conn.close()


# ---- Obtener excursion ----
def verExcursiones():
    """
    Obtiene todas las excurisones.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM excursiones WHERE eliminado_en IS NULL")
        respuesta = cur.fetchall()
        excursiones = []

        for exc in respuesta:
            inicio = exc[2]
            inicio = inicio.strftime("%H:%M:%S")
            final = exc[3]
            final = final.strftime("%H:%M:%S")
            excursion = {
                "Excursion id": exc[0],
                "Nombre": exc[1],
                "Inicio": inicio,
                "Final": final,
                "Descripcion": exc[4],
                "Lugar": exc[5],
            }

            excursiones.append(excursion)
        return excursiones

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
#  Relacionar Excursión & Paquete
# ===============================


def paqueteViajesExcursion(data):
    """Vincula productos activos sin duplicar la relación."""
    from modulos.vinculos_catalogo import vincular
    return vincular('pv_exc',data.pv_id,data.exc_id)

def buscarExcursionporId(data):
    """Mantiene la lista esperada por el frontend y devuelve 404 si no existe."""
    rows=query("""SELECT excursion_id AS "Excursion id",nombre AS "Nombre",to_char(inicio,'HH24:MI:SS') AS "Inicio",to_char(final,'HH24:MI:SS') AS "Final",descripcion AS "Descripcion",lugar AS "Lugar" FROM excursiones WHERE excursion_id=%s AND eliminado_en IS NULL""",(data.excursion_id,))
    if not rows: raise HTTPException(404,'Excursión no encontrada')
    return rows

def verExcursionPaquete(data):
    """Una consulta; conserva el formato de listas usado por paquetes."""
    rows=query("""SELECT DISTINCT e.excursion_id AS "Excursion id",e.nombre AS "Nombre",to_char(e.inicio,'HH24:MI:SS') AS "Inicio",to_char(e.final,'HH24:MI:SS') AS "Final",e.descripcion AS "Descripcion",e.lugar AS "Lugar" FROM pv_exc x JOIN excursiones e ON e.excursion_id=x.exc_id JOIN paquete_de_viajes p ON p.codigo=x.pv_id WHERE x.pv_id=%s AND e.eliminado_en IS NULL AND p.eliminado_en IS NULL ORDER BY e.excursion_id""",(data.pv_id,))
    return [[row] for row in rows]
