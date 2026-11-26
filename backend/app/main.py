from fastapi import APIRouter, FastAPI

from app.router import perfil, registros

app = FastAPI(title="GluMee API")
api = APIRouter(prefix="/api/v1")


@api.get("/salud")
def salud():
    return {"estado": "ok"}

api.include_router(perfil.router)
api.include_router(registros.router)
app.include_router(api)