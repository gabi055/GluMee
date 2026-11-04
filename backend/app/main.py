from fastapi import APIRouter, FastAPI

from app.perfil import router as perfil_router

app = FastAPI(title="GluMee API")
api = APIRouter(prefix="/api/v1")


@api.get("/salud")
def salud():
    return {"estado": "ok"}

api.include_router(perfil_router)
app.include_router(api)