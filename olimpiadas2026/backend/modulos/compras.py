"""
Pedidos vinculados al comprador autenticado;
no confirman ventas ni pagos.
"""

import os
import secrets
import time

from uuid import uuid4
from collections import defaultdict
from decimal import Decimal

from dotenv import load_dotenv

from fastapi import HTTPException, Header

import bcrypt

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from modulos.gestion import connection


# ============================================================
# CONFIGURACIÓN
# ============================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# SESIONES
# ============================================================

_sessions = {}


# ============================================================
# LOGIN
# ============================================================

def login(email, password):

    with connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    uc_id,
                    contraseña
                FROM usuario_comun
                WHERE lower(correo_electronico) = %s
                """,
                (
                    email.strip().lower(),
                )
            )

            row = cur.fetchone()


    try:

        valid = (
            bool(row)
            and bcrypt.checkpw(
                password.encode(),
                row[1].encode()
            )
        )

    except (ValueError, TypeError):

        valid = False


    if not valid:

        raise HTTPException(
            401,
            "Correo o contraseña incorrectos"
        )


    now = time.time()


    # Eliminar sesiones vencidas

    for key in list(_sessions):

        if _sessions.get(
            key,
            (None, 0)
        )[1] <= now:

            _sessions.pop(
                key,
                None
            )


    # Crear nueva sesión

    token = secrets.token_urlsafe(32)

    _sessions[token] = (
        row[0],
        now + 3600
    )


    return {
        "token": token,
        "expires_in": 3600
    }


# ============================================================
# VALIDAR COMPRADOR
# ============================================================

def require_buyer(
    authorization: str = Header(default="")
):

    token = authorization.removeprefix(
        "Bearer "
    )

    session = (
        _sessions.get(token)
        if authorization.startswith("Bearer ")
        else None
    )


    if (
        not session
        or session[1] <= time.time()
    ):

        _sessions.pop(
            token,
            None
        )

        raise HTTPException(
            401,
            "Volvé a iniciar sesión para realizar el pedido"
        )


    return session[0]


# ============================================================
# CREAR CHECKOUT
# ============================================================

def checkout(
    items,
    user_id,
    sdk
):

    # --------------------------------------------------------
    # Verificar Mercado Pago
    # --------------------------------------------------------

    if sdk is None:

        raise HTTPException(
            503,
            "Mercado Pago no está configurado"
        )


    # --------------------------------------------------------
    # Validar carrito
    # --------------------------------------------------------

    if not items or len(items) > 100:

        raise HTTPException(
            422,
            "Carrito inválido"
        )


    # --------------------------------------------------------
    # Agrupar cantidades
    # --------------------------------------------------------

    amounts = defaultdict(int)


    for item in items:

        if (
            item.quantity < 1
            or item.quantity > 50
        ):

            raise HTTPException(
                422,
                "Cantidad inválida"
            )


        amounts[
            (
                item.tipo,
                item.id
            )
        ] += item.quantity


    # --------------------------------------------------------
    # Crear pedido
    # --------------------------------------------------------

    order_id = str(uuid4())

    snapshot = []

    total = Decimal("0")


    # --------------------------------------------------------
    # Consultar productos
    # --------------------------------------------------------

    with connection() as conn:

        with conn.cursor(
            row_factory=dict_row
        ) as cur:

            for (
                kind,
                code
            ), quantity in sorted(
                amounts.items()
            ):

                table = {
                    "viaje": "viaje_simple",
                    "paquete": "paquete_de_viajes"
                }[kind]


                cur.execute(
                    sql.SQL(
                        """
                        SELECT
                            codigo,
                            nombre,
                            precio,
                            cupos,
                            estado
                        FROM {}
                        WHERE codigo = %s
                        """
                    ).format(
                        sql.Identifier(table)
                    ),
                    (code,)
                )


                product = cur.fetchone()


                # ------------------------------------------------
                # Validar producto
                # ------------------------------------------------

                if (
                    not product
                    or product["cupos"] < quantity
                    or str(
                        product["estado"]
                    ).lower() != "disponible"
                ):

                    raise HTTPException(
                        409,
                        "Un producto no está disponible o no tiene suficientes cupos"
                    )


                # ------------------------------------------------
                # Validar precio
                # ------------------------------------------------

                price = Decimal(
                    str(
                        product["precio"]
                    )
                )


                if (
                    not price.is_finite()
                    or price <= 0
                ):

                    raise HTTPException(
                        409,
                        "Precio de catálogo inválido"
                    )


                # ------------------------------------------------
                # Guardar snapshot
                # ------------------------------------------------

                snapshot.append(
                    {
                        "id": code,
                        "tipo": kind,
                        "title": product["nombre"],
                        "unit_price": float(price),
                        "quantity": quantity
                    }
                )


                total += (
                    price * quantity
                )


            # ----------------------------------------------------
            # Crear pedido en DB
            # ----------------------------------------------------

            cur.execute(
                """
                INSERT INTO pedidos
                (
                    id,
                    uc_id,
                    estado,
                    total,
                    items
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    order_id,
                    user_id,
                    "creado",
                    total,
                    Jsonb(snapshot)
                )
            )


    # ========================================================
    # URL DEL WEBHOOK
    # ========================================================

    webhook_url = os.getenv(
        "MP_WEBHOOK_URL"
    )


    # ========================================================
    # CREAR PREFERENCIA DE MERCADO PAGO
    # ========================================================

    preference_data = {

        "external_reference": order_id,

        "items": [

            {
                **{
                    key: value
                    for key, value in item.items()
                    if key != "tipo"
                },

                "id": (
                    f"{item['tipo']}:{item['id']}"
                ),

                "currency_id": "ARS"
            }

            for item in snapshot

        ],

        "back_urls": {

            "success": "http://localhost:5173/",

            "failure": "http://localhost:5173/",

            "pending": "http://localhost:5173/"

        }

    }


    # --------------------------------------------------------
    # Agregar webhook solamente si está configurado
    # --------------------------------------------------------

    if webhook_url:

        preference_data[
            "notification_url"
        ] = webhook_url


        print(
            "Webhook Mercado Pago:",
            webhook_url
        )

    else:

        print(
            "ADVERTENCIA: MP_WEBHOOK_URL no está configurado."
        )


    # ========================================================
    # ENVIAR PREFERENCIA A MERCADO PAGO
    # ========================================================

    try:

        response = (
            sdk.preference().create(
                preference_data
            )
        )


        data = response.get(
            "response",
            {}
        )


        # ----------------------------------------------------
        # Validar respuesta
        # ----------------------------------------------------

        if (
            response.get("status")
            not in (200, 201)
            or not data.get("id")
            or not data.get("init_point")
        ):

            print(
                "Respuesta de Mercado Pago:",
                response
            )

            raise ValueError(
                "Preferencia rechazada"
            )


    except Exception as e:

        print(
            "ERROR CREANDO PREFERENCIA:",
            e
        )


        with connection() as conn:

            conn.execute(
                """
                UPDATE pedidos
                SET estado = 'error_checkout'
                WHERE id = %s
                """,
                (order_id,)
            )


        raise HTTPException(
            502,
            "No se pudo iniciar el pago. El intento quedó registrado en tu pedido"
        )


    # ========================================================
    # ACTUALIZAR PEDIDO
    # ========================================================

    with connection() as conn:

        conn.execute(
            """
            UPDATE pedidos
            SET
                estado = 'pendiente_pago',
                preferencia_id = %s
            WHERE id = %s
            """,
            (
                data["id"],
                order_id
            )
        )


    # ========================================================
    # RESPUESTA AL FRONTEND
    # ========================================================

    return {

        "pedido_id": order_id,

        "id": data["id"],

        "init_point": data["init_point"],

        "total": total

    }