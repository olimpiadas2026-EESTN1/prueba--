# ===============================
#       Configuración de correo
# ===============================

import os
from pathlib import Path

from dotenv import load_dotenv

from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig
)


# ===============================
#       Cargar .env
# ===============================

BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ===============================
#       Configuración SMTP
# ===============================

def crear_configuracion():
    valores = {
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
        "MAIL_FROM": os.getenv("MAIL_FROM"),
        "MAIL_SERVER": os.getenv("MAIL_SERVER"),
    }

    faltantes = [nombre for nombre, valor in valores.items() if not valor]
    if faltantes:
        raise RuntimeError(
            "Faltan variables de correo: " + ", ".join(faltantes)
        )

    return ConnectionConfig(
        **valores,
        MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )


# ===============================
#       Función general
# ===============================

async def enviar_correo(
    destinatario: str,
    asunto: str,
    cuerpo: str
):

    mensaje = MessageSchema(
        subject=asunto,
        recipients=[destinatario],
        body=cuerpo,
        subtype="plain"
    )

    mail = FastMail(crear_configuracion())

    await mail.send_message(
        mensaje
    )


# ===============================
#       CORREO DE REGISTRO
# ===============================

async def enviar_correo_registro(
    email_usuario: str,
    nombre_usuario: str
):

    await enviar_correo(

        destinatario=email_usuario,

        asunto="Registro exitoso - Olimpiadas 2026",

        cuerpo=f"""
Hola {nombre_usuario}.

Tu cuenta fue registrada correctamente
en Olimpiadas 2026.

Ya podés ingresar a nuestra plataforma.

Saludos,

Olimpiadas 2026
"""
    )


# ===============================
#       CORREO DE COMPRA
#       AL USUARIO
# ===============================

async def enviar_correo_compra(
    email_usuario: str,
    nombre_usuario: str,
    id_compra: str,
    monto: float
):

    await enviar_correo(

        destinatario=email_usuario,

        asunto="Pago confirmado - Olimpiadas 2026",

        cuerpo=f"""
Hola {nombre_usuario}.

Tu pago fue confirmado correctamente.

Número de pedido:
{id_compra}

Monto abonado:
${monto:.2f}

Gracias por tu compra.

Saludos,

Olimpiadas 2026
"""
    )


# ===============================
#       CORREO DE COMPRA
#       AL ADMINISTRADOR
# ===============================

async def enviar_correo_admin(
    id_compra: str,
    email_comprador: str,
    monto: float
):

    admin_email = os.getenv(
        "ADMIN_EMAIL"
    )


    if not admin_email:

        print(
            "ADMIN_EMAIL no está configurado"
        )

        return


    await enviar_correo(

        destinatario=admin_email,

        asunto="Nueva compra confirmada - Olimpiadas 2026",

        cuerpo=f"""
Se confirmó una nueva compra.

Número de pedido:
{id_compra}

Comprador:
{email_comprador}

Monto:
${monto:.2f}

Mercado Pago confirmó el pago.

Olimpiadas 2026
"""
    )
