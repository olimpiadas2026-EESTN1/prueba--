
# ===============================
#         Creación del Router
# ===============================

from fastapi import APIRouter, Depends, Header
from modulos.administradores import require_admin

router = APIRouter()


# ===============================
#       Importación de CRUD
# ===============================

from modulos.usuarioComun import (
    crearCliente,
    verClientes,
    verClienteId,
    eliminarUsuario,
    validarCliente,
)


# ===============================
#       Importación de Modelos
# ===============================

from modulos.esquemas import (
    Usuarios_comunes,
    Usuarios_comunes_id,
    Validacion_de_usuarios,
)


# ===============================
#           Rutas CRUD
# ===============================


# ---- Crear nuevo usuario común ----
@router.post("/ingresar")
async def ingresar_usuario(data: Usuarios_comunes):
    """
    Recibe los datos de un usuario común y lo crea en la base de datos.
    """
    res = await crearCliente(data)
    return res


# ---- Obtener todos los usuarios comunes ----
@router.get("/obtener", dependencies=[Depends(require_admin)])
def retornar_usuario():
    """
    Devuelve la lista de todos los usuarios comunes.
    """
    res = verClientes()
    return res


# ---- Eliminar usuario común por ID ----
@router.post("/eliminar", dependencies=[Depends(require_admin)])
def eliminar_usuario(
    data: Usuarios_comunes_id,
    admin=Depends(require_admin)
):
    """
    Elimina un usuario común dado su ID.
    """
    from modulos.papelera import cambiar

    res = cambiar(
        "usuarios",
        data.uc_id,
        "Baja desde endpoint compatible",
        admin
    )

    return res


# ---- Obtener usuario común por ID ----
@router.post("/obtenerId", dependencies=[Depends(require_admin)])
def retornarPorID_usuario(data: Usuarios_comunes_id):
    """
    Devuelve los datos de un usuario común específico por ID.
    """
    res = verClienteId(data)
    return res


# ---- Validar contraseña ----
@router.post("/validarContrasena")
def retornarValidacion(data: Validacion_de_usuarios):
    """
    Devuelve la validación en formato booleano
    de si existe o no el usuario.
    """
    res = validarCliente(data)
    return res


# ===============================
#            COMPRAS
# ===============================

from modulos import compras


# ---- Iniciar sesión comprador ----
@router.post("/sesion")
def buyer_login(data: Validacion_de_usuarios):
    return compras.login(
        data.usuarioIngresado,
        data.contraseñaIngresada
    )


# ---- Cerrar sesión comprador ----
@router.post("/cerrarSesion")
def buyer_logout(
    authorization: str = Header(default=""),
    user_id=Depends(compras.require_buyer)
):
    compras._sessions.pop(
        authorization.removeprefix("Bearer "),
        None
    )

    return {
        "ok": True
    }


# ---- Mis pedidos ----
@router.get("/mis-pedidos")
def my_orders(
    user_id=Depends(compras.require_buyer)
):
    from modulos.gestion import query

    return query(
        """
        SELECT
            id,
            creado_en,
            estado,
            estado_gestion,
            total,
            moneda,
            items,
            version,
            checkout_iniciado,
            preferencia_id,
            anulado_en
        FROM pedidos
        WHERE uc_id = %s
          AND eliminado_en IS NULL
        ORDER BY creado_en DESC
        LIMIT 200
        """,
        (user_id,)
    )

