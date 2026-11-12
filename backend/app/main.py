from fastapi import APIRouter, FastAPI

from app.router import registros

from app.perfil import router as perfil_router

app = FastAPI(title="GluMee API")
api = APIRouter(prefix="/api/v1")


@api.get("/salud")
def salud():
    return {"estado": "ok"}

api.include_router(perfil_router)
api.include_router(registros.router)
app.include_router(api)