import os
from pathlib import Path
from typing import Any, List, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
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
    id: int = Field(gt=0)
    tipo: Literal['viaje','paquete']
    quantity: int = Field(gt=0,le=50)

class Carrito(BaseModel):
    items: List[ItemCarrito]


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
    return psycopg.connect(
        host='aws-0-us-west-2.pooler.supabase.com', port=5432,
        user='postgres.dncdqfmfixojxprdlbkf', password=DATABASE_PASSWORD,
        dbname='postgres', connect_timeout=10,
        options='-c statement_timeout=15000 -c lock_timeout=5000',
    )


# ============================================================
# ROUTERS
# ============================================================

from roots.autos import router as autos_routers
from roots.clientes import router as clientes_routers
from roots.excursiones import router as excursiones_routers
from roots.paqueteDeViajes import router as paqueteDeViajes_routers
from roots.ventas import router as ventas_routers
from roots.viajes import router as viajes_routers


from roots.administradores import router as admin_router
app.include_router(admin_router)
from roots.circuito import router as circuito_router
app.include_router(circuito_router)
from roots.pagos import router as pagos_router
app.include_router(pagos_router)

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

from modulos.compras import require_buyer, checkout

@app.post("/carrito")
def post_carrito(carrito: Carrito, user_id=Depends(require_buyer)):
    return checkout(carrito.items, user_id, mp_sdk)
