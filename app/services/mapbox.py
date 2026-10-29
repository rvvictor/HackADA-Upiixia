"""Orden de paradas a pie: Mapbox Optimization v1 `walking` si hay token; si no, vecino más cercano en línea recta."""

import math
from itertools import pairwise

import httpx

from app import config

OPTIMIZATION_URL = "https://api.mapbox.com/optimized-trips/v1/mapbox/walking/{coords}"
MAX_COORDS = 12  # límite de Optimization v1, incluido el origen
FACTOR_CALLE = 1.3  # distancia a pie ≈ línea recta × 1.3
METROS_POR_MINUTO = 80


def distancia_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lng1, lat2, lng2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def minutos_a_pie(metros_linea_recta: float) -> float:
    return metros_linea_recta * FACTOR_CALLE / METROS_POR_MINUTO


def _vecino_mas_cercano(origen: tuple[float, float], puntos: list[tuple[float, float]]) -> list[int]:
    pendientes, orden, actual = list(range(len(puntos))), [], origen
    while pendientes:
        siguiente = min(pendientes, key=lambda i: distancia_m(actual, puntos[i]))
        orden.append(siguiente)
        pendientes.remove(siguiente)
        actual = puntos[siguiente]
    return orden


def _linea_recta(origen, puntos, orden, regresar) -> dict:
    camino = [origen, *(puntos[i] for i in orden)] + ([origen] if regresar else [])
    metros = sum(distancia_m(a, b) for a, b in pairwise(camino)) * FACTOR_CALLE
    return {
        "orden": orden,
        "geometria": {"type": "LineString", "coordinates": [[lng, lat] for lat, lng in camino]},
        "distancia_m": round(metros),
        "minutos": round(metros / METROS_POR_MINUTO),
        "fuente": "linea_recta",
        "aviso": "Ruta aproximada en línea recta: sin conexión con Mapbox.",
    }


def ordenar(origen: tuple[float, float], puntos: list[tuple[float, float]], regresar: bool = True) -> dict:
    """Devuelve orden de las paradas (índices de `puntos`), geometría GeoJSON, distancia y minutos."""
    if not puntos:
        return {"orden": [], "geometria": None, "distancia_m": 0, "minutos": 0, "fuente": "vacia", "aviso": None}
    orden_local = _vecino_mas_cercano(origen, puntos)
    token = config.settings.mapbox_token
    if config.settings.demo_mode or not token or len(puntos) + 1 > MAX_COORDS:
        return _linea_recta(origen, puntos, orden_local, regresar)
    coords = ";".join(f"{lng},{lat}" for lat, lng in [origen, *puntos])
    params = {"access_token": token, "geometries": "geojson", "overview": "full", "source": "first",
              "roundtrip": str(regresar).lower()}
    if not regresar:
        params["destination"] = "any"
    try:
        r = httpx.get(OPTIMIZATION_URL.format(coords=coords), params=params, timeout=6)
        r.raise_for_status()
        datos = r.json()
        viaje = datos["trips"][0]
        # waypoints[i].waypoint_index es la posición de la coordenada i en el viaje; el 0 es el origen.
        posiciones = [w["waypoint_index"] for w in datos["waypoints"]][1:]
        orden = sorted(range(len(puntos)), key=lambda i: posiciones[i])
        return {
            "orden": orden,
            "geometria": viaje["geometry"],
            "distancia_m": round(viaje["distance"]),
            "minutos": round(viaje["duration"] / 60),
            "fuente": "mapbox",
            "aviso": None,
        }
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return _linea_recta(origen, puntos, orden_local, regresar)
