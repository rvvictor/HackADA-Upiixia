"""Páginas públicas del negocio: /n/{slug} y su cartel imprimible."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.services import eventos, paginas
from app.services import negocio as svc

router = APIRouter(tags=["paginas"])


def _pagina(slug: str, request: Request) -> dict:
    """Metadatos de la página; la genera si el slug es de un negocio o alta y aún no tiene página."""
    meta = paginas.pagina_o_generar(slug, str(request.base_url))
    if meta is None or paginas.leer_html(slug) is None:
        raise HTTPException(status_code=404, detail="Página no encontrada")
    return meta


@router.get("/n/{slug}", response_class=HTMLResponse)
def ver_pagina(slug: str, request: Request) -> HTMLResponse:
    meta = _pagina(slug, request)
    eventos.registrar("vista_pagina", meta["negocio_id"], meta.get("h3"))
    return HTMLResponse(paginas.leer_html(slug))


@router.get("/n/{slug}/cartel", response_class=HTMLResponse)
def ver_cartel(slug: str, request: Request) -> HTMLResponse:
    meta = _pagina(slug, request)
    rec = svc.get_negocio(meta["negocio_id"]) or {}
    nombre = rec.get("nombre") or "Negocio de barrio"
    html = paginas.render_cartel(slug, nombre, str(request.base_url))
    return HTMLResponse(html)
