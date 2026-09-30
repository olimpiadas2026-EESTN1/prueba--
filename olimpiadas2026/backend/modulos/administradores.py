"""Autenticación administrativa independiente (sesiones locales de 1 hora)."""
import secrets
import time
from threading import Lock
import bcrypt
from fastapi import Header, HTTPException

_sessions = {}
_lock = Lock()
_dummy_hash = bcrypt.hashpw(b'invalid-password', bcrypt.gensalt())


def authenticate(email, password):
    from main import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT ua_id, nombre, contraseña, correo_electronico FROM usuario_administrativo WHERE lower(correo_electronico) = %s', (email.strip().lower(),))
            row = cur.fetchone()
    stored = row[2] if row else _dummy_hash
    if isinstance(stored, str):
        stored = stored.encode()
    try:
        valid = bcrypt.checkpw(password.encode(), stored)
    except (ValueError, TypeError):
        valid = False
    if not row or not valid:
        raise HTTPException(401, 'Correo o contraseña incorrectos')
    admin = {'id': row[0], 'nombre': row[1], 'email': row[3], 'rol': 'administrador'}
    token = secrets.token_urlsafe(32)
    with _lock:
        now = time.time()
        for key in list(_sessions):
            if _sessions[key][1] <= now:
                del _sessions[key]
        _sessions[token] = (admin, now + 3600)
    return {'token': token, 'admin': admin, 'expires_in': 3600}


def require_admin(authorization: str = Header(default='')):
    token = authorization.removeprefix('Bearer ')
    with _lock:
        session = _sessions.get(token) if authorization.startswith('Bearer ') else None
        if not session or session[1] <= time.time():
            _sessions.pop(token, None)
            raise HTTPException(401, 'Iniciá sesión como administrador')
        return session[0]


def logout(authorization):
    with _lock:
        _sessions.pop(authorization.removeprefix('Bearer '), None)
