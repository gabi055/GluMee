from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_uid
from app.firebase import db
from app.modelos import Perfil

router = APIRouter(prefix="/perfil", tags=["perfil"])


@router.get("")
def obtener(uid: str = Depends(get_uid)):
    snap = db.collection("usuarios").document(uid).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Aún no has creado tu perfil.")
    return snap.to_dict()


@router.put("")
def guardar(perfil: Perfil, uid: str = Depends(get_uid)):
    ref = db.collection("usuarios").document(uid)
    datos = perfil.model_dump()
    datos["actualizado_en"] = datetime.now(timezone.utc)
    if not ref.get().exists:
        datos["creado_en"] = datos["actualizado_en"]
    ref.set(datos, merge=True)
    return ref.get().to_dict()