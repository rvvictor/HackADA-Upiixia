"""Ruta de compras de barrio (IDEA.md A.6): candidatos, puntaje, desvío máximo, cobertura voraz y orden a pie.

Invariante: ninguna parada es una cadena. Si alguna lo fuera, se lanza RutaConCadena y la API responde 500.
"""

import json
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

import h3

from app import config
from app.services import eventos, mapbox
from app.services.articulos import interpretar
from pipeline.articulos.__main__ import normalizar

MAX_PARADAS = 10
DESVIO_MAX_MIN = 5
ZONA = ZoneInfo("America/Mexico_City")

# Giros de tianguis → clase SCIAN (los giros vienen en texto libre en tianguis_abierto.json).
GIRO_A_CLASE = {
    "abarrotes": "461110", "recauderia": "461130", "frutas y verduras": "461130", "tortilleria": "311830",
    "panaderia": "311812", "carniceria": "461121", "polleria": "461122", "cremeria": "461150",
    "chiles y semillas": "461140", "ferreteria": "467111", "papeleria": "465311", "zapateria": "463310",
    "calzado": "463310", "ropa": "463211", "farmacia": "464111", "fonda": "722519", "tacos": "722514",
    "estetica": "812110", "dulceria": "461160",
}


class RutaConCadena(RuntimeError):
    pass


def _leer(nombre: str):
    archivo = config.PROCESSED_DIR / nombre
    return json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else None


@lru_cache(maxsize=1)
def _impulso_por_hex() -> tuple[dict[str, float], float]:
    datos = _leer("hex.geojson")
    impulso = {f["properties"]["h3"]: f["properties"].get("impulso") or 0.0 for f in (datos or {}).get("features", [])}
    valores = sorted(v for v in impulso.values() if v > 0)
    p70 = valores[int(len(valores) * 0.7)] if valores else 1.0
    return impulso, p70


@lru_cache(maxsize=1)
def _negocios() -> list[dict]:
    return [n for n in (_leer("negocios.json") or []) if n.get("es_barrial")]


@lru_cache(maxsize=1)
def _tianguis() -> list[dict]:
    return _leer("tianguis_abierto.json") or []


def _altas() -> list[dict]:
    """Altas en vivo del bot (data/live/altas.jsonl): se leen cada vez para que aparezcan en la ruta al momento."""
    archivo = config.LIVE_DIR / "altas.jsonl"
    if not archivo.exists():
        return []
    altas = []
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        try:
            a = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if a.get("ficha") and a.get("lat") is not None and a.get("consentimiento_publicar", True):
            altas.append(a)
    return altas


def _abierto(dias: list[int] | None, abre: str | None, cierra: str | None, dia: int, hora: str) -> bool:
    if dias is not None and dia not in dias:
        return False
    return not abre or not cierra or abre <= hora < cierra


def _lugares(dia: int, hora: str) -> list[dict]:
    """Todos los lugares de barrio posibles, con lo que venden en forma comparable."""
    lugares = []
    for n in _negocios():
        lugares.append({
            "id": n["id"], "nombre": n["nombre"], "tipo": "negocio", "giro": n["clase_nombre"],
            "lat": n["lat"], "lng": n["lng"], "h3": n["h3"], "clases": {n["clase_scian"]}, "productos": set(),
            "formas_pago": n.get("formas_pago", []), "acepta_mercomuna": n.get("acepta_mercomuna"),
            "es_barrial": True, "tipo_dato": n.get("tipo_dato", "simulado"), "horario_verificado": False,
        })
    for t in _tianguis():
        if not _abierto(t.get("dias"), t.get("abre"), t.get("cierra"), dia, hora):
            continue
        clases = {GIRO_A_CLASE[g] for g in map(normalizar, t.get("giros", [])) if g in GIRO_A_CLASE}
        lugares.append({
            "id": t["id"], "nombre": t["nombre"], "tipo": t.get("tipo", "tianguis"), "giro": ", ".join(t.get("giros", [])),
            "lat": t["lat"], "lng": t["lng"], "h3": t.get("h3"), "clases": clases,
            "productos": {normalizar(p) for p in t.get("productos", [])},
            "formas_pago": t.get("formas_pago", []), "acepta_mercomuna": t.get("acepta_mercomuna"),
            "es_barrial": True, "tipo_dato": t.get("tipo_dato", "simulado"), "horario_verificado": True,
        })
    for a in _altas():
        f = a["ficha"]
        if not _abierto(f.get("dias") or None, f.get("abre"), f.get("cierra"), dia, hora):
            continue
        lugares.append({
            "id": a["id"], "nombre": f.get("nombre", "Puesto de barrio"), "tipo": "alta", "giro": f.get("clase_scian", ""),
            "lat": a["lat"], "lng": a["lng"], "h3": a.get("h3") or h3.latlng_to_cell(a["lat"], a["lng"], 9),
            "clases": {f["clase_scian"]} if f.get("clase_scian") else set(),
            "productos": {normalizar(p["nombre"] if isinstance(p, dict) else p) for p in f.get("productos", [])},
            "formas_pago": f.get("formas_pago", []), "acepta_mercomuna": f.get("acepta_mercomuna"),
            "es_barrial": True, "tipo_dato": "real" if not a.get("demo_data") else "simulado", "horario_verificado": True,
        })
    return lugares


def _cubre(lugar: dict, item: dict) -> bool:
    return item["articulo"] in lugar["productos"] or bool(lugar["clases"] & set(item["clases"]))


def _ahora() -> tuple[int, str]:
    ahora = datetime.now(ZONA)
    return ahora.weekday(), ahora.strftime("%H:%M")


def armar_ruta(origen: dict, texto_lista: str, dia: int | None = None, hora: str | None = None,
               radio_m: int = 1500, alpha: float = 0.6, regresar: bool = True) -> dict:
    dia_ahora, hora_ahora = _ahora()
    dia = dia_ahora if dia is None else dia
    hora = hora or hora_ahora
    o = (origen["lat"], origen["lng"])
    impulso, p70 = _impulso_por_hex()
    interpretado = interpretar(texto_lista)
    items = interpretado["items"]
    sin_resultado = list(interpretado["sin_resultado"])

    # 1-3. Candidatos a ≤ radio con tiempo a pie y puntaje.
    cercanos = []
    for lugar in _lugares(dia, hora):
        d = mapbox.distancia_m(o, (lugar["lat"], lugar["lng"]))
        if d <= radio_m:
            cercanos.append({**lugar, "t": mapbox.minutos_a_pie(d), "impulso": impulso.get(lugar["h3"], 0.0)})
    t_max = max((c["t"] for c in cercanos), default=1.0) or 1.0
    for c in cercanos:
        c["puntaje"] = alpha * (1 - c["t"] / t_max) + (1 - alpha) * c["impulso"]

    # 4. Por artículo, solo cuentan los lugares a ≤ 5 min más que el más cercano que lo vende.
    elegibles: dict[int, list[dict]] = {}
    for i, item in enumerate(items):
        opciones = [c for c in cercanos if _cubre(c, item)]
        if not opciones:
            sin_resultado.append(item["texto"])
            continue
        t_min = min(c["t"] for c in opciones)
        elegibles[i] = [c for c in opciones if c["t"] <= t_min + DESVIO_MAX_MIN]

    # 5. Cobertura voraz: el lugar que cubre más artículos pendientes por su puntaje.
    pendientes, paradas = set(elegibles), []
    while pendientes and len(paradas) < MAX_PARADAS:
        por_lugar: dict[str, tuple[dict, set[int]]] = {}
        for i in pendientes:
            for c in elegibles[i]:
                por_lugar.setdefault(c["id"], (c, set()))[1].add(i)
        lugar, cubiertos = max(por_lugar.values(), key=lambda lc: (len(lc[1]) * lc[0]["puntaje"], -lc[0]["t"]))
        paradas.append((lugar, sorted(cubiertos)))
        pendientes -= cubiertos

    # 10. Invariante: nunca una cadena.
    if not all(lugar["es_barrial"] for lugar, _ in paradas):
        raise RutaConCadena("una parada no es de barrio")

    # 6. Orden a pie.
    viaje = mapbox.ordenar(o, [(lugar["lat"], lugar["lng"]) for lugar, _ in paradas], regresar)
    resultado = []
    for posicion, idx in enumerate(viaje["orden"], start=1):
        lugar, cubiertos = paradas[idx]
        articulos = [items[i]["texto"] for i in cubiertos]
        resultado.append({
            "orden": posicion,
            "negocio": {k: lugar[k] for k in ("id", "nombre", "tipo", "giro", "lat", "lng", "h3", "formas_pago",
                                              "acepta_mercomuna", "tipo_dato", "horario_verificado")}
                       | {"impulso": round(lugar["impulso"], 2)},
            "articulos": articulos,
            "por_que": _por_que(lugar, len(articulos), p70),
        })
        eventos.registrar("aparicion_ruta", lugar["id"], lugar["h3"])
    eventos.registrar("busqueda", None, None)

    con_impulso = sum(1 for p in resultado if p["negocio"]["impulso"] >= p70 and p["negocio"]["impulso"] > 0)
    return {
        "paradas": resultado,
        "geometria": viaje["geometria"],
        "distancia_m": viaje["distancia_m"],
        "minutos": viaje["minutos"],
        "resumen": {"barrial_pct": 100 if resultado else 0, "cadenas": 0, "paradas_impulso": con_impulso},
        "sin_resultado": sin_resultado,
        "aviso": viaje["aviso"],
        "demo_data": any(p["negocio"]["tipo_dato"] == "simulado" for p in resultado),
    }


def _por_que(lugar: dict, n_articulos: int, p70: float) -> list[str]:
    """Razones con datos calculados, nunca LLM (A.6 paso 7)."""
    razones = []
    if lugar["impulso"] >= p70 and lugar["impulso"] > 0:
        razones.append(f"Zona con poco movimiento de pago digital (impulso {lugar['impulso']:.2f}, estimado)")
    razones.append(f"Cubre {n_articulos} de tus artículos" if n_articulos > 1 else "Tiene lo que buscas")
    razones.append(f"A {round(lugar['t'])} min a pie")
    if lugar["tipo"] == "alta":
        razones.append("Se sumó hoy a la red de barrio")
    elif lugar["tipo"] in {"tianguis", "mercado"}:
        razones.append(f"{lugar['tipo'].capitalize()} abierto ahora")
    if lugar.get("acepta_mercomuna"):
        razones.append("Acepta Mercomuna")
    return razones
