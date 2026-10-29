from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import articulos, ruta

router = APIRouter(prefix="/api", tags=["ruta"])

# Sede del evento (Utopía Elena Poniatowska Amor, San Lucas, Coyoacán): origen por defecto de la demo.
SEDE = {"lat": 19.3486, "lng": -99.1530}


class Punto(BaseModel):
    lat: float
    lng: float


class InterpretarRequest(BaseModel):
    texto: str


class RutaRequest(BaseModel):
    origen: Punto = Field(default_factory=lambda: Punto(**SEDE))
    texto_lista: str
    dia: int | None = Field(default=None, ge=0, le=6, description="0 = lunes … 6 = domingo; por defecto hoy")
    hora: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$", description="HH:MM; por defecto ahora")
    radio_m: int = Field(default=1500, ge=200, le=5000)
    alpha: float = Field(default=0.6, ge=0, le=1)
    regresar: bool = True


@router.post("/articulos/interpretar")
def interpretar(body: InterpretarRequest) -> dict:
    return articulos.interpretar(body.texto)


@router.post("/ruta")
def armar(body: RutaRequest) -> dict:
    try:
        return ruta.armar_ruta(body.origen.model_dump(), body.texto_lista, body.dia, body.hora,
                               body.radio_m, body.alpha, body.regresar)
    except ruta.RutaConCadena as error:
        raise HTTPException(status_code=500, detail="La ruta incluía una cadena; no se entrega.") from error
