from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

# Margen por desfase de reloj entre el celular y el servidor
MARGEN_RELOJ = timedelta(minutes=2)


class Momento(str, Enum):
    ayunas = "ayunas"
    antes_de_comer = "antes_de_comer"
    despues_de_comer = "despues_de_comer"
    antes_de_dormir = "antes_de_dormir"
    otro = "otro"


class TipoComida(str, Enum):
    desayuno = "desayuno"
    comida = "comida"
    cena = "cena"
    colacion = "colacion"


class TipoActividad(str, Enum):
    fuerza = "fuerza"
    cardio = "cardio"
    otro = "otro"


class RegistroBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    # AwareDatetime rechaza fechas sin zona horaria
    fecha_hora: AwareDatetime

    @field_validator("fecha_hora")
    @classmethod
    def no_futura(cls, v: AwareDatetime) -> AwareDatetime:
        if v > datetime.now(timezone.utc) + MARGEN_RELOJ:
            raise ValueError("La fecha y hora no pueden estar en el futuro.")
        return v


class Glucosa(RegistroBase):
    valor: int = Field(ge=20, le=600)  # mg/dL
    momento: Momento
    nota: Optional[str] = Field(default=None, max_length=200)


class Alimentacion(RegistroBase):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    tipo_comida: TipoComida


class Actividad(RegistroBase):
    tipo: TipoActividad
    duracion_min: int = Field(ge=1, le=600)


class Hidratacion(RegistroBase):
    ml: int = Field(ge=50, le=5000)