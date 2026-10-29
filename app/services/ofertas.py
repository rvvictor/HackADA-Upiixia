"""Ofertas de ruta para repartidores de barrio (IDEA-v2 §4.3).

Orden de candidatos: prioridad DESC, cercanía ASC, antigüedad ASC. La prioridad decide quién ve
primero, nunca quién ve: el siguiente en la fila la ve `VENTANA_S` segundos después.
"""

import json
import time
import uuid
from pathlib import Path

from app.config import LIVE_DIR, settings
from app.services import repartidores

VENTANA_S = 60

DEMO = [
    {"id": "O-DEMO1", "negocio_id": "N-DEMO", "tipo_negocio": "fonda", "colonia": "San Lucas",
     "paradas": [{"lat": 19.3468, "lng": -99.1617, "colonia": "San Lucas"},
                 {"lat": 19.3490, "lng": -99.1590, "colonia": "San Lucas"}],
     "distancia_m": 850, "minutos_est": 12, "pago_est": 45, "tipo_dato_pago": "simulado"},
    {"id": "O-DEMO2", "negocio_id": "N-DEMO", "tipo_negocio": "panaderia", "colonia": "San Lucas",
     "paradas": [{"lat": 19.3471, "lng": -99.1620, "colonia": "San Lucas"}],
     "distancia_m": 400, "minutos_est": 6, "pago_est": 25, "tipo_dato_pago": "simulado"},
]


# Rutas fijas del repartidor demo (R-00001): se siembran la primera vez que entra, con o sin DEMO_MODE.
RUTAS_REPARTIDOR_DEMO = [
    {"id": "O-FIJA1", "negocio_id": "N-DEMO", "negocio_nombre": "Fonda Doña Lupe", "tipo_negocio": "negocio_local",
     "colonia": "San Lucas",
     "paradas": [{"lat": 19.3468, "lng": -99.1617, "colonia": "San Lucas"},
                 {"lat": 19.3490, "lng": -99.1590, "colonia": "San Lucas"}],
     "distancia_m": 850, "minutos_est": 12, "pago_est": 45, "tipo_dato_pago": "simulado"},
    {"id": "O-FIJA2", "negocio_id": "N-DEMO2", "negocio_nombre": "Panadería del mercado", "tipo_negocio": "mercado",
     "colonia": "San Lucas",
     "paradas": [{"lat": 19.3471, "lng": -99.1620, "colonia": "San Lucas"}],
     "distancia_m": 400, "minutos_est": 6, "pago_est": 25, "tipo_dato_pago": "simulado"},
    {"id": "O-FIJA3", "negocio_id": "N-DEMO3", "negocio_nombre": "Tianguis de San Lucas", "tipo_negocio": "tianguis",
     "colonia": "San Lucas",
     "paradas": [{"lat": 19.3455, "lng": -99.1632, "colonia": "San Lucas"},
                 {"lat": 19.3481, "lng": -99.1648, "colonia": "San Lucas"},
                 {"lat": 19.3502, "lng": -99.1611, "colonia": "San Lucas"}],
     "distancia_m": 1300, "minutos_est": 18, "pago_est": 60, "tipo_dato_pago": "simulado"},
    {"id": "O-FIJA4", "negocio_id": "N-DEMO", "negocio_nombre": "Fonda Doña Lupe", "tipo_negocio": "negocio_local",
     "colonia": "San Lucas", "estado": "completada",
     "paradas": [{"lat": 19.3462, "lng": -99.1605, "colonia": "San Lucas"}],
     "distancia_m": 600, "minutos_est": 8, "pago_est": 30, "tipo_dato_pago": "simulado"},
]


class NoEncontrada(Exception):
    pass


class TransicionInvalida(Exception):
    pass


# ---------- almacenamiento ----------

def _ruta() -> Path:
    return LIVE_DIR / "ofertas.jsonl"


def _todas() -> list[dict]:
    ruta = _ruta()
    if not ruta.is_file():
        return []
    filas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        try:
            filas.append(json.loads(linea))
        except ValueError:
            continue
    return [f for f in filas if isinstance(f, dict)]


def _guardar(filas: list[dict]) -> None:
    ruta = _ruta()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")


def crear(datos: dict, ahora: float | None = None) -> dict:
    filas = _todas()
    o = {"id": datos.get("id") or f"O-{uuid.uuid4().hex[:6].upper()}", "ts": ahora if ahora is not None else time.time(),
         "estado": "abierta", "repartidor_id": None, "demo_data": False, **datos}
    filas.append(o)
    _guardar(filas)
    return o


def _sembrar_demo(ahora: float) -> None:
    if settings.demo_mode and not _todas():
        for d in DEMO:
            crear({**d, "demo_data": True}, ahora=ahora - VENTANA_S * 10)


def _sembrar_rutas_repartidor_demo(ahora: float) -> None:
    hay = {o.get("id") for o in _todas()}
    for d in RUTAS_REPARTIDOR_DEMO:
        if d["id"] not in hay:
            extra = {"repartidor_id": repartidores.DEMO_ID} if d.get("estado") == "completada" else {}
            crear({**d, **extra, "demo_data": True}, ahora=ahora - 3600)


# ---------- orden ----------

def _cercania(r: dict, oferta: dict) -> int:
    """Posición de la colonia de la oferta en las colonias del repartidor (0 = la suya principal)."""
    colonias = r.get("colonias") or []
    return colonias.index(oferta.get("colonia")) if oferta.get("colonia") in colonias else len(colonias)


def ordenar_candidatos(candidatos: list[dict], oferta: dict) -> list[dict]:
    return sorted(candidatos, key=lambda r: (-(r.get("prioridad") or 0), _cercania(r, oferta), r.get("ts_alta") or 0))


def candidatos(oferta: dict) -> list[dict]:
    activos = [r for r in repartidores.todos()
               if r.get("estado") != "rechazado" and oferta.get("colonia") in (r.get("colonias") or [])]
    return ordenar_candidatos(activos, oferta)


def visible_desde(oferta: dict, rid: str) -> float | None:
    """Momento en que `rid` ve la oferta según su lugar en la fila; None si no es de su barrio."""
    ids = [r["id"] for r in candidatos(oferta)]
    if rid not in ids:
        return None
    return (oferta.get("ts") or 0) + ids.index(rid) * VENTANA_S


def ofertas_para(rid: str, desde: float | None = None, ahora: float | None = None) -> list[dict]:
    repartidores.obtener(rid)
    ahora = ahora if ahora is not None else time.time()
    _sembrar_demo(ahora)
    if repartidores.DEMO_CODIGO and rid == repartidores.DEMO_ID:
        _sembrar_rutas_repartidor_demo(ahora)
    visibles = []
    for o in _todas():
        if o.get("estado") in ("tomada", "completada"):
            if o.get("repartidor_id") == rid:
                visibles.append(o)
            continue
        if o.get("estado") != "abierta" or (desde is not None and (o.get("ts") or 0) < desde):
            continue
        t = visible_desde(o, rid)
        if t is not None and t <= ahora:
            visibles.append(o)
    return sorted(visibles, key=lambda o: (o.get("distancia_m") or 0, o.get("ts") or 0))


# ---------- estados ----------

def _cambiar(oid: str, rid: str, de: str, a: str, ahora: float) -> dict:
    filas = _todas()
    for o in filas:
        if o.get("id") != oid:
            continue
        if o.get("estado") != de:
            raise TransicionInvalida(f"la oferta está {o.get('estado')}")
        if de == "abierta":
            t = visible_desde(o, rid)
            if t is None or t > ahora:
                raise TransicionInvalida("la oferta aún no está disponible para ti")
            o["repartidor_id"] = rid
        elif o.get("repartidor_id") != rid:
            raise TransicionInvalida("la oferta la tomó otro repartidor")
        o["estado"] = a
        o[f"ts_{a}"] = ahora
        _guardar(filas)
        return o
    raise NoEncontrada(oid)


def tomar(oid: str, rid: str, ahora: float | None = None) -> dict:
    return _cambiar(oid, rid, "abierta", "tomada", ahora if ahora is not None else time.time())


def completar(oid: str, rid: str, ahora: float | None = None) -> dict:
    o = _cambiar(oid, rid, "tomada", "completada", ahora if ahora is not None else time.time())
    r = repartidores.obtener(rid)
    repartidores.actualizar(rid, rutas_completadas=(r.get("rutas_completadas") or 0) + 1)
    return o
