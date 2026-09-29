import os
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

MERCADOPAGO_TOKEN = os.getenv("MERCADOPAGO_TOKEN")

mp_sdk = (
    mercadopago.SDK(MERCADOPAGO_TOKEN)
    if MERCADOPAGO_TOKEN
    else None
)


# ============================================================
# MODELOS
# ============================================================

class ItemCarrito(BaseModel):
    id: Any
    title: str
    unit_price: float
    quantity: int


class Carrito(BaseModel):
    items: List[ItemCarrito]
    user: str


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

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

hostURL = (
    f"postgresql://postgres.dncdqfmfixojxprdlbkf:{DATABASE_PASSWORD}"
    "@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)


def get_connection():
    return psycopg.connect(hostURL)


# ============================================================
# ROUTERS
# ============================================================

from roots.autos import router as autos_routers
from roots.clientes import router as clientes_routers
from roots.excursiones import router as excursiones_routers
from roots.paqueteDeViajes import router as paqueteDeViajes_routers
from roots.ventas import router as ventas_routers
from roots.viajes import router as viajes_routers


app.include_router(autos_routers, prefix="/autos")
app.include_router(clientes_routers, prefix="/clientes")
app.include_router(excursiones_routers, prefix="/excursiones")
app.include_router(paqueteDeViajes_routers, prefix="/paqueteDeViajes")
app.include_router(ventas_routers, prefix="/ventas")
app.include_router(viajes_routers, prefix="/viajes")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "mercadopago_configurado": bool(mp_sdk),
        "database_configurada": bool(DATABASE_PASSWORD),
    }


# ============================================================
# MERCADO PAGO - CREAR PREFERENCIA
# ============================================================

@app.post("/carrito")
def post_carrito(carrito: Carrito):

    print("====================================")
    print("INICIANDO CREACIÓN DE PREFERENCIA")
    print("====================================")

    # --------------------------------------------------------
    # Verificar Mercado Pago
    # --------------------------------------------------------

    if not mp_sdk:
        return {
            "error": "No se configuró MERCADOPAGO_TOKEN. "
                     "Definilo en el archivo .env.",
            "sandbox_init_point": None,
            "detalle": "Falta el token de Mercado Pago",
        }

    # --------------------------------------------------------
    # Verificar carrito
    # --------------------------------------------------------

    if not carrito.items:
        return {
            "error": "El carrito está vacío.",
            "detalle": "No se recibieron productos.",
        }

    # --------------------------------------------------------
    # Mostrar productos recibidos
    # --------------------------------------------------------

    print("USUARIO:", carrito.user)
    print("PRODUCTOS:")

    for item in carrito.items:
        print(
            f"- {item.title} | "
            f"Precio: {item.unit_price} | "
            f"Cantidad: {item.quantity}"
        )

    # --------------------------------------------------------
    # Crear datos de Mercado Pago
    # --------------------------------------------------------

    preference_data = {
        "items": [
            {
                "id": str(item.id),
                "title": item.title,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "currency_id": "ARS",
            }
            for item in carrito.items
        ],

        "metadata": {
            "user": carrito.user,
        },

        # IMPORTANTE:
        # Dejamos las URLs de retorno, pero quitamos
        # auto_return porque estás trabajando en localhost.
        #
        # Mercado Pago no permite usar localhost como URL
        # válida para auto_return.
        "back_urls": {
            "success": "http://localhost:5173/",
            "failure": "http://localhost:5173/",
            "pending": "http://localhost:5173/",
        },
    }

    print("====================================")
    print("PREFERENCE DATA:")
    print(preference_data)
    print("====================================")

    # --------------------------------------------------------
    # Crear preferencia
    # --------------------------------------------------------

    try:

        preference_response = mp_sdk.preference().create(
            preference_data
        )

        print("====================================")
        print("RESPUESTA MERCADO PAGO:")
        print(preference_response)
        print("====================================")

        # ----------------------------------------------------
        # Verificar respuesta
        # ----------------------------------------------------

        if "response" not in preference_response:

            return {
                "error": "No se pudo crear la preferencia de pago.",
                "detalle": preference_response,
            }

        preference = preference_response["response"]

        # ----------------------------------------------------
        # Verificar errores devueltos por Mercado Pago
        # ----------------------------------------------------

        if "error" in preference:

            return {
                "error": "Mercado Pago rechazó la creación de la preferencia.",
                "detalle": preference,
            }

        # ----------------------------------------------------
        # Verificar ID
        # ----------------------------------------------------

        if "id" not in preference:

            return {
                "error": "No se recibió la preferencia de Mercado Pago.",
                "detalle": preference,
            }

        # ----------------------------------------------------
        # Obtener URL de pago
        # ----------------------------------------------------

        init_point = preference.get("init_point")
        sandbox_init_point = preference.get("sandbox_init_point")

        print("====================================")
        print("PREFERENCIA CREADA CORRECTAMENTE")
        print("ID:", preference["id"])
        print("INIT POINT:", init_point)
        print("SANDBOX INIT POINT:", sandbox_init_point)
        print("====================================")

        # ----------------------------------------------------
        # Respuesta al frontend
        # ----------------------------------------------------

        return {
            "id": preference["id"],
            "init_point": init_point,
            "sandbox_init_point": sandbox_init_point,
        }

    # --------------------------------------------------------
    # Error general
    # --------------------------------------------------------

    except Exception as e:

        print("====================================")
        print("ERROR MERCADO PAGO")
        print("====================================")
        print(str(e))
        print("====================================")

        return {
            "error": "Ocurrió un error al comunicarse con Mercado Pago.",
            "detalle": str(e),
        }