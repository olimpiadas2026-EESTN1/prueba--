import os

import resend


# ===============================
#       Configuración Resend
# ===============================

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not RESEND_API_KEY:
    raise RuntimeError("Falta la variable RESEND_API_KEY")

resend.api_key = RESEND_API_KEY


# ===============================
#       Función general
# ===============================

async def enviar_correo(
    destinatario: str,
    asunto: str,
    cuerpo: str
):
    try:
        params = {
            "from": "onboarding@resend.dev",
            "to": [destinatario],
            "subject": asunto,
            "text": cuerpo,
        }

        resultado = await resend.Emails.send_async(params)

        print(
            f"CORREO ENVIADO CORRECTAMENTE: {resultado}"
        )

        return resultado

    except Exception as e:
        print(
            f"ERROR ENVIANDO CORREO: {e}"
        )
        raise


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
#       CORREO AL ADMIN
# ===============================

async def enviar_correo_admin(
    id_compra: str,
    email_comprador: str,
    monto: float
):
    admin_email = os.getenv("ADMIN_EMAIL")

    if not admin_email:
        print("ADMIN_EMAIL no está configurado")
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