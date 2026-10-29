from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import repartidores

router = APIRouter(prefix="/api/repartidores", tags=["repartidores"])


class CodigoIn(BaseModel):
    id: str


class SesionIn(BaseModel):
    id: str
    codigo: str


@router.post("", status_code=201)
def crear(entrada: repartidores.RepartidorIn) -> dict:
    return repartidores.publico(repartidores.crear(entrada))


@router.post("/codigo", status_code=201)
def codigo(entrada: CodigoIn) -> dict:
    try:
        cod = repartidores.pedir_codigo(entrada.id)
    except repartidores.NoEncontrado:
        raise HTTPException(404, "repartidor no encontrado")
    # Fuera de demo el código solo viaja por Telegram.
    if repartidores.demo_mode():
        return {"enviado": True, "codigo": cod, "demo_data": True}
    return {"enviado": True}


@router.post("/sesion")
def sesion(entrada: SesionIn) -> dict:
    try:
        return repartidores.abrir_sesion(entrada.id, entrada.codigo)
    except repartidores.AccesoInvalido as e:
        raise HTTPException(401, str(e))


@router.get("/{rid}")
def perfil(rid: str) -> dict:
    try:
        r = repartidores.obtener(rid)
    except repartidores.NoEncontrado:
        raise HTTPException(404, "repartidor no encontrado")
    return {**repartidores.publico(r), "incentivos": repartidores.avance(r)}
