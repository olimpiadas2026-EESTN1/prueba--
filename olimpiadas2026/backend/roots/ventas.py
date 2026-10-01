# ===============================
#         Creación del Router
# ===============================

from fastapi import APIRouter, Depends
from modulos.administradores import require_admin

router = APIRouter()

# ===============================
#       Importación de CRUD
# ===============================

from modulos.ventas import (
    sumarVenta,
    verVentas,
    buscarVentaId,
    cancelarCompraTVS,
    buscarVentaUsuario,
)

# ===============================
#       Importación de Modelos
# ===============================

from modulos.esquemas import Venta_request, Venta_id, Usuarios_comunes_id

# ===============================
#       Funciones auxiliares
# ===============================

# ===============================
#           Rutas CRUD
# ===============================


# ---- Crear nueva venta ----
@router.post("/ingresar", dependencies=[Depends(require_admin)])
def ingresar_ventas(data: Venta_request):
    """
    Registra una nueva venta en la base de datos.
    """
    res = sumarVenta(data)
    return res


# ---- Obtener todas las ventas ----
@router.get("/obtener", dependencies=[Depends(require_admin)])
def retornar_ventas():
    """
    Devuelve la lista de todas las ventas registradas.
    """
    res = verVentas()
    return res


# ---- Obtener todas las ventas relacionadas a una id ----
@router.post("/obtenerID", dependencies=[Depends(require_admin)])
def retornar_ventas(data: Venta_id):
    """
    Devuelve la lista de todas las ventas registradas por id.
    """
    res = buscarVentaId(data)
    return res


# ---- Obtener todas las ventas relacionadas a un usuario ----
@router.post("/obtenerUsuario", dependencies=[Depends(require_admin)])
def retornar_ventas(data: Usuarios_comunes_id):
    """
    Devuelve la lista de todas las ventas registradas por usuario.
    """
    res = buscarVentaUsuario(data)
    return res


# ---- Eliminar venta existente ----
@router.post("/eliminarTVS", dependencies=[Depends(require_admin)])
def eliminar_ventas(data: Venta_id, admin=Depends(require_admin)):
    """
    Elimina una venta de la base de datos.
    """
    from modulos.papelera import cambiar
    res = cambiar("ventas", data.vtas_id, "Baja desde endpoint compatible", admin)
    return res
