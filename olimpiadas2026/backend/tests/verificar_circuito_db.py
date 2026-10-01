"""Prueba optativa contra PostgreSQL, siempre en una transacción revertida.
Ejecutar desde backend: .venv/bin/python tests/verificar_circuito_db.py
No llama a Mercado Pago ni a Gmail. No confirma pagos reales.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contextlib import contextmanager
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import main
from modulos import circuito,gestion,pagos

conn=main.get_connection()
@contextmanager
def local_connection():
    with conn.transaction():
        yield conn

try:
    conn.execute("SET LOCAL statement_timeout='15s'")
    user=conn.execute('SELECT uc_id FROM usuario_comun WHERE eliminado_en IS NULL LIMIT 1').fetchone()
    admin=conn.execute('SELECT ua_id FROM usuario_administrativo LIMIT 1').fetchone()
    product=conn.execute("SELECT codigo FROM viaje_simple WHERE eliminado_en IS NULL AND cupos>=2 AND estado='Disponible' LIMIT 1").fetchone()
    assert user and admin and product, 'Requiere comprador, administrador y viaje disponible'
    with patch.object(circuito,'connection',local_connection),patch.object(gestion,'connection',local_connection),patch.object(pagos,'connection',local_connection):
        items=[SimpleNamespace(tipo='viaje',id=product[0],quantity=1)]
        order=circuito.crear(items,user[0])['pedido_id']
        assert conn.execute('SELECT count(*) FROM pedido_articulos WHERE pedido_id=%s',(order,)).fetchone()[0]==1
        items[0].quantity=2
        circuito.modificar(order,items,1,user[0])
        total=conn.execute('SELECT total FROM pedidos WHERE id=%s',(order,)).fetchone()[0]
        assert conn.execute('SELECT cantidad FROM pedido_articulos WHERE pedido_id=%s',(order,)).fetchone()[0]==2
        assert conn.execute('SELECT importe FROM facturas_internas WHERE pedido_id=%s',(order,)).fetchone()[0]==total
        circuito.anular(order,'Prueba transaccional',user_id=user[0])
        assert not any(str(r['pedido_id'])==order for r in circuito.cuenta())
        delivered=circuito.crear(items,user[0])['pedido_id']
        # Proveedor simulado solo para este registro efímero, revertido al finalizar.
        conn.execute("UPDATE pedidos SET preferencia_id=%s WHERE id=%s",('test-'+delivered,delivered))
        sdk=MagicMock(); payment_id='test-'+delivered
        sdk.payment.return_value.get.return_value={'status':200,'response':{'id':payment_id,'status':'approved','external_reference':delivered,'currency_id':'ARS','transaction_amount':float(total),'collector_id':77,'live_mode':False}}
        sdk.preference.return_value.get.return_value={'status':200,'response':{'collector_id':77,'external_reference':delivered}}
        assert pagos.process_payment(payment_id,sdk)==delivered
        assert pagos.process_payment(payment_id,sdk)==delivered
        assert conn.execute('SELECT count(*) FROM correos_compra WHERE pedido_id=%s',(delivered,)).fetchone()[0]==2
        assert conn.execute('SELECT count(*) FROM pedido_ventas WHERE pedido_id=%s',(delivered,)).fetchone()[0]==1
        conn.execute("UPDATE pedidos SET estado_gestion='listo' WHERE id=%s",(delivered,))
        circuito.entregar(delivered,'Entrega simulada en transacción revertida',{'id':admin[0]})
        assert conn.execute('SELECT count(*) FROM pedidos_entregados WHERE pedido_id=%s',(delivered,)).fetchone()[0]==1
        assert conn.execute('SELECT estado_gestion FROM pedidos WHERE id=%s',(delivered,)).fetchone()[0]=='completado'
        assert isinstance(circuito.cuenta('cliente',False),list)
    print('OK: detalle, edición, importe, anulación, entrega e histórico. Sin pagos ni correos.')
finally:
    conn.rollback()
    conn.close()
    print('Transacción revertida: no se conservaron pedidos de prueba.')
