import os
from pathlib import Path
from typing import List, Literal

from roots.circuito import router as circuito_router
from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Depends,
    Request
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

import mercadopago
import psycopg


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

app = FastAPI()


# ============================================================
# MERCADO PAGO
# ============================================================

MERCADOPAGO_TOKEN = os.getenv(
    "MERCADOPAGO_TOKEN"
)

mp_sdk = (
    mercadopago.SDK(
        MERCADOPAGO_TOKEN
    )
    if MERCADOPAGO_TOKEN
    else None
)


# ============================================================
# MODELOS
# ============================================================

class ItemCarrito(BaseModel):

    id: int = Field(
        gt=0
    )

    tipo: Literal[
        "viaje",
        "paquete"
    ]

    quantity: int = Field(
        gt=0,
        le=50
    )


class Carrito(BaseModel):

    items: List[
        ItemCarrito
    ]


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# BASE DE DATOS
# ============================================================

DATABASE_PASSWORD = os.getenv(
    "DATABASE_PASSWORD"
)


hostURL = (
    f"postgresql://postgres.dncdqfmfixojxprdlbkf:{DATABASE_PASSWORD}"
    "@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)


def get_connection():

    return psycopg.connect(
        hostURL
    )


# ============================================================
# CORREOS
# ============================================================

from correo import (
    enviar_correo_compra,
    enviar_correo_admin
)


# ============================================================
# ROUTERS
# ============================================================

from roots.autos import (
    router as autos_routers
)

from roots.clientes import (
    router as clientes_routers
)

from roots.paqueteDeViajes import (
    router as paqueteDeViajes_routers
)

from roots.ventas import (
    router as ventas_routers
)

from roots.viajes import (
    router as viajes_routers
)

from roots.administradores import (
    router as admin_router
)


# ============================================================
# REGISTRO DE ROUTERS
# ============================================================

app.include_router(
    admin_router
)

app.include_router(
    autos_routers,
    prefix="/autos"
)

app.include_router(
    clientes_routers,
    prefix="/clientes"
)

app.include_router(
    paqueteDeViajes_routers,
    prefix="/paqueteDeViajes"
)

app.include_router(
    ventas_routers,
    prefix="/ventas"
)

app.include_router(
    viajes_routers,
    prefix="/viajes"
)

# IMPORTANTE:
# circuito.py ya define rutas como:
# /clientes/pedidos
# por eso NO usamos prefix="/clientes" acá.
app.include_router(
    circuito_router
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {

        "status": "ok",

        "mercadopago_configurado":
            bool(mp_sdk),

        "database_configurada":
            bool(DATABASE_PASSWORD)

    }


# ============================================================
# CREAR CHECKOUT
# ============================================================

from modulos.compras import (
    require_buyer,
    checkout
)


@app.post("/carrito")
def post_carrito(
    carrito: Carrito,
    user_id=Depends(
        require_buyer
    )
):

    return checkout(
        carrito.items,
        user_id,
        mp_sdk
    )


# ============================================================
# WEBHOOK MERCADO PAGO
# ============================================================

@app.post(
    "/webhook/mercadopago"
)
async def webhook_mercadopago(
    request: Request
):

    try:

        # ====================================================
        # LEER BODY
        # ====================================================

        try:

            data = await request.json()

        except Exception:

            print(
                "Webhook recibido sin JSON válido."
            )

            return {
                "status": "invalid_json"
            }


        print()
        print(
            "========================================"
        )
        print(
            "WEBHOOK MERCADO PAGO"
        )
        print(
            "========================================"
        )
        print(
            "DATA:",
            data
        )
        print(
            "========================================"
        )
        print()


        # ====================================================
        # VERIFICAR TIPO
        # ====================================================

        if data.get("type") != "payment":

            print(
                "Notificación ignorada:",
                data.get("type")
            )

            return {
                "status": "ignored"
            }


        # ====================================================
        # PAYMENT ID
        # ====================================================

        payment_id = (
            data
            .get("data", {})
            .get("id")
        )


        if not payment_id:

            print(
                "No se recibió payment_id."
            )

            return {
                "status": "no_payment_id"
            }


        # ====================================================
        # VERIFICAR SDK
        # ====================================================

        if mp_sdk is None:

            print(
                "Mercado Pago no está configurado."
            )

            return {
                "status":
                    "mercadopago_not_configured"
            }


        # ====================================================
        # CONSULTAR PAGO EN MERCADO PAGO
        # ====================================================

        print(
            "Consultando pago:",
            payment_id
        )


        payment_response = (
            mp_sdk
            .payment()
            .get(payment_id)
        )


        payment = payment_response.get(
            "response",
            {}
        )


        status = payment.get(
            "status"
        )


        print(
            "PAYMENT ID:",
            payment_id
        )

        print(
            "PAYMENT STATUS:",
            status
        )


        # ====================================================
        # SOLO PAGOS APROBADOS
        # ====================================================

        if status != "approved":

            print(
                "Pago todavía no aprobado:",
                status
            )

            return {

                "status":
                    "payment_not_approved",

                "payment_status":
                    status

            }


        # ====================================================
        # EXTERNAL REFERENCE
        # ====================================================

        order_id = payment.get(
            "external_reference"
        )


        if not order_id:

            print(
                "El pago no tiene external_reference."
            )

            return {
                "status":
                    "missing_external_reference"
            }


        print(
            "PEDIDO:",
            order_id
        )


        # ====================================================
        # MONTO
        # ====================================================

        monto = float(
            payment.get(
                "transaction_amount"
            ) or 0
        )


        # ====================================================
        # BUSCAR PEDIDO
        # ====================================================

        with get_connection() as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        p.id,
                        p.total,
                        p.pago_confirmado,
                        p.email_comprador_enviado,
                        p.email_admin_enviado,
                        u.nombre,
                        u.correo_electronico
                    FROM pedidos p
                    INNER JOIN usuario_comun u
                        ON u.uc_id = p.uc_id
                    WHERE p.id = %s
                    """,
                    (order_id,)
                )


                pedido = cur.fetchone()


                if not pedido:

                    print(
                        "No se encontró el pedido:",
                        order_id
                    )

                    return {
                        "status":
                            "order_not_found"
                    }


                (
                    pedido_id,
                    total,
                    pago_confirmado,
                    email_comprador_enviado,
                    email_admin_enviado,
                    nombre,
                    email_comprador
                ) = pedido


                print(
                    "Pedido encontrado:",
                    pedido_id
                )

                print(
                    "Comprador:",
                    email_comprador
                )


                # =================================================
                # MARCAR COMO PAGADO
                # =================================================

                cur.execute(
                    """
                    UPDATE pedidos
                    SET
                        estado = 'pagado',
                        pago_confirmado = TRUE,
                        payment_id = %s
                    WHERE id = %s
                    """,
                    (
                        str(payment_id),
                        order_id
                    )
                )


        # ====================================================
        # CORREO AL COMPRADOR
        # ====================================================

        if not email_comprador_enviado:

            print(
                "Enviando correo al comprador..."
            )


            await enviar_correo_compra(

                email_usuario=
                    email_comprador,

                nombre_usuario=
                    nombre or "Cliente",

                id_compra=
                    order_id,

                monto=
                    monto

            )


            with get_connection() as conn:

                conn.execute(
                    """
                    UPDATE pedidos
                    SET
                        email_comprador_enviado = TRUE
                    WHERE id = %s
                    """,
                    (order_id,)
                )


            print(
                "Correo al comprador enviado."
            )


        else:

            print(
                "El correo al comprador "
                "ya había sido enviado."
            )


        # ====================================================
        # CORREO AL ADMINISTRADOR
        # ====================================================

        if not email_admin_enviado:

            print(
                "Enviando correo al administrador..."
            )


            await enviar_correo_admin(

                id_compra=
                    order_id,

                email_comprador=
                    email_comprador,

                monto=
                    monto

            )


            with get_connection() as conn:

                conn.execute(
                    """
                    UPDATE pedidos
                    SET
                        email_admin_enviado = TRUE
                    WHERE id = %s
                    """,
                    (order_id,)
                )


            print(
                "Correo al administrador enviado."
            )


        else:

            print(
                "El correo al administrador "
                "ya había sido enviado."
            )


        # ====================================================
        # RESPUESTA
        # ====================================================

        print(
            "WEBHOOK PROCESADO CORRECTAMENTE."
        )


        return {

            "status":
                "ok",

            "pedido_id":
                order_id,

            "payment_id":
                str(payment_id),

            "payment_status":
                status

        }


    except Exception as e:

        print()
        print(
            "========================================"
        )
        print(
            "ERROR WEBHOOK MERCADO PAGO"
        )
        print(
            "========================================"
        )
        print(
            repr(e)
        )
        print(
            "========================================"
        )
        print()


        return {

            "status":
                "error",

            "detail":
                str(e)

        }
