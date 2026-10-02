"""Correos transaccionales de registro y compra.

Resend necesita un dominio verificado para enviar a usuarios arbitrarios. Mientras
no exista ``RESEND_FROM`` con ese dominio, se usa la cuenta SMTP configurada en
Railway. Nunca se usa ``onboarding@resend.dev`` en produccion: ese remitente solo
sirve para pruebas con el dueño de la cuenta de Resend.
"""

import asyncio
import logging
import os
import smtplib
from email.message import EmailMessage

import resend


logger = logging.getLogger(__name__)


def _resend_disponible() -> bool:
    remitente = os.getenv("RESEND_FROM", "").strip()
    return bool(
        os.getenv("RESEND_API_KEY")
        and remitente
        and not remitente.endswith("@resend.dev")
    )


async def _enviar_resend(destinatario: str, asunto: str, cuerpo: str):
    resend.api_key = os.environ["RESEND_API_KEY"]
    return await resend.Emails.send_async(
        {
            "from": os.environ["RESEND_FROM"].strip(),
            "to": [destinatario],
            "subject": asunto,
            "text": cuerpo,
        }
    )


def _enviar_smtp(destinatario: str, asunto: str, cuerpo: str) -> None:
    usuario = os.getenv("MAIL_USERNAME", "").strip()
    password = os.getenv("MAIL_PASSWORD", "").strip()
    servidor = os.getenv("MAIL_SERVER", "smtp.gmail.com").strip()
    puerto = int(os.getenv("MAIL_PORT", "587"))
    remitente = os.getenv("MAIL_FROM", usuario).strip() or usuario

    faltantes = [
        nombre
        for nombre, valor in (("MAIL_USERNAME", usuario), ("MAIL_PASSWORD", password))
        if not valor
    ]
    if faltantes:
        raise RuntimeError("Faltan variables de correo: " + ", ".join(faltantes))

    mensaje = EmailMessage()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)

    with smtplib.SMTP(servidor, puerto, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(usuario, password)
        smtp.send_message(mensaje)


async def enviar_correo(destinatario: str, asunto: str, cuerpo: str):
    if _resend_disponible():
        resultado = await _enviar_resend(destinatario, asunto, cuerpo)
        logger.info("Correo aceptado por Resend para %s", destinatario)
        return resultado

    if os.getenv("RESEND_API_KEY"):
        logger.warning(
            "RESEND_FROM no tiene un dominio verificado; se utiliza SMTP para poder enviar a usuarios"
        )

    await asyncio.to_thread(_enviar_smtp, destinatario, asunto, cuerpo)
    logger.info("Correo aceptado por SMTP para %s", destinatario)
    return {"provider": "smtp", "accepted": True}


async def enviar_correo_registro(email_usuario: str, nombre_usuario: str):
    return await enviar_correo(
        email_usuario,
        "Registro exitoso - Olimpiadas 2026",
        f"""Hola {nombre_usuario}.

Tu cuenta fue registrada correctamente en Olimpiadas 2026.
Ya podés ingresar a nuestra plataforma.

Saludos,
Olimpiadas 2026
""",
    )


async def enviar_correo_compra(
    email_usuario: str, nombre_usuario: str, id_compra: str, monto: float
):
    return await enviar_correo(
        email_usuario,
        "Pago confirmado - Olimpiadas 2026",
        f"""Hola {nombre_usuario}.

Tu pago fue confirmado correctamente.
Número de pedido: {id_compra}
Monto abonado: ${monto:.2f}

Gracias por tu compra.
Olimpiadas 2026
""",
    )


async def enviar_correo_admin(id_compra: str, email_comprador: str, monto: float):
    admin_email = os.getenv("ADMIN_EMAIL", "").strip()
    if not admin_email:
        raise RuntimeError("ADMIN_EMAIL no está configurado")

    return await enviar_correo(
        admin_email,
        "Nueva compra confirmada - Olimpiadas 2026",
        f"""Se confirmó una nueva compra.

Número de pedido: {id_compra}
Comprador: {email_comprador}
Monto: ${monto:.2f}

Mercado Pago confirmó el pago.
Olimpiadas 2026
""",
    )
