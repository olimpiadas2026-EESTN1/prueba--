import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
import main
from modulos import estados_pedidos as estados

class EstadosTests(unittest.TestCase):
    def change(self, pago, actual, nuevo, esperado=None):
        conn=MagicMock()
        cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value={'estado':pago,'estado_gestion':actual}
        with patch.object(estados,'connection',return_value=conn):
            result=estados.cambiar('order',nuevo,esperado or actual,'Solicitud revisada',{'id':1})
        return result,cur

    def test_paid_order_records_history(self):
        result,cur=self.change('confirmado','pendiente','en_preparacion')
        self.assertTrue(result['ok'])
        self.assertIn('pedido_estados',cur.execute.call_args.args[0])
        self.assertEqual(cur.execute.call_args.args[1],('order',1,'pendiente','en_preparacion','Solicitud revisada'))

    def test_unpaid_cannot_be_prepared(self):
        with self.assertRaises(HTTPException) as error:
            self.change('pendiente_pago','pendiente','en_preparacion')
        self.assertEqual(error.exception.status_code,409)

    def test_conflict_and_invalid_transition(self):
        for actual,nuevo,esperado in [('listo','completado','en_preparacion'),('pendiente','completado','pendiente')]:
            with self.assertRaises(HTTPException):
                self.change('confirmado',actual,nuevo,esperado)

    def test_unpaid_can_be_reviewed(self):
        self.assertTrue(self.change('pendiente_pago','pendiente','en_revision')[0]['ok'])

    def test_auth_and_buyer_scope(self):
        client=TestClient(main.app)
        path='/admin/pedidos/00000000-0000-0000-0000-000000000001'
        self.assertEqual(client.patch(path+'/estado',json={'estado':'en_revision','estado_esperado':'pendiente','motivo':'Revisar'}).status_code,401)
        self.assertEqual(client.get(path+'/historial').status_code,401)
        from modulos.compras import require_buyer
        main.app.dependency_overrides[require_buyer]=lambda:42
        try:
            with patch('modulos.gestion.query',return_value=[]) as query:
                self.assertEqual(client.get('/clientes/mis-pedidos').status_code,200)
                self.assertIn('WHERE uc_id=%s',query.call_args.args[0])
                self.assertEqual(query.call_args.args[1],(42,))
        finally: main.app.dependency_overrides.pop(require_buyer,None)
