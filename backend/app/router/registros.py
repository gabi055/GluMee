from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import AwareDatetime

from app.auth import get_uid
from app.modelos import Actividad, Alimentacion, Glucosa, Hidratacion

router = APIRouter(prefix="/registros", tags=["registros"])


class TipoRegistro(str, Enum):
    glucosa = "glucosa"
    alimentacion = "alimentacion"
    actividad = "actividad"
    hidratacion = "hidratacion"


def _coleccion(uid: str, nombre: str):
    return firestore.client().collection("usuarios").document(uid).collection(nombre)


def _guardar(uid: str, nombre: str, modelo):
    datos = modelo.model_dump()
    datos["fecha_hora"] = datos["fecha_hora"].astimezone(timezone.utc)  
    datos["creado_en"] = datetime.now(timezone.utc)
    _, ref = _coleccion(uid, nombre).add(datos)
    return {"id": ref.id, **datos}


@router.post("/glucosa", status_code=201)
def crear_glucosa(registro: Glucosa, uid: str = Depends(get_uid)):
    return _guardar(uid, "glucosa", registro)


@router.post("/alimentacion", status_code=201)
def crear_alimentacion(registro: Alimentacion, uid: str = Depends(get_uid)):
    return _guardar(uid, "alimentacion", registro)


@router.post("/actividad", status_code=201)
def crear_actividad(registro: Actividad, uid: str = Depends(get_uid)):
    return _guardar(uid, "actividad", registro)


@router.post("/hidratacion", status_code=201)
def crear_hidratacion(registro: Hidratacion, uid: str = Depends(get_uid)):
    return _guardar(uid, "hidratacion", registro)

@router.get("")
def listar(
    tipo: TipoRegistro,
    desde: Optional[AwareDatetime] = None,
    hasta: Optional[AwareDatetime] = None,
    limite: int = Query(500, ge=1, le=1000),
    uid: str = Depends(get_uid),
):
    if desde and hasta and desde > hasta:
        raise HTTPException(status_code=400, detail="'desde' no puede ser posterior a 'hasta'.")

    consulta = _coleccion(uid, tipo.value)
    if desde:
        consulta = consulta.where(filter=FieldFilter("fecha_hora", ">=", desde))
    if hasta:
        consulta = consulta.where(filter=FieldFilter("fecha_hora", "<=", hasta))
    consulta = consulta.order_by("fecha_hora", direction=firestore.Query.DESCENDING).limit(limite)

    return [{"id": d.id, **d.to_dict()} for d in consulta.stream()]