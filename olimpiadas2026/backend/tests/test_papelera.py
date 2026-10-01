import time
import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
import main
from modulos import papelera, compras, gestion

class PapeleraTests(unittest.TestCase):
    def fixture(self, deleted=None):
        conn=MagicMock()
        cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value={'eliminado_en':deleted}
        return conn,cur

    def test_delete_and_restore_all_entities_audited(self):
        for kind in papelera.ENTIDADES:
            key='00000000-0000-0000-0000-000000000001' if kind=='pedidos' else '7'
            for restoring in (False,True):
                conn,cur=self.fixture('date' if restoring else None)
                with patch.object(papelera,'connection',return_value=conn):
                    result=papelera.cambiar(kind,key,' Prueba ',{'id':1},restoring)
                self.assertTrue(result['ok'])
                self.assertEqual(cur.execute.call_count,3)
                self.assertIn('UPDATE',cur.execute.call_args_list[1].args[0].as_string())
                self.assertEqual(cur.execute.call_args.args[1][:3],(1,kind,key))
                self.assertEqual(cur.execute.call_args.args[1][3].obj['motivo'],'Prueba')

    def test_invalid_and_conflicting_operations(self):
        for kind,key,motivo in [('unknown','1','ok'),('pedidos','invalid','ok'),('usuarios','-1','ok'),('usuarios','1','  ')]:
            with patch.object(papelera,'connection') as connection,self.assertRaises(HTTPException):
                papelera.cambiar(kind,key,motivo,{'id':1})
            connection.assert_not_called()
        conn,cur=self.fixture('date')
        with patch.object(papelera,'connection',return_value=conn),self.assertRaises(HTTPException) as error:
            papelera.cambiar('ventas','1','ok',{'id':1})
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(cur.execute.call_count,1)

    def test_missing_row(self):
        conn,cur=self.fixture();cur.fetchone.return_value=None
        with patch.object(papelera,'connection',return_value=conn),self.assertRaises(HTTPException) as error:
            papelera.cambiar('ventas','1','ok',{'id':1})
        self.assertEqual(error.exception.status_code,404)

    def test_user_sessions_revoked(self):
        conn,cur=self.fixture()
        compras._sessions['deleted-user']=(7,time.time()+60)
        compras._sessions['other-user']=(8,time.time()+60)
        try:
            with patch.object(papelera,'connection',return_value=conn):
                papelera.cambiar('usuarios','7','Baja',{'id':1})
            self.assertNotIn('deleted-user',compras._sessions)
            self.assertIn('other-user',compras._sessions)
        finally: compras._sessions.clear()

    def test_other_worker_session_checks_db(self):
        conn=MagicMock();conn.__enter__.return_value.execute.return_value.fetchone.return_value=None
        compras._sessions['stale']=(7,time.time()+60)
        with patch.object(compras,'connection',return_value=conn),self.assertRaises(HTTPException) as error:
            compras.require_buyer('Bearer stale')
        self.assertEqual(error.exception.status_code,401)
        self.assertNotIn('stale',compras._sessions)

    def test_routes_require_admin(self):
        client=TestClient(main.app)
        for kind in papelera.ENTIDADES:
            self.assertEqual(client.request('DELETE',f'/admin/datos/{kind}/1',json={'motivo':'Prueba'}).status_code,401)
            self.assertEqual(client.post(f'/admin/datos/{kind}/1/restaurar',json={'motivo':'Prueba'}).status_code,401)

    def test_checkout_excludes_deleted_products(self):
        from types import SimpleNamespace
        conn,cur=self.fixture();cur.fetchone.return_value=None
        sdk=MagicMock()
        with patch.object(compras,'connection',return_value=conn),self.assertRaises(HTTPException):
            compras.checkout([SimpleNamespace(tipo='viaje',id=1,quantity=1)],7,sdk)
        self.assertIn('eliminado_en IS NULL',cur.execute.call_args.args[0].as_string())
        sdk.preference.assert_not_called()

    def test_trash_filters(self):
        with patch.object(gestion,'query',return_value=[]) as query:
            gestion.orders(eliminados=True)
            self.assertEqual(query.call_args.args[1][:2],(True,True))
            gestion.users(eliminados=False)
            self.assertEqual(query.call_args.args[1][-1],False)
