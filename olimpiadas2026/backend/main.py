
import os
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mercadopago
import psycopg


# ==============================================
#              Cargar variables .env
# ==============================================

# Busca el .env en la raíz del proyecto:
# olimp-26/.env
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ==============================================
#          Configuración de la aplicación
# ==============================================

app = FastAPI()


# ==============================================
#             Configuración Mercado Pago
# ==============================================

MERCADOPAGO_TOKEN = os.getenv("MERCADOPAGO_TOKEN")

mp_sdk = (
    mercadopago.SDK(MERCADOPAGO_TOKEN)
    if MERCADOPAGO_TOKEN
    else None
)


# ==============================================
#                  Modelos
# ==============================================

class ItemCarrito(BaseModel):
    id: Any
    title: str
    unit_price: float
    quantity: int


class Carrito(BaseModel):
    items: List[ItemCarrito]
    user: str


# ==============================================
#              Configuración de CORS
# ==============================================

# Permitir solicitudes desde cualquier origen.
# Recuerda restringir esto antes de producción.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================
#          Conexión a PostgreSQL / Supabase
# ==============================================

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")




# URL de conexión a PostgreSQL
hostURL = (
    f"postgresql://postgres.dncdqfmfixojxprdlbkf:{DATABASE_PASSWORD}@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)


def get_connection():
    return psycopg.connect(hostURL)


# ==============================================
#                  Rutas
# ==============================================

# Importar y registrar todos los routers
from roots.autos import router as autos_routers
from roots.clientes import router as clientes_routers
from roots.excursiones import router as excursiones_routers
from roots.paqueteDeViajes import router as paqueteDeViajes_routers
from roots.ventas import router as ventas_routers
from roots.viajes import router as viajes_routers


# Registrar routers
app.include_router(autos_routers, prefix="/autos")
app.include_router(clientes_routers, prefix="/clientes")
app.include_router(excursiones_routers, prefix="/excursiones")
app.include_router(paqueteDeViajes_routers, prefix="/paqueteDeViajes")
app.include_router(ventas_routers, prefix="/ventas")
app.include_router(viajes_routers, prefix="/viajes")


# ==============================================
#                  Health Check
# ==============================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "mercadopago_configurado": bool(mp_sdk),
        "database_configurada": bool(DATABASE_PASSWORD),
    }


# ==============================================
#                Crear carrito
# ==============================================

@app.post("/carrito")
def post_carrito(carrito: Carrito):

    if not mp_sdk:
        return {
            "error": "No se configuró MERCADOPAGO_TOKEN. "
                     "Definilo en el archivo .env.",
            "sandbox_init_point": None,
            "detalle": "Falta el token de Mercado Pago",
        }

    preference_data = {
        "items": [
            {
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
        "back_urls": {
            "success": "http://localhost:5173/",
            "failure": "http://localhost:5173/",
            "pending": "http://localhost:5173/",
        },
        "auto_return": "approved",
    }

    try:

        preference_response = mp_sdk.preference().create(
            preference_data
        )

        if "response" not in preference_response:
            return {
                "error": "No se pudo crear la preferencia de pago.",
                "detalle": preference_response,
            }

        preference = preference_response["response"]

        if "id" not in preference:
            return {
                "error": "No se recibió la preferencia de Mercado Pago.",
                "detalle": preference,
            }

        return {
            "id": preference["id"],
            "init_point": preference.get("init_point"),
            "sandbox_init_point": preference.get(
                "sandbox_init_point"
            ),
        }

    except Exception as e:

        return {
            "error": "Ocurrió un error al comunicarse con Mercado Pago.",
            "detalle": str(e),
        }
