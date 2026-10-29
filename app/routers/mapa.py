"""Mapa SEDECO: GET /api/hex, /api/dinero/alcaldias, /api/tianguis y /api/sedeco/resumen."""

from fastapi import APIRouter, Query

from app.services import mapa

# Prefijo /api (no /api/mapa): las rutas son las del contrato de IDEA.md Apéndice C.
router = APIRouter(prefix="/api", tags=["mapa"])

DIA = Query(None, ge=0, le=6, description="0 = lunes … 6 = domingo; por defecto hoy")
HORA = Query(None, pattern=r"^\d{1,2}:\d{2}$", description="HH:MM; por defecto la hora actual de CDMX")


@router.get("/hex")
def hex_geojson() -> dict:
    return mapa.hexagonos()


@router.get("/dinero/alcaldias")
def dinero_alcaldias() -> list[dict]:
    return mapa.dinero_alcaldias()


@router.get("/tianguis")
def tianguis(dia: int | None = DIA, hora: str | None = HORA) -> dict:
    return mapa.tianguis(dia, hora)


@router.get("/sedeco/resumen")
def resumen(dia: int | None = DIA, hora: str | None = HORA) -> dict:
    return mapa.resumen(dia, hora)
