"""Datos del mapa SEDECO: hexágonos, dinero por alcaldía, tianguis abiertos, cobertura y resumen.

Lee `data/processed/`; si falta un archivo usa el fixture de `app/fixtures/` y, si tampoco existe,
devuelve una respuesta vacía válida. Nunca lanza un 500 por un archivo ausente.
Días: 0 = lunes … 6 = domingo (misma convención que `pipeline.geo`).
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import h3

from app.config import FIXTURES_DIR, LIVE_DIR, PROCESSED_DIR

ZONA = ZoneInfo("America/Mexico_City")
RADIO_COBERTURA_M = 800
CAMPOS_DINERO = ("actividad_tpv_est", "monto_est")
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")

# nombre lógico → (archivo procesado, fixtures candidatos)
ARCHIVOS = {
    "hex": ("hex.geojson", ("hex.geojson", "hex.json")),
    "dinero": ("cnbv_tpv_municipios.json", ("dinero_alcaldias.json", "cnbv_tpv_municipios.json")),
    "tianguis": ("tianguis_abierto.json", ("tianguis.json", "tianguis_abierto.json")),
}

_cache: dict[Path, tuple[float, Any]] = {}


def _leer_json(ruta: Path) -> Any:
    mtime = ruta.stat().st_mtime
    hit = _cache.get(ruta)
    if hit and hit[0] == mtime:
        return hit[1]
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    _cache[ruta] = (mtime, datos)
    return datos


def _cargar(nombre: str) -> tuple[Any, str]:
    """Devuelve (datos, origen) con origen ∈ {processed, fixture, vacio}."""
    procesado, fixtures = ARCHIVOS[nombre]
    candidatos = [(PROCESSED_DIR / procesado, "processed")]
    candidatos += [(FIXTURES_DIR / f, "fixture") for f in fixtures]
    for ruta, origen in candidatos:
        if ruta.is_file():
            try:
                return _leer_json(ruta), origen
            except (OSError, ValueError):
                continue
    return None, "vacio"


def _lista(datos: Any, clave: str) -> list[dict]:
    """Acepta una lista o un objeto que la envuelve (p. ej. un fixture de respuesta)."""
    if isinstance(datos, list):
        return datos
    if isinstance(datos, dict) and isinstance(datos.get(clave), list):
        return datos[clave]
    return []


# ---------- hexágonos ----------

def _features() -> list[dict]:
    datos, _ = _cargar("hex")
    return _lista(datos, "features")


def hexagonos() -> dict:
    datos, origen = _cargar("hex")
    features = []
    for f in _lista(datos, "features"):
        props = dict(f.get("properties") or {})
        if props.get("oculto"):
            for campo in CAMPOS_DINERO:
                props[campo] = None
        features.append({**f, "properties": props})
    meta = dict(datos.get("meta") or {}) if isinstance(datos, dict) else {}
    meta["origen"] = origen
    return {"type": "FeatureCollection", "meta": meta, "features": features}


# ---------- dinero por alcaldía ----------

def dinero_alcaldias() -> list[dict]:
    datos, _ = _cargar("dinero")
    return _lista(datos, "alcaldias")


# ---------- tianguis por día y hora ----------

def ahora() -> tuple[int, str]:
    n = datetime.now(ZONA)
    return n.weekday(), n.strftime("%H:%M")


def _hhmm(valor: str | None, defecto: str) -> str:
    try:
        h, m = (valor or defecto).split(":")[:2]
        return f"{int(h):02d}:{int(m):02d}"
    except ValueError:
        return defecto


def esta_abierto(punto: dict, dia: int, hora: str) -> bool:
    if dia not in (punto.get("dias") or []):
        return False
    abre = _hhmm(punto.get("abre"), "07:00")
    cierra = _hhmm(punto.get("cierra"), "18:00")
    return abre <= hora < cierra


def _distancia_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _centro(props: dict) -> tuple[float, float] | None:
    try:
        return h3.cell_to_latlng(props["h3"])
    except (KeyError, ValueError, TypeError):
        return None


def cobertura(abiertos: list[dict]) -> dict:
    """Población de hexágonos cuyo centro cae a ≤ 800 m de un punto abierto, y desiertos del día.

    Desierto = hexágono con población ≥ mediana sin ningún punto abierto a 800 m (A.4).
    """
    hexes = []
    for f in _features():
        props = f.get("properties") or {}
        centro = _centro(props)
        if centro is not None:
            hexes.append((props.get("h3"), props.get("poblacion") or 0, centro))
    total = sum(p for _, p, _ in hexes)
    poblaciones = sorted(p for _, p, _ in hexes)
    mediana = poblaciones[len(poblaciones) // 2] if poblaciones else 0
    puntos = [(p["lat"], p["lng"]) for p in abiertos if p.get("lat") is not None and p.get("lng") is not None]

    cubierta, desiertos = 0, []
    for h, pob, (lat, lng) in hexes:
        cerca = any(
            abs(lat - plat) < 0.01 and _distancia_m(lat, lng, plat, plng) <= RADIO_COBERTURA_M
            for plat, plng in puntos
        )
        if cerca:
            cubierta += pob
        elif pob >= mediana and pob > 0:
            desiertos.append(h)
    return {
        "poblacion_total": total,
        "poblacion_cubierta": cubierta,
        "poblacion_cubierta_pct": round(100 * cubierta / total, 1) if total else 0.0,
        "desiertos": desiertos,
        "radio_m": RADIO_COBERTURA_M,
        "tipo_dato": "estimado",
        "metodo": "Población de hexágonos cuyo centro está a ≤ 800 m en línea recta de un punto abierto",
    }


def tianguis(dia: int | None = None, hora: str | None = None) -> dict:
    dia_actual, hora_actual = ahora()
    dia = dia_actual if dia is None else dia
    hora = _hhmm(hora, hora_actual)
    datos, origen = _cargar("tianguis")
    puntos = [{**p, "abierto": esta_abierto(p, dia, hora)} for p in _lista(datos, "puntos")]
    abiertos = [p for p in puntos if p["abierto"]]
    return {
        "dia": dia,
        "dia_nombre": DIAS[dia],
        "hora": hora,
        "total": len(puntos),
        "abiertos": len(abiertos),
        "puntos": puntos,
        "cobertura": cobertura(abiertos),
        "origen": origen,
    }


# ---------- resumen SEDECO ----------

def _jsonl(nombre: str) -> list[dict]:
    ruta = LIVE_DIR / nombre
    if not ruta.is_file():
        return []
    filas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        try:
            fila = json.loads(linea)
        except ValueError:
            continue
        if isinstance(fila, dict):
            filas.append(fila)
    return filas


def _fecha(ts: Any) -> str | None:
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, ZONA).date().isoformat()
        d = datetime.fromisoformat(str(ts))
        return (d.astimezone(ZONA) if d.tzinfo else d).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


def resumen(dia: int | None = None, hora: str | None = None) -> dict:
    hoy = datetime.now(ZONA).date().isoformat()
    altas = [a for a in _jsonl("altas.jsonl") if _fecha(a.get("ts")) == hoy]
    rutas: dict[str, int] = {}
    for e in _jsonl("eventos.jsonl"):
        if e.get("tipo") == "aparicion_ruta" and e.get("h3"):
            rutas[e["h3"]] = rutas.get(e["h3"], 0) + 1
    dia_tianguis = tianguis(dia, hora)
    return {
        "altas_hoy": len(altas),
        "rutas_por_hexagono": rutas,
        "dia": dia_tianguis["dia"],
        "hora": dia_tianguis["hora"],
        "abiertos": dia_tianguis["abiertos"],
        "poblacion_cubierta_pct": dia_tianguis["cobertura"]["poblacion_cubierta_pct"],
        "desiertos": len(dia_tianguis["cobertura"]["desiertos"]),
        "tipo_campos": {
            "altas_hoy": "real",
            "rutas_por_hexagono": "real",
            "poblacion_cubierta_pct": "estimado",
            "desiertos": "estimado",
        },
    }
