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
    "colonias": ("colonias.json", ("colonias.json",)),
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


# ---------- puntos por tipo y alcaldías (CO-012) ----------

TIPOS_PUNTO = ("tianguis", "mercado", "negocio_local")
PRIORITARIAS = ("09003", "09007")
TOPE_PUNTOS = 3000
TOPE_NEGOCIOS = 1500
NEGOCIOS_DENUE = "negocios_denue.json"  # CO-004; puede no existir


def _bbox(texto: str | None) -> tuple[float, float, float, float] | None:
    if not texto:
        return None
    try:
        a, b, c, d = (float(x) for x in texto.split(","))
    except ValueError:
        return None
    return min(a, c), min(b, d), max(a, c), max(b, d)


def _en_bbox(p: dict, caja: tuple[float, float, float, float] | None) -> bool:
    if caja is None:
        return True
    try:
        return caja[0] <= float(p["lng"]) <= caja[2] and caja[1] <= float(p["lat"]) <= caja[3]
    except (KeyError, TypeError, ValueError):
        return False


def _punto(p: dict, tipo: str) -> dict:
    return {
        "id": p.get("id"), "tipo": tipo, "nombre": p.get("nombre"),
        "alcaldia_cvegeo": p.get("alcaldia_cvegeo"), "colonia": p.get("colonia"),
        "lat": p.get("lat"), "lng": p.get("lng"),
        "dias": p.get("dias"), "abre": p.get("abre"), "cierra": p.get("cierra"),
        "tipo_dato": p.get("tipo_dato") or "simulado",
        "fuente": p.get("fuente") or "sin fuente registrada",
    }


def _negocios_locales(caja, alcaldia: str | None, tope: int) -> tuple[list[dict], int]:
    ruta = PROCESSED_DIR / NEGOCIOS_DENUE
    if not ruta.is_file():
        return [], 0
    try:
        datos = _leer_json(ruta)
    except (OSError, ValueError):
        return [], 0
    filas = datos if isinstance(datos, list) else (datos.get("negocios") or []) if isinstance(datos, dict) else []
    sel = [p for p in filas if isinstance(p, dict) and _en_bbox(p, caja)
           and (not alcaldia or p.get("alcaldia_cvegeo") == alcaldia)]
    return [_punto(p, "negocio_local") for p in sel[:tope]], len(sel)


def puntos(tipos: str | None, bbox: str | None, alcaldia: str | None = None, limite: int = TOPE_PUNTOS) -> dict:
    pedidos = [t.strip() for t in (tipos or "").split(",") if t.strip() in TIPOS_PUNTO] or list(TIPOS_PUNTO[:2])
    caja = _bbox(bbox)
    datos, origen = _cargar("tianguis")
    res: list[dict] = []
    total = 0
    for p in _lista(datos, "puntos") or _lista(datos, "tianguis"):
        tipo = p.get("tipo") or "tianguis"
        if tipo not in pedidos or not _en_bbox(p, caja):
            continue
        if alcaldia and p.get("alcaldia_cvegeo") != alcaldia:
            continue
        total += 1
        if len(res) < limite:
            res.append(_punto(p, tipo))
    if "negocio_local" in pedidos:
        neg, n = _negocios_locales(caja, alcaldia, min(TOPE_NEGOCIOS, max(0, limite - len(res))))
        res += neg
        total += n
    return {"puntos": res, "total": total, "truncado": total > len(res), "origen": origen, "tipos": pedidos}


def alcaldias() -> list[dict]:
    """16 alcaldías (colonias.json); 09003 y 09007 con prioridad: true van primero."""
    colonias, _ = _cargar("colonias")
    nombres: dict[str, str] = {}
    for c in _lista(colonias, "colonias"):
        if c.get("alcaldia_cvegeo") and c.get("alcaldia"):
            nombres.setdefault(c["alcaldia_cvegeo"], c["alcaldia"])
    pts, _ = _cargar("tianguis")
    cuenta: dict[str, dict[str, int]] = {}
    for p in _lista(pts, "puntos"):
        d = cuenta.setdefault(p.get("alcaldia_cvegeo"), {})
        d[p.get("tipo")] = d.get(p.get("tipo"), 0) + 1
    dinero = {d.get("cvegeo"): d for d in dinero_alcaldias()}
    filas = []
    for cve in sorted(nombres):
        din = dinero.get(cve)
        filas.append({
            "cvegeo": cve, "nombre": nombres[cve], "prioridad": cve in PRIORITARIAS,
            "puntos_por_tipo": cuenta.get(cve, {}),
            "tipo_dato": "real",
            "fuente": "data/processed/colonias.json y tianguis_abierto.json (datos abiertos CDMX)",
            "cnbv": ({"trimestre": din.get("trimestre"), "tpv_por_adulto": din.get("tpv_por_adulto"),
                      "tipo_dato": din.get("tipo_dato"), "fuente": din.get("fuente_url") or "CNBV (sin URL registrada)"}
                     if din else None),
        })
    filas.sort(key=lambda a: (not a["prioridad"], PRIORITARIAS.index(a["cvegeo"]) if a["prioridad"] else 0, a["nombre"]))
    return filas
