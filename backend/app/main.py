from fastapi import APIRouter, Depends, FastAPI

from app.auth import get_uid

app = FastAPI(title="GluMee API")
api = APIRouter(prefix="/api/v1")


@api.get("/salud")
def salud():
    return {"estado": "ok"}


@api.get("/yo")
def yo(uid: str = Depends(get_uid)):
    """Endpoint temporal para probar la verificación de token."""
    return {"uid": uid}


app.include_router(api)