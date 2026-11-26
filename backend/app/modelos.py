from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Literal, Optional
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

# Margen por desfase de reloj entre el celular y el servidor
MARGEN_RELOJ = timedelta(minutes=2)


CRITERIOS_VALIDOS = {
    "carbs_refinados", "bebidas_azucaradas", "proteina_verduras", "frituras",
}

FAMILIARES_VALIDOS = {
    "padre", "madre", "hermanos", "abuelos", "otro"
}

class RangoGlucosa(BaseModel):
    min: int = Field(ge=20, le=600)
    max: int = Field(ge=20, le=600)
    
    @model_validator(mode="after")
    def orden(self):
        if self.min >= self.max:
            raise ValueError("El mínimo del rango debe ser menor que el máximo.")
        return self
    
class Perfil(BaseModel):
    model_config= ConfigDict(str_strip_whitespace=True)
    
    apodo: str =Field(min_length=1, max_length=30)
    tipo_condicion: Literal["tipo_1", "tipo_2", "prediabetes", "prevencion"]
    antecedentes_familiares: list[str] = Field(default_factory=list, max_length=5)
    alergias: list[str] = Field(default_factory =list, max_length=10)
    criterios_alimentarios: list[str] = Field(default_factory = list, max_length=10)
    rango_glucosa: Optional[RangoGlucosa] = None
    meta_ml: Optional[int] = Field(default=None, ge=500, le=6000)
    
    @model_validator(mode="after")
    def listas_validas(self):
        malos = set(self.criterios_alimentarios) - CRITERIOS_VALIDOS
        if malos:
            raise ValueError(f"Criterios no válidos: {', '.join(sorted(malos))}")
        malos = set(self.antecedentes_familiares) - FAMILIARES_VALIDOS
        if malos:
            raise ValueError(f"Antecedentes no válidos: {', '.join(sorted(malos))}")
        alergias_limpias = [a.strip() for a in self.alergias]
        for a in alergias_limpias:
            if not 1 <= len(a) <= 40:
                raise ValueError("Cada alergia debe tener entre 1 y 40 caracteres.")
        vistas = {}
        for a in alergias_limpias:
            vistas.setdefault(a.lower(), a)
        self.alergias = list(vistas.values())
        # sin duplicados, conservando el orden
        self.criterios_alimentarios = list(dict.fromkeys(self.criterios_alimentarios))
        self.antecedentes_familiares = list(dict.fromkeys(self.antecedentes_familiares))
        return self

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