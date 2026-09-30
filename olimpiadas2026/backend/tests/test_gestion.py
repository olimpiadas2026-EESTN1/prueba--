import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
import main
from modulos import compras, gestion

class GestionTests(unittest.TestCase):
    def test_protected_routes(self):
        client=TestClient(main.app)
        for path in ['/admin/resumen','/admin/usuarios','/admin/usuarios/1','/admin/pedidos','/admin/ventas','/admin/catalogo/viajes','/admin/auditoria','/clientes/mis-pedidos']:
            self.assertEqual(client.get(path).status_code,401,path)
        self.assertEqual(client.patch('/admin/datos/usuarios/1',json={'nombre':'X'}).status_code,401)
        self.assertEqual(client.post('/carrito',json={'items':[],'user':'another@example.test'}).status_code,401)

    def test_validation(self):
        for kind,data in [('usuarios',{'contraseña':'x'}),('viajes',{'cupos':-1}),('viajes',{'cupos':1.5}),('viajes',{'precio':'NaN'}),('viajes',{'estado':'inventado'})]:
            with self.assertRaises(HTTPException) as result:
                gestion.update(kind,1,data,{'id':1})
            self.assertEqual(result.exception.status_code,422)

    def test_checkout_price_and_owner(self):
        conn=MagicMock(); cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value={'codigo':7,'nombre':'Viaje','precio':100,'cupos':5,'estado':'Disponible'}
        sdk=MagicMock();sdk.preference.return_value.create.return_value={'status':201,'response':{'id':'pref','init_point':'https://www.mercadopago.com.ar/checkout'}}
        with patch.object(compras,'connection',return_value=conn):
            result=compras.checkout([SimpleNamespace(id=7,tipo='viaje',quantity=2,unit_price=1)],42,sdk)
        self.assertEqual(result['total'],200)
        payload=sdk.preference.return_value.create.call_args.args[0]
        self.assertEqual(payload['items'][0]['unit_price'],100)
        self.assertEqual(payload['external_reference'],result['pedido_id'])
        insert=[c for c in cur.execute.call_args_list if isinstance(c.args[0],str) and c.args[0].startswith('INSERT INTO pedidos')][0]
        self.assertEqual(insert.args[1][1],42)

    def test_stock_and_gateway_errors(self):
        conn=MagicMock();cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value={'nombre':'Demo','precio':100,'cupos':0,'estado':'Disponible'}
        sdk=MagicMock(); item=SimpleNamespace(id=1,tipo='viaje',quantity=1)
        with patch.object(compras,'connection',return_value=conn),self.assertRaises(HTTPException): compras.checkout([item],1,sdk)
        sdk.preference.assert_not_called()
        cur.fetchone.return_value['cupos']=1
        sdk.preference.return_value.create.side_effect=RuntimeError('offline')
        with patch.object(compras,'connection',return_value=conn),self.assertRaises(HTTPException) as error: compras.checkout([item],1,sdk)
        self.assertEqual(error.exception.status_code,502)
        self.assertIn('error_checkout',conn.__enter__.return_value.execute.call_args.args[0])

if __name__=='__main__': unittest.main()
