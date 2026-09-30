import time
import unittest
from unittest.mock import patch, MagicMock
import bcrypt
from fastapi.testclient import TestClient
import main
from modulos import administradores as auth

class AdminTests(unittest.TestCase):
    def setUp(self):
        auth._sessions.clear()
        self.client = TestClient(main.app)

    def test_protected_routes(self):
        for path in ['/ventas/obtener', '/clientes/obtener', '/admin/me']:
            self.assertEqual(self.client.get(path).status_code, 401)
        for path in ['/viajes/ingresar', '/autos/eliminar', '/paqueteDeViajes/ingresar', '/excursiones/ingresar', '/ventas/ingresar']:
            self.assertEqual(self.client.post(path, json={}).status_code, 401)
        self.assertEqual(self.client.get('/admin/me', headers={'Authorization': 'Bearer true'}).status_code,401)

    def test_login_logout_and_expiry(self):
        conn = MagicMock()
        conn.__enter__.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = (1, 'Admin', bcrypt.hashpw(b'correct-password', bcrypt.gensalt()).decode(), 'admin@example.test')
        with patch.object(main, 'get_connection', return_value=conn):
            self.assertEqual(self.client.post('/admin/login',json={'email':'admin@example.test','password':'wrong'}).status_code,401)
            response=self.client.post('/admin/login',json={'email':'admin@example.test','password':'correct-password'})
        self.assertEqual(response.status_code,200)
        token=response.json()['token']; headers={'Authorization':f'Bearer {token}'}
        self.assertEqual(self.client.get('/admin/me',headers=headers).status_code,200)
        self.assertEqual(self.client.post('/admin/logout',headers=headers).status_code,200)
        self.assertEqual(self.client.get('/admin/me',headers=headers).status_code,401)
        auth._sessions[token]=({'id':1},time.time()-1)
        self.assertEqual(self.client.get('/admin/me',headers=headers).status_code,401)

    def test_no_public_admin_login_alias(self):
        self.assertEqual(self.client.post('/clientes/validarContrasenaAdmin', json={}).status_code,404)
        self.assertEqual(self.client.get('/health').status_code,200)

if __name__ == '__main__':
    unittest.main()
