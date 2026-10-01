from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from modulos.administradores import authenticate, require_admin, logout

router = APIRouter(prefix='/admin', tags=['Administración'])

class LoginAdmin(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=72)

@router.post('/login')
def login(data: LoginAdmin):
    try:
        return authenticate(data.email, data.password)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, 'No se pudo validar la cuenta administrativa')

@router.get('/me')
def me(admin=Depends(require_admin)):
    return admin

@router.post('/logout')
def close_session(admin=Depends(require_admin), authorization: str = Header(default='')):
    logout(authorization)
    return {'ok': True}

from modulos import gestion
from typing import Any
from fastapi import Query

@router.get('/resumen')
def overview(admin=Depends(require_admin)):
    return gestion.summary()

@router.get('/usuarios')
def users(q: str = Query(default='', max_length=100), eliminados: bool = False, admin=Depends(require_admin)):
    return gestion.users(q, eliminados)

@router.get('/usuarios/{user_id}')
def user_profile(user_id: int, admin=Depends(require_admin)):
    return gestion.profile(user_id)

@router.get('/pedidos')
def orders(usuario_id: int = None, eliminados: bool = False, admin=Depends(require_admin)):
    return gestion.orders(usuario_id, eliminados)

@router.get('/ventas')
def sales(usuario_id: int = None, eliminados: bool = False, admin=Depends(require_admin)):
    return gestion.sales(usuario_id, eliminados)

@router.get('/catalogo/{kind}')
def catalog(kind: str, eliminados: bool = False, admin=Depends(require_admin)):
    return gestion.catalog(kind, eliminados)

@router.patch('/datos/{kind}/{key}')
def edit(kind: str, key: int, changes: dict[str, Any], admin=Depends(require_admin)):
    return gestion.update(kind,key,changes,admin)

@router.get('/auditoria')
def audit(admin=Depends(require_admin)):
    return gestion.query('SELECT id,ua_id,creado_en,entidad,registro_id,cambios FROM admin_auditoria ORDER BY id DESC LIMIT 200')

from uuid import UUID
from typing import Literal
from modulos.estados_pedidos import cambiar

class EstadoPedido(BaseModel):
    estado: Literal['pendiente','en_preparacion','listo','completado','en_revision']
    estado_esperado: str
    motivo: str = Field(min_length=1, max_length=500)

@router.patch('/pedidos/{order_id}/estado')
def change_order_state(order_id: UUID, data: EstadoPedido, admin=Depends(require_admin)):
    return cambiar(order_id, data.estado, data.estado_esperado, data.motivo, admin)

@router.get('/pedidos/{order_id}/historial')
def order_history(order_id: UUID, admin=Depends(require_admin)):
    return gestion.query('SELECT anterior,nuevo,motivo,ua_id,creado_en FROM pedido_estados WHERE pedido_id=%s ORDER BY id DESC', (order_id,))

class MotivoBaja(BaseModel):
    motivo: str = Field(min_length=1, max_length=500)

@router.delete('/datos/{kind}/{key}')
def delete_record(kind: str, key: str, data: MotivoBaja, admin=Depends(require_admin)):
    from modulos.papelera import cambiar
    return cambiar(kind, key, data.motivo, admin)

@router.post('/datos/{kind}/{key}/restaurar')
def restore_record(kind: str, key: str, data: MotivoBaja, admin=Depends(require_admin)):
    from modulos.papelera import cambiar
    return cambiar(kind, key, data.motivo, admin, restaurar=True)
