import unittest
from unittest.mock import MagicMock,patch
from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.testclient import TestClient
import main
from modulos import circuito

class CircuitoTests(unittest.TestCase):
    def order(self,**kwargs):
        return dict(id='00000000-0000-0000-0000-000000000001',uc_id=2,estado='creado',estado_gestion='pendiente',anulado_en=None,checkout_iniciado=False,preferencia_id=None,pago_id=None,version=1,total=100,items=[],**kwargs)
    def db(self):
        conn=MagicMock();cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        return conn,cur
    def test_owner_filter(self):
        cur=MagicMock();cur.fetchone.return_value=None
        with self.assertRaises(HTTPException) as e: circuito.bloquear(cur,'id',8)
        self.assertEqual(e.exception.status_code,404)
        self.assertEqual(cur.execute.call_args.args[1],('id',8,8))
    def test_checkout_locks_edits(self):
        for key,value in [('checkout_iniciado',True),('preferencia_id','pref'),('pago_id','pay'),('estado_gestion','completado')]:
            order=self.order();order[key]=value
            with self.assertRaises(HTTPException): circuito.editable(order)
    def test_quote_ignores_browser_price_and_caps_aggregate(self):
        cur=MagicMock();cur.fetchone.return_value={'nombre':'Test','precio':100,'cupos':100,'estado':'Disponible'}
        items=[SimpleNamespace(tipo='viaje',id=1,quantity=2,unit_price=1)]
        self.assertEqual(circuito.cotizar(cur,items)[1],200)
        with self.assertRaises(HTTPException): circuito.cotizar(cur,[SimpleNamespace(tipo='viaje',id=1,quantity=30)]*2)
    def test_auto_quote_uses_server_daily_price_and_dates(self):
        from datetime import date
        cur=MagicMock();cur.fetchone.side_effect=[{'modelo':'Sedan','disponibles':3,'precio_por_dia':100},{'reservados':1}]
        item=SimpleNamespace(tipo='auto',id=4,quantity=2,fecha_retiro=date(2026,10,5),fecha_devolucion=date(2026,10,8))
        snapshot,total=circuito.cotizar(cur,[item])
        self.assertEqual(total,600)
        self.assertEqual(snapshot[0]['unit_price'],300)
        self.assertEqual(snapshot[0]['precio_diario'],100)
        self.assertEqual(snapshot[0]['fecha_retiro'],'2026-10-05')
        self.assertEqual(snapshot[0]['fecha_devolucion'],'2026-10-08')
    def test_auto_quote_requires_dates_and_availability(self):
        from datetime import date
        with self.assertRaises(HTTPException): circuito.cotizar(MagicMock(),[SimpleNamespace(tipo='auto',id=4,quantity=1)])
        cur=MagicMock();cur.fetchone.side_effect=[{'modelo':'Sedan','disponibles':1,'precio_por_dia':100},{'reservados':1}]
        item=SimpleNamespace(tipo='auto',id=4,quantity=1,fecha_retiro=date(2026,10,5),fecha_devolucion=date(2026,10,6))
        with self.assertRaises(HTTPException) as error: circuito.cotizar(cur,[item])
        self.assertEqual(error.exception.status_code,409)
    def test_edit_conflict(self):
        conn,cur=self.db();cur.fetchone.return_value=self.order()
        with patch.object(circuito,'connection',return_value=conn),self.assertRaises(HTTPException) as e:
            circuito.modificar('id',[],2,2)
        self.assertEqual(e.exception.status_code,409)
        self.assertEqual(cur.execute.call_count,1)
    def test_no_unpaid_delivery(self):
        conn,cur=self.db();cur.fetchone.return_value=self.order()
        with patch.object(circuito,'connection',return_value=conn),self.assertRaises(HTTPException): circuito.entregar('id','Entrega',{'id':1})
        self.assertEqual(cur.execute.call_count,1)
    def test_delivery_history_atomic(self):
        conn,cur=self.db();order=self.order();order.update(estado='confirmado',estado_gestion='listo')
        cur.fetchone.side_effect=[order,None,None]
        with patch.object(circuito,'connection',return_value=conn): circuito.entregar('id','Voucher entregado',{'id':1})
        statements=[c.args[0] for c in cur.execute.call_args_list]
        self.assertTrue(any('INSERT INTO pedidos_entregados' in s for s in statements))
        self.assertTrue(any('INSERT INTO admin_auditoria' in s for s in statements))
    def test_delivery_duplicate_or_request_blocks(self):
        for replies in [[{'id':1}],[None,{'id':1}]]:
            conn,cur=self.db();order=self.order();order.update(estado='confirmado',estado_gestion='listo')
            cur.fetchone.side_effect=[order]+replies
            with patch.object(circuito,'connection',return_value=conn),self.assertRaises(HTTPException): circuito.entregar('id','Voucher',{'id':1})
    def test_private_endpoints(self):
        client=TestClient(main.app);id='00000000-0000-0000-0000-000000000001'
        for path in ['/admin/cuenta-corriente','/admin/entregados','/admin/configuracion-empresa','/admin/solicitudes','/clientes/solicitudes']:
            self.assertEqual(client.get(path).status_code,401)
        for path in [f'/admin/pedidos/{id}/entregar',f'/admin/pedidos/{id}/anular',f'/clientes/pedidos/{id}/anular',f'/clientes/pedidos/{id}/pagar']:
            self.assertEqual(client.post(path,json={'motivo':'test'}).status_code,401)
    def test_cancel_not_archive(self):
        conn,cur=self.db();cur.fetchone.return_value=self.order()
        with patch.object(circuito,'connection',return_value=conn): circuito.anular('id','Ya no viajo',user_id=2)
        statement=cur.execute.call_args.args[0]
        self.assertIn('anulado_en=now()',statement)
        self.assertNotIn('eliminado_en=',statement)
