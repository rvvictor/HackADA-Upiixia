"""Altas en vivo: POST /api/altas, GET /api/altas/live, POST /api/altas/ficha (vista previa sin publicar)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import altas

router = APIRouter(prefix="/api/altas", tags=["altas"])


class TextoIn(BaseModel):
    texto: str


@router.post("", status_code=201)
def crear(entrada: altas.AltaIn) -> dict:
    try:
        alta = altas.crear_alta(entrada)
    except altas.SinConfirmar as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return {**alta.model_dump(), "pagina": f"/n/{alta.slug}", "panel": f"/#/negocio/{alta.id}"}


@router.get("/live")
def live(desde: float = 0) -> dict:
    nuevas = altas.altas_desde(desde)
    ultimo = max((a.get("ts") or 0 for a in nuevas), default=desde)
    return {"altas": nuevas, "desde": desde, "ultimo_ts": ultimo}


@router.post("/ficha")
def ficha(entrada: TextoIn) -> dict:
    """Texto libre → ficha para que el comerciante la confirme. No publica nada."""
    f, grabada = altas.extraer_ficha(entrada.texto)
    return {"ficha": f.model_dump(), "texto": altas.ficha_texto(f), "demo_data": grabada}
