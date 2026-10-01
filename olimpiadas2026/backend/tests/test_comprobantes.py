import hashlib
import hmac
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
import main
from modulos.pagos import validate_payment, process_payment
from modulos.correos import compose, deliver_one
from roots.pagos import verify_signature

class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.order={'id':'d72906b4-f0c6-44ca-8d9b-d0ed9a148bfc','moneda':'ARS','total':100,'items':[{'title':'Viaje','quantity':1,'unit_price':100}]}
        self.payment={'id':123,'status':'approved','external_reference':self.order['id'],'currency_id':'ARS','transaction_amount':100,'collector_id':77}
        self.pref={'collector_id':77,'external_reference':self.order['id']}

    def test_payment_validation(self):
        self.assertTrue(validate_payment(self.payment,self.order,self.pref))
        for key,value in [('transaction_amount',1),('currency_id','USD'),('collector_id',99),('external_reference','other'),('transaction_amount_refunded',10)]:
            with self.assertRaises(HTTPException): validate_payment({**self.payment,key:value},self.order,self.pref)
        self.assertFalse(validate_payment({**self.payment,'status':'pending'},self.order,self.pref))

    def test_signature(self):
        digest=hmac.new(b'secret',b'id:123;request-id:req;ts:1234;',hashlib.sha256).hexdigest()
        verify_signature('123','req',f'ts=1234,v1={digest}','secret')
        with self.assertRaises(HTTPException): verify_signature('124','req',f'ts=1234,v1={digest}','secret')

    def test_receipt_test_label(self):
        subject,body=compose(self.order,'Cliente',123,False)
        self.assertIn('[PRUEBA]',subject)
        self.assertIn('sin validez como reserva real',body)
        self.assertNotIn('[PRUEBA]',compose(self.order,'Cliente',123,True)[0])

    def test_no_double_confirmation(self):
        sdk=MagicMock();sdk.payment.return_value.get.return_value={'status':200,'response':self.payment}
        conn=MagicMock();cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value={**self.order,'pago_id':'123'}
        with patch('modulos.pagos.connection',return_value=conn):
            self.assertEqual(process_payment(123,sdk),self.order['id'])
        self.assertEqual(cur.execute.call_count,1)
        sdk.preference.assert_not_called()

    def test_no_double_mail_and_missing_credentials(self):
        conn=MagicMock();cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value={'estado':'enviado'}
        with patch('modulos.correos.connection',return_value=conn),patch('modulos.gmail_api.build') as smtp:
            self.assertEqual(deliver_one(self.order['id'],'comprador'),'enviado');smtp.assert_not_called()
        cur.fetchone.return_value={'estado':'pendiente'}
        with patch('modulos.correos.connection',return_value=conn),patch.dict('os.environ',{'GMAIL_FROM':''}),patch('modulos.gmail_api.build') as smtp:
            self.assertEqual(deliver_one(self.order['id'],'comprador'),'error');smtp.assert_not_called()

    def test_gmail_api_transport(self):
        import base64
        from email import message_from_bytes
        from modulos.gmail_api import send_email
        with patch.dict('os.environ',{'GMAIL_FROM':'shop@example.com'}),patch('modulos.gmail_api.gmail_credentials'),patch('modulos.gmail_api.build') as build:
            service=build.return_value.__enter__.return_value
            send=service.users.return_value.messages.return_value.send
            send.return_value.execute.return_value={'id':'gmail-message'}
            self.assertEqual(send_email('buyer@example.com','Compra confirmada','Detalle del pedido','<pedido-prueba@airtrip.local>'),'gmail-message')
            self.assertEqual(send.call_args.kwargs['userId'],'me')
            message=message_from_bytes(base64.urlsafe_b64decode(send.call_args.kwargs['body']['raw']))
            self.assertEqual(message['To'],'buyer@example.com')
            self.assertEqual(message['From'],'shop@example.com')
            self.assertEqual(message['Message-ID'],'<pedido-prueba@airtrip.local>')
            send.return_value.execute.assert_called_once_with(num_retries=0)

    def test_gmail_missing_authorization(self):
        from modulos.gmail_api import gmail_credentials
        with patch('modulos.gmail_api.secret_path') as path:
            path.return_value.is_file.return_value=False
            with self.assertRaises(RuntimeError): gmail_credentials()

    def test_two_independent_deliveries(self):
        from modulos.correos import deliver, compose_admin
        with patch('modulos.correos.deliver_one',side_effect=['error','enviado']) as send:
            result=deliver(self.order['id'])
        self.assertEqual(result,{'comprador':'error','administrador':'enviado'})
        self.assertEqual(send.call_count,2)
        subject,body=compose_admin(self.order,{'nombre':'Cliente','correo_electronico':'cliente@example.test'},123,False)
        self.assertIn('Nueva venta',subject)
        self.assertIn('cliente@example.test',body)

    def test_private_retry_and_removed_unsafe_route(self):
        client=TestClient(main.app)
        self.assertEqual(client.get('/admin/correos').status_code,401)
        self.assertEqual(client.post('/admin/pagos/123/verificar').status_code,401)
        self.assertEqual(client.post('/ventas/confirmarMail',json={}).status_code,404)

if __name__=='__main__': unittest.main()
