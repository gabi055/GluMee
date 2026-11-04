from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TipoCondicion(str, Enum):
    tipo_1 = "tipo_1"
    tipo_2 = "tipo_2"
    prediabetes = "prediabetes"
    prevencion = "prevencion"


class PerfilEntrada(BaseModel):
    apodo: str = Field(min_length=1, max_length=40)
    tipo_condicion: TipoCondicion


class PerfilSalida(PerfilEntrada):
    creado_en: datetime | None = None