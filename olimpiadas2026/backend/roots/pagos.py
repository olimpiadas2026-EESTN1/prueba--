import os
import hashlib
import hmac
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from modulos.administradores import require_admin
from modulos.pagos import process_payment
from modulos.correos import deliver
from modulos.gestion import query

router=APIRouter(tags=['Pagos y comprobantes'])


def verify_signature(payment_id,request_id,signature,secret):
    if not secret: raise HTTPException(503,'Falta configurar el secreto del webhook')
    parts=dict(part.strip().split('=',1) for part in signature.split(',') if '=' in part)
    ts=parts.get('ts',''); received=parts.get('v1','')
    if not payment_id.isdigit() or not request_id or not ts.isdigit() or not received:
        raise HTTPException(401,'Firma inválida')
    manifest=f'id:{payment_id};request-id:{request_id};ts:{ts};'
    expected=hmac.new(secret.encode(),manifest.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,received): raise HTTPException(401,'Firma inválida')


@router.post('/webhooks/mercadopago')
def webhook(request: Request, background: BackgroundTasks):
    payment_id=request.query_params.get('data.id','')
    verify_signature(payment_id,request.headers.get('x-request-id',''),request.headers.get('x-signature',''),os.getenv('MERCADOPAGO_WEBHOOK_SECRET',''))
    from main import mp_sdk
    order_id=process_payment(payment_id,mp_sdk)
    if order_id: background.add_task(deliver,order_id)
    return {'ok':True}


@router.post('/admin/pagos/{payment_id}/verificar')
def reconcile(payment_id: int, background: BackgroundTasks, admin=Depends(require_admin)):
    from main import mp_sdk
    order_id=process_payment(payment_id,mp_sdk)
    if order_id: background.add_task(deliver,order_id)
    return {'pedido_id':order_id,'confirmado':bool(order_id)}


@router.get('/admin/correos')
def emails(admin=Depends(require_admin)):
    return query('SELECT pedido_id,tipo,destinatario,estado,intentos,enviado_en,ultimo_error FROM correos_compra ORDER BY enviado_en DESC NULLS FIRST LIMIT 200')


@router.post('/admin/correos/{order_id}/reintentar')
def retry(order_id: UUID, admin=Depends(require_admin)):
    return {'estado':deliver(str(order_id))}
