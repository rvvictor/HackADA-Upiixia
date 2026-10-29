"""Eventos de la plataforma en data/live/eventos.jsonl (IDEA.md §6). Único escritor: este módulo (OWNERS.md)."""

import json
import time
from pathlib import Path

from app import config

TIPOS = {"busqueda", "aparicion_ruta", "compre_aqui", "vista_pagina", "alta"}


def _archivo() -> Path:
    return config.LIVE_DIR / "eventos.jsonl"


def registrar(tipo: str, negocio_id: str | None = None, h3: str | None = None, demo_data: bool = False) -> dict:
    if tipo not in TIPOS:
        raise ValueError(f"tipo de evento desconocido: {tipo}")
    evento = {"ts": time.time(), "tipo": tipo, "negocio_id": negocio_id, "h3": h3, "demo_data": demo_data}
    archivo = _archivo()
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with archivo.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    return evento


def leer() -> list[dict]:
    archivo = _archivo()
    if not archivo.exists():
        return []
    eventos = []
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        try:
            eventos.append(json.loads(linea))
        except json.JSONDecodeError:
            continue
    return eventos
