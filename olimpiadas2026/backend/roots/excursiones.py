# ===============================
#         Creación del Router
# ===============================

from fastapi import APIRouter, Depends
from modulos.administradores import require_admin

router = APIRouter()

# ===============================
#       Importación de CRUD
# ===============================

from modulos.excursiones import (
    agregarExcursiones,
    eliminarExcursion,
    paqueteViajesExcursion,
    buscarExcursionporId,
    verExcursionPaquete,
    verExcursiones,
)

# ===============================
#       Importación de Modelos
# ===============================

from modulos.esquemas import (
    Excursiones,
    Excursiones_id,
    Vinculo_pv_a_exc,
    Paquete_de_viaje_id,
)


# ===============================
#           Rutas CRUD
# ===============================


# ---- Crear nueva excursión ----
@router.post("/ingresar", dependencies=[Depends(require_admin)])
def ingresar_excursiones(data: Excursiones):
    """
    Recibe datos de una excursión y la agrega a la base de datos.
    """
    res = agregarExcursiones(data)
    return res


# ---- Crear nueva relacion paquete de viajes a excursion ----
@router.post("/ingresarVinculoPV", dependencies=[Depends(require_admin)])
def ingresar_vinculo_PV(data: Vinculo_pv_a_exc):
    """
    Recibe las ids de un paquete de viajes y una excursion, y los relaciona.
    """
    res = paqueteViajesExcursion(data)
    return res


# ---- Obtener todas las excursiones ----
@router.get("/obtener")
def retornar_excursiones():
    """
    Devuelve la lista de todas las excursiones almacenadas.
    """
    res = verExcursiones()
    return res


# ---- Obtener todas las excursiones por ID ----
@router.post("/obtenerID")
def retornar_excursionesPorID(data: Excursiones_id):
    """
    Devuelve la lista de todas las excursiones almacenadas basandose en su ID.
    """
    res = buscarExcursionporId(data)
    return res


# ---- Obtener todas las excursiones relacionadas a un paquete de viajes ----
@router.post("/obtenerPV")
def retornar_excursionesPorPV(data: Paquete_de_viaje_id):
    """
    Devuelve la lista de todas las excursiones almacenadas basandose en paquetes de viaje.
    """
    res = verExcursionPaquete(data)
    return res


# ---- Eliminar excursión por ID ----
@router.post("/eliminar", dependencies=[Depends(require_admin)])
def eliminar_excursiones(data: Excursiones_id, admin=Depends(require_admin)):
    """
    Elimina una excursión dado su ID.
    """
    from modulos.papelera import cambiar
    res = cambiar("excursiones", data.excursion_id, "Baja desde endpoint compatible", admin)
    return res
