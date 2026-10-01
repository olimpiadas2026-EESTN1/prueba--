# ===============================
#   Creación de modelos Pydantic
# ===============================
from pydantic import BaseModel, Field
from typing import Optional


class Usuarios_comunes(BaseModel):
    """
    Modelo Pydantic para la creación de usuarios comunes.
    """

    nombre: str = Field(min_length=1,max_length=2000)
    apellido: str
    contraseña: str
    correo_electronico: str


class Usuarios_comunes_id(BaseModel):
    """
    Modelo Pydantic para obtener la id de un usuario comun.
    """

    uc_id: int = Field(gt=0)


class Ventas(BaseModel):
    """
    Modelo Pydantic para registrar información de una venta.
    """

    medio_de_pago: str
    cuotas: bool
    cantidad: Optional[int] = None
    codigo_vs: Optional[int] = None
    codigo_pv: Optional[int] = None
    precio: float = Field(gt=0, allow_inf_nan=False)


class Venta_request(BaseModel):
    """
    Modelo Pydantic para registrar información de una venta y relacionarlo a un usuario.
    """

    data: Ventas
    correo_electronico: str


class Venta_id(BaseModel):
    """
    Modelo Pydantic para obtener la id de una venta.
    """

    vtas_id: int = Field(gt=0)


class Viaje_simple(BaseModel):
    """
    Modelo Pydantic para representar un viaje simple.
    """

    nombre: str = Field(min_length=1,max_length=2000)
    descripcion: str = Field(min_length=1,max_length=2000)
    precio: float = Field(gt=0, allow_inf_nan=False)
    origen: str = Field(min_length=1,max_length=2000)
    destino: str = Field(min_length=1,max_length=2000)
    transporte: str
    fecha: str  # Formato recomendado: 'dd/mm/yy'
    hora: str  # Formato recomendado: 'HH:MM'
    cupos: int = Field(ge=0)
    duracion_aprox: str
    tipo_de_viaje: str  # Valores: 'solo ida' o 'ida y vuelta'


class Viaje_simple_id(BaseModel):
    """
    Modelo Pydantic para representar la ID de un viaje simple.
    """

    vs_id: int = Field(gt=0)


class Paquete_de_viaje(BaseModel):
    """
    Modelo Pydantic para representar un paquete de viaje.
    """

    nombre: str = Field(min_length=1,max_length=2000)
    precio: float = Field(gt=0, allow_inf_nan=False)
    origen: str = Field(min_length=1,max_length=2000)
    destino: str = Field(min_length=1,max_length=2000)
    estadia: str
    tipo: str  # Valores: 'solo ida' o 'ida y vuelta'
    descripcion: str = Field(min_length=1,max_length=2000)
    cupos: int = Field(ge=0)
    duracion: str
    tipo_de_viaje: str  # Valores: 'nacional' o 'internacional'
    hora: str  # Formato recomendado: 'HH:MM'
    fecha: str  # Formato recomendado: 'dd/mm/yy'


class Codigo_paquete_de_viaje(BaseModel):
    """
    Modelo Pydantic para obtener el codigo de un paquete de viaje
    """

    codigoDeViaje: int = Field(gt=0)


class Paquete_de_viaje_id(BaseModel):
    """
    Modelo Pydantic para representar la id de un paquete de viaje.
    """

    pv_id: int = Field(gt=0)


class Auto(BaseModel):
    """
    Modelo Pydantic para representar un auto disponible para alquiler.
    """

    modelo: str = Field(min_length=1,max_length=2000)
    disponibles: int = Field(ge=0)
    precio_por_dia: float = Field(gt=0, allow_inf_nan=False)


class Auto_id(BaseModel):
    """
    Modelo Pydantic para representar el id de un auto.
    """

    auto_id: int = Field(gt=0)


class Vinculo_vs_a_auto(BaseModel):
    """
    Modelo Pydantic para representar el vinculo de un viaje simple a un auto
    """

    vs_id: int = Field(gt=0)
    at_id: int = Field(gt=0)


class Vinculo_pv_a_auto(BaseModel):
    """
    Modelo Pydantic para representar el vinculo de un paquete de viajes a un auto
    """

    pv_id: int = Field(gt=0)
    at_id: int = Field(gt=0)


class Validacion_de_usuarios(BaseModel):
    """
    Modelo Pydantic para representar logins.
    """

    usuarioIngresado: str
    contraseñaIngresada: str
