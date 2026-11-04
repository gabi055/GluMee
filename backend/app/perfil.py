from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_uid
from app.firebase import db
from app.schemas import PerfilEntrada, PerfilSalida

router = APIRouter(prefix="/perfil", tags=["perfil"])


@router.get("", response_model=PerfilSalida)
def obtener_perfil(uid: str = Depends(get_uid)):
    doc = db.collection("usuarios").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Perfil no creado")
    return doc.to_dict()


@router.put("", response_model=PerfilSalida)
def guardar_perfil(datos: PerfilEntrada, uid: str = Depends(get_uid)):
    ref = db.collection("usuarios").document(uid)
    data = datos.model_dump(mode="json")
    if not ref.get().exists:
        data["creado_en"] = datetime.now(timezone.utc)
    ref.set(data, merge=True)
    return ref.get().to_dict()