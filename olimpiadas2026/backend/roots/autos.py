
# ===============================
#         Creación del Router
# ===============================

from fastapi import APIRouter

router = APIRouter()


# ===============================
#         Importación de CRUD
# ===============================

from modulos.autos import (
    agregarAuto,
    borrarAuto,
    verAutos,
    vinculaVSaAuto,
    vincularPVaAuto,
    verAutoID,
    verAutoPV,
    verAutoVs,
)


# ===============================
#         Importación de Modelos
# ===============================

from modulos.esquemas import (
    Auto,
    Auto_id,
    Vinculo_vs_a_auto,
    Vinculo_pv_a_auto,
    Paquete_de_viaje_id,
    Viaje_simple_id,
)


# ===============================
#             Rutas CRUD
# ===============================


# ---- Crear nuevo auto ----

@router.post("/ingresar")
async def ingresar_autos(data: Auto):
    """
    Recibe los datos de un auto y lo agrega a la base de datos.
    """

    res = agregarAuto(data)
    return res


# ---- Crear relación de viaje simple a auto ----

@router.post("/ingresarVinculoVS")
async def ingresar_vinculos_VS(data: Vinculo_vs_a_auto):
    """
    Recibe los IDs de un viaje simple y un auto,
    y crea la relación.
    """

    res = vinculaVSaAuto(data)
    return res


# ---- Crear relación de paquete de viaje a auto ----

@router.post("/ingresarVinculoPV")
async def ingresar_vinculos_PV(data: Vinculo_pv_a_auto):
    """
    Recibe los IDs de un paquete de viaje y un auto,
    y crea la relación.
    """

    res = vincularPVaAuto(data)
    return res


# ---- Obtener lista de autos ----

@router.get("/obtener")
async def retornar_autos():
    """
    Devuelve la lista de autos almacenados.
    """

    res = verAutos()
    return res


# ---- Obtener auto por ID ----

@router.post("/obtenerID")
async def retornar_autosPorID(data: Auto_id):
    """
    Devuelve un auto utilizando su ID.
    """

    res = verAutoID(data)
    return res


# ---- Obtener autos relacionados a un paquete de viaje ----

@router.post("/obtenerPV")
async def retornar_autosPorPV(data: Paquete_de_viaje_id):
    """
    Devuelve los autos relacionados a un paquete de viaje.
    """

    res = verAutoPV(data)
    return res


# ---- Obtener autos relacionados a un viaje simple ----

@router.post("/obtenerVS")
async def retornar_autosPorVS(data: Viaje_simple_id):
    """
    Devuelve los autos relacionados a un viaje simple.
    """

    res = verAutoVs(data)
    return res


# ---- Eliminar un auto por ID ----

@router.post("/eliminar")
async def eliminar_autos(data: Auto_id):
    """
    Elimina un auto de la base de datos utilizando su ID.
    """

    res = borrarAuto(data.auto_id)
    return res

