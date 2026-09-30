"""Crear un administrador explícitamente desde la terminal, nunca desde registro público."""
from getpass import getpass
import bcrypt
from main import get_connection

if __name__ == '__main__':
    nombre = input('Nombre: ').strip()
    apellido = input('Apellido: ').strip()
    email = input('Correo: ').strip().lower()
    password = getpass('Contraseña (mínimo 12 caracteres): ')
    if not nombre or not apellido or '@' not in email:
        raise SystemExit('Nombre, apellido y correo son obligatorios')
    if len(password) < 12 or len(password.encode()) > 72 or password != getpass('Repetir contraseña: '):
        raise SystemExit('Contraseña inválida o confirmación diferente')
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('LOCK TABLE usuario_administrativo IN SHARE ROW EXCLUSIVE MODE')
            cur.execute('SELECT 1 FROM usuario_administrativo WHERE lower(correo_electronico) = %s', (email,))
            if cur.fetchone():
                raise SystemExit('Ya existe ese administrador')
            cur.execute('SELECT COALESCE(MAX(ua_id), 0) + 1 FROM usuario_administrativo')
            next_id = cur.fetchone()[0]
            cur.execute('INSERT INTO usuario_administrativo (ua_id,nombre,apellido,contraseña,correo_electronico) VALUES (%s,%s,%s,%s,%s)', (next_id,nombre,apellido,hashed,email))
    print('Administrador creado')
