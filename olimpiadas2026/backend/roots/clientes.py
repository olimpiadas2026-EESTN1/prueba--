# ===============================
#         Creación del Router
# ===============================

from fastapi import APIRouter, Depends
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


# ---- Crear nuevo usuario común ---- ANDA
@router.post("/ingresar")
async def ingresar_usuario(data: Usuarios_comunes):
    """
    Recibe los datos de un usuario común y lo crea en la base de datos.
    """
    res = crearCliente(data)
    return res


# ---- Obtener todos los usuarios comunes ----
@router.get("/obtener", dependencies=[Depends(require_admin)])
async def retornar_usuario():
    """
    Devuelve la lista de todos los usuarios comunes.
    """
    res = verClientes()
    return res


# ---- Eliminar usuario común por ID ----
@router.post("/eliminar", dependencies=[Depends(require_admin)])
async def eliminar_usuario(data: Usuarios_comunes_id):
    """
    Elimina un usuario común dado su ID.
    """
    res = eliminarUsuario(data)
    return res


# ---- Obtener usuario común por ID ----
@router.post("/obtenerId", dependencies=[Depends(require_admin)])
async def retornarPorID_usuario(data: Usuarios_comunes_id):
    """
    Devuelve los datos de un usuario común específico por ID.
    """
    res = verClienteId(data)
    return res


@router.post("/validarContrasena")
async def retornarValidacion(data: Validacion_de_usuarios):
    """
    Devuelve la validacion en formato booleano de si existe o no el usuario.
    """
    res = validarCliente(data)
    return res

from modulos import compras
from fastapi import Header

@router.post('/sesion')
def buyer_login(data: Validacion_de_usuarios):
    return compras.login(data.usuarioIngresado,data.contraseñaIngresada)

@router.post('/cerrarSesion')
def buyer_logout(authorization: str=Header(default=''), user_id=Depends(compras.require_buyer)):
    compras._sessions.pop(authorization.removeprefix('Bearer '),None)
    return {'ok':True}

@router.get('/mis-pedidos')
def my_orders(user_id=Depends(compras.require_buyer)):
    from modulos.gestion import query
    return query('SELECT id,creado_en,estado,total,items FROM pedidos WHERE uc_id=%s ORDER BY creado_en DESC LIMIT 200',(user_id,))
