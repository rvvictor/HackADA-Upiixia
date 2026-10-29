from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import eventos

router = APIRouter(prefix="/api", tags=["eventos"])


class EventoRequest(BaseModel):
    tipo: Literal["busqueda", "compre_aqui"]
    negocio_id: str | None = None
    h3: str | None = None


@router.post("/eventos")
def registrar(body: EventoRequest) -> dict:
    return eventos.registrar(body.tipo, body.negocio_id, body.h3)
