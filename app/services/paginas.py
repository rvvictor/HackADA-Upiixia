"""Página web automática de cada negocio: HTML con Jinja2, QR en base64 y cartel imprimible.

Archivos: `LIVE_DIR/paginas/{slug}.html` (la página) y `{slug}.json` (negocio_id, h3).
El slug se guarda en la ficha (`pagina_slug`) y no cambia al regenerar la página.
"""

import base64
import io
import json
import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import qrcode
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app import config
from app.services import negocio as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,119}$")
_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html"]))


def _ascii_slug(texto: str) -> str:
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", sin_acentos.lower()).strip("-")


def slug_para(rec: dict) -> str:
    base = _ascii_slug(str(rec.get("nombre") or ""))[:40].strip("-") or "negocio"
    ident = _ascii_slug(str(rec["id"]))
    return "-".join(p for p in (base, ident) if p)[:120].strip("-")


def slug_de(rec: dict) -> str:
    """Slug público: el ya asignado, luego el slug del alta del bot (PB-008), y si no, nombre-id."""
    return rec.get("pagina_slug") or rec.get("slug") or slug_para(rec)


def qr_data_uri(url: str, box_size: int = 8) -> str:
    qr = qrcode.QRCode(box_size=box_size, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def wa_url(telefono: Any) -> str | None:
    """Enlace wa.me solo si el negocio dio un número (10 dígitos o con lada 52)."""
    digitos = re.sub(r"\D", "", str(telefono or ""))
    if len(digitos) == 10:
        digitos = "52" + digitos
    if len(digitos) < 12:
        return None
    texto = quote("Hola, vi tu página en Pulso Barrial.")
    return f"https://wa.me/{digitos}?text={texto}"


def _carpeta() -> Path:
    return config.LIVE_DIR / "paginas"


def generar_pagina(rec: dict, base_url: str) -> dict:
    ficha = svc.ficha_publica(rec)
    slug = slug_de(rec)
    url_completa = f"{base_url.rstrip('/')}/n/{slug}"
    html = _env.get_template("pagina.html").render(
        ficha=ficha,
        descripcion=svc.descripcion(ficha),
        wa_url=wa_url(ficha.get("telefono")),
        qr=qr_data_uri(url_completa),
        url=url_completa,
    )
    carpeta = _carpeta()
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / f"{slug}.html").write_text(html, encoding="utf-8")
    (carpeta / f"{slug}.json").write_text(
        json.dumps(
            {
                "negocio_id": rec["id"],
                "h3": rec.get("h3"),
                "creada": datetime.now(UTC).isoformat(),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    if rec.get("pagina_slug") != slug:
        svc.guardar_ficha(rec["id"], {"pagina_slug": slug})
    return {
        "slug": slug,
        "url": f"/n/{slug}",
        "url_completa": url_completa,
        "cartel": f"/n/{slug}/cartel",
        "qr": qr_data_uri(url_completa, box_size=6),
    }


def meta_pagina(slug: str) -> dict | None:
    """Metadatos de una página publicada, o None si el slug no existe."""
    if not SLUG_RE.match(slug):
        return None
    datos = svc._leer_json(_carpeta() / f"{slug}.json", None)
    return datos if isinstance(datos, dict) else None


def leer_html(slug: str) -> str | None:
    if not SLUG_RE.match(slug):
        return None
    ruta = _carpeta() / f"{slug}.html"
    return ruta.read_text(encoding="utf-8") if ruta.is_file() else None


def negocio_por_slug(slug: str) -> dict | None:
    """Negocio cuyo slug público es `slug` (directorio o alta), con su ficha completa."""
    for rec in svc.registros_base():
        if slug_de(rec) == slug:
            return svc.get_negocio(str(rec["id"]))
    return None


def pagina_o_generar(slug: str, base_url: str) -> dict | None:
    """Metadatos de la página; si aún no existe, la genera en el primer acceso. None = no hay negocio."""
    if not SLUG_RE.match(slug):
        return None
    meta = meta_pagina(slug)
    if meta is not None and leer_html(slug) is not None:
        return meta
    rec = negocio_por_slug(slug)
    if rec is None:
        return None
    generar_pagina(rec, base_url)
    return meta_pagina(slug)


def render_cartel(slug: str, nombre: str, base_url: str) -> str:
    url_completa = f"{base_url.rstrip('/')}/n/{slug}"
    return _env.get_template("cartel.html").render(
        nombre=nombre,
        url=url_completa,
        qr=qr_data_uri(url_completa, box_size=14),
    )
