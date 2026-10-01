"""Operaciones del comprador y de ventas, con permisos separados."""
from uuid import UUID
from typing import Literal, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from modulos.compras import require_buyer
from modulos.administradores import require_admin
from modulos import circuito
from modulos.gestion import query

router=APIRouter(tags=['Circuito comercial'])
class Articulo(BaseModel):
    tipo: Literal['viaje','paquete']
    id: int = Field(gt=0)
    quantity: int = Field(gt=0,le=50)
class Pedido(BaseModel):
    items: List[Articulo] = Field(min_length=1,max_length=100)
class Edicion(Pedido):
    version: int = Field(gt=0)
class Motivo(BaseModel):
    motivo: str = Field(min_length=1,max_length=1000)
class Solicitud(BaseModel):
    tipo: Literal['modificacion','anulacion']
    detalle: str = Field(min_length=1,max_length=1000)
class Respuesta(BaseModel):
    estado: Literal['resuelta','rechazada']
    respuesta: str = Field(min_length=1,max_length=1000)
class Correo(BaseModel):
    correo_ventas: str = Field(min_length=3,max_length=254)

@router.post('/clientes/pedidos')
def crear(data: Pedido,user=Depends(require_buyer)):
    return circuito.crear(data.items,user)
@router.patch('/clientes/pedidos/{id}')
def modificar(id: UUID,data: Edicion,user=Depends(require_buyer)):
    return circuito.modificar(id,data.items,data.version,user)
@router.post('/clientes/pedidos/{id}/anular')
def anular(id: UUID,data: Motivo,user=Depends(require_buyer)):
    return circuito.anular(id,data.motivo,user_id=user)
@router.post('/clientes/pedidos/{id}/pagar')
def pagar(id: UUID,user=Depends(require_buyer)):
    from main import mp_sdk
    return circuito.pagar(id,user,mp_sdk)
@router.post('/clientes/pedidos/{id}/solicitudes')
def solicitar(id: UUID,data: Solicitud,user=Depends(require_buyer)):
    return circuito.solicitar(id,data.tipo,data.detalle,user)
@router.get('/clientes/solicitudes')
def propias(user=Depends(require_buyer)):
    return query('SELECT id,pedido_id,tipo,detalle,estado,respuesta,creado_en FROM solicitudes_pedido WHERE uc_id=%s ORDER BY id DESC LIMIT 200',(user,))
@router.post('/admin/pedidos/{id}/entregar')
def entregar(id: UUID,data: Motivo,admin=Depends(require_admin)):
    return circuito.entregar(id,data.motivo,admin)
@router.post('/admin/pedidos/{id}/anular')
def cancelar(id: UUID,data: Motivo,admin=Depends(require_admin)):
    return circuito.anular(id,data.motivo,admin=admin)
@router.get('/admin/entregados')
def entregados(admin=Depends(require_admin)):
    return query('SELECT * FROM pedidos_entregados ORDER BY entregado_en DESC LIMIT 200')
@router.get('/admin/pendientes-entrega')
def pendientes(admin=Depends(require_admin)):
    return query("SELECT id,uc_id,creado_en,total,estado,estado_gestion FROM pedidos WHERE anulado_en IS NULL AND eliminado_en IS NULL AND NOT EXISTS(SELECT 1 FROM pedidos_entregados h WHERE h.pedido_id=pedidos.id) ORDER BY creado_en LIMIT 200")
@router.get('/admin/cuenta-corriente')
def cuenta(orden: Literal['fecha','cliente']='fecha',solo_pendientes: bool=True,admin=Depends(require_admin)):
    return circuito.cuenta(orden,solo_pendientes)
@router.get('/admin/solicitudes')
def solicitudes(admin=Depends(require_admin)):
    return query('SELECT * FROM solicitudes_pedido ORDER BY creado_en DESC LIMIT 200')
@router.patch('/admin/solicitudes/{id}')
def responder(id: int,data: Respuesta,admin=Depends(require_admin)):
    return circuito.resolver(id,data.estado,data.respuesta,admin)
@router.get('/admin/configuracion-empresa')
def config(admin=Depends(require_admin)):
    return query('SELECT correo_ventas,actualizado_en FROM configuracion_empresa WHERE id=1')
@router.put('/admin/configuracion-empresa')
def save_config(data: Correo,admin=Depends(require_admin)):
    return circuito.guardar_correo(data.correo_ventas,admin)
