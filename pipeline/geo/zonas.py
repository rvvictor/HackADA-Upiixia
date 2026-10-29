"""Zona de demo: alcaldías, polígonos aproximados y totales simulados.

Los polígonos son contornos simplificados escritos a mano a partir de la
ubicación general de cada alcaldía. NO son los límites oficiales del Marco
Geoestadístico (INEGI). Sirven para generar una rejilla de demo; la versión
real debe leer la capa municipal oficial (ver data/fuentes/geo.md).

Los totales (población, adultos, transacciones TPV) son SIMULADOS. No son
cifras del Censo 2020 ni de la CNBV.

Los vértices van como (lat, lng), el mismo orden que usa `h3.LatLngPoly`.
"""

from __future__ import annotations

ALCALDIAS: dict[str, dict] = {
    "09003": {
        "nombre": "Coyoacán",
        # Totales simulados (orden de magnitud, no cifras oficiales).
        "poblacion_total": 620_000,
        "adultos": 470_000,
        "transacciones_tpv": 1_850_000,
        # Personas por negocio barrial simulado (más negocios por persona que Iztapalapa).
        "personas_por_negocio": 60,
    },
    "09007": {
        "nombre": "Iztapalapa",
        "poblacion_total": 1_850_000,
        "adultos": 1_400_000,
        "transacciones_tpv": 2_300_000,
        "personas_por_negocio": 110,
    },
}

POLIGONOS: dict[str, list[tuple[float, float]]] = {
    "09003": [
        (19.2990, -99.2000),
        (19.2870, -99.1950),
        (19.2800, -99.1700),
        (19.2790, -99.1450),
        (19.2870, -99.1250),
        (19.3050, -99.1190),
        (19.3290, -99.1230),
        (19.3450, -99.1330),
        (19.3580, -99.1450),
        (19.3580, -99.1750),
        (19.3470, -99.1950),
        (19.3270, -99.2050),
        (19.3100, -99.2060),
    ],
    "09007": [
        (19.2790, -99.1450),
        (19.2870, -99.1250),
        (19.3050, -99.1190),
        (19.3290, -99.1230),
        (19.3450, -99.1080),
        (19.3600, -99.0950),
        (19.3650, -99.0700),
        (19.3700, -99.0500),
        (19.3720, -99.0300),
        (19.3600, -99.0150),
        (19.3400, -99.0100),
        (19.3150, -99.0100),
        (19.2950, -99.0150),
        (19.2750, -99.0200),
        (19.2600, -99.0300),
        (19.2550, -99.0600),
        (19.2650, -99.0900),
        (19.2760, -99.1200),
    ],
}
