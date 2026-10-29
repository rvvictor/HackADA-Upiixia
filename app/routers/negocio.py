"""API del negocio: ficha, avance, escalera, programas y página web."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.services import negocio as svc
from app.services import paginas

router = APIRouter(prefix="/api/negocio", tags=["negocio"])


class ProductoIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    precio: float | None = Field(default=None, ge=0)
    fecha: str | None = Field(default=None, max_length=40)


class FichaIn(BaseModel):
    # extra="forbid": no se puede guardar un campo fuera de la ficha (p. ej. ventas o ingresos).
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, max_length=120)
    giro: str | None = Field(default=None, max_length=80)
    colonia: str | None = Field(default=None, max_length=80)
    telefono: str | None = Field(default=None, max_length=20)
    horario: str | None = Field(default=None, max_length=120)
    formas_pago: list[str] | None = Field(default=None, max_length=10)
    productos: list[ProductoIn] | None = Field(default=None, max_length=30)
    acepta_mercomuna: bool | None = None
    ubicacion: Literal["exacta", "aproximada"] | None = None
    aparecer_en_rutas: bool | None = None


def _404() -> HTTPException:
    return HTTPException(status_code=404, detail="Negocio no encontrado")


@router.get("/{negocio_id}")
def ver_negocio(negocio_id: str) -> dict:
    datos = svc.ficha_completa(negocio_id)
    if datos is None:
        raise _404()
    return datos


@router.put("/{negocio_id}/ficha")
def editar_ficha(negocio_id: str, body: FichaIn) -> dict:
    if svc.get_negocio(negocio_id) is None:
        raise _404()
    svc.guardar_ficha(negocio_id, body.model_dump(exclude_unset=True))
    return svc.ficha_completa(negocio_id)


@router.post("/{negocio_id}/pagina")
def generar_pagina(negocio_id: str, request: Request) -> dict:
    rec = svc.get_negocio(negocio_id)
    if rec is None:
        raise _404()
    return paginas.generar_pagina(rec, str(request.base_url))
