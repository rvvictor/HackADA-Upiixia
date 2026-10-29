"""Panel de crecimiento SEDECO: series simuladas (deterministas) + conteos reales de la plataforma.

Toda cifra viaja con `tipo_dato` (real | estimado | simulado) y `fuente`. Un archivo vivo
ausente o corrupto nunca rompe el panel: cuenta 0 (o vacío) y lo dice.
"""

import json
import random
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from app.config import LIVE_DIR, settings

TZ = ZoneInfo("America/Mexico_City")
TipoDato = Literal["real", "estimado", "simulado"]

NOMBRES_ALCALDIAS = {
    "09002": "Azcapotzalco",
    "09003": "Coyoacán",
    "09004": "Cuajimalpa de Morelos",
    "09005": "Gustavo A. Madero",
    "09006": "Iztacalco",
    "09007": "Iztapalapa",
    "09008": "La Magdalena Contreras",
    "09009": "Milpa Alta",
    "09010": "Álvaro Obregón",
    "09011": "Tláhuac",
    "09012": "Tlalpan",
    "09013": "Xochimilco",
    "09014": "Benito Juárez",
    "09015": "Cuauhtémoc",
    "09016": "Miguel Hidalgo",
    "09017": "Venustiano Carranza",
}

FUENTE_CNBV = (
    "Simulación con forma de la base de inclusión financiera CNBV (no son datos reales)"
)
FUENTE_DENUE = (
    "Simulación con forma de DENUE INEGI, campo Fecha_Alta (no son datos reales)"
)
FUENTE_ALTAS = "Plataforma colonIA · data/live/altas.jsonl"
FUENTE_EVENTOS = (
    "Plataforma colonIA · data/live/eventos.jsonl (eventos aparicion_ruta)"
)


class Punto(BaseModel):
    periodo: str
    valor: int


class SerieAlcaldia(BaseModel):
    alcaldia_cvegeo: str
    alcaldia: str
    indicador: str
    puntos: list[Punto]
    tipo_dato: TipoDato
    fuente: str


class AltasHoy(BaseModel):
    fecha: str
    hoy: int
    total: int
    tipo_dato: TipoDato
    fuente: str
    archivo_disponible: bool


class RutaHexagono(BaseModel):
    h3: str
    rutas: int


class RutasPorHexagono(BaseModel):
    hexagonos: list[RutaHexagono]
    total: int
    tipo_dato: TipoDato
    fuente: str
    archivo_disponible: bool


class Escala(BaseModel):
    alcaldias_activas: list[str]
    alcaldias_totales: int
    parametro: str
    costo: str
    piezas: list[str]
    tipo_dato: TipoDato
    fuente: str


class Crecimiento(BaseModel):
    generado: str
    alcaldias: list[str]
    serie_trimestral: list[SerieAlcaldia]
    altas_negocios_por_anio: list[SerieAlcaldia]
    altas_plataforma: AltasHoy
    rutas_por_hexagono: RutasPorHexagono
    escala: Escala
    demo_data: bool


def _rng(*semilla: str) -> random.Random:
    return random.Random("|".join(semilla))


def _serie_trimestral(cvegeo: str) -> list[Punto]:
    rng = _rng("cnbv", cvegeo)
    valor = rng.randint(180, 420)
    puntos = []
    for anio in (2023, 2024, 2025):
        for t in (1, 2, 3, 4):
            valor = max(50, int(valor * (1 + rng.uniform(-0.03, 0.07))))
            puntos.append(Punto(periodo=f"{anio}-T{t}", valor=valor))
    return puntos


def _altas_por_anio(cvegeo: str) -> list[Punto]:
    rng = _rng("denue", cvegeo)
    base = rng.randint(900, 2600)
    return [
        Punto(
            periodo=str(anio), valor=max(100, int(base * (1 + rng.uniform(-0.15, 0.2))))
        )
        for anio in range(2019, 2026)
    ]


def _leer_jsonl(path: Path) -> tuple[list[dict], bool]:
    if not path.is_file():
        return [], False
    filas: list[dict] = []
    try:
        with path.open(encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    fila = json.loads(linea)
                except json.JSONDecodeError:
                    continue
                if isinstance(fila, dict):
                    filas.append(fila)
    except OSError:
        return [], False
    return filas, True


def _es_demo(fila: dict) -> bool:
    return bool(fila.get("demo_data")) or fila.get("origen") == "demo"


def _fecha_local(ts: object) -> date | None:
    try:
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts / 1000 if ts > 1e11 else ts, tz=UTC)
        elif isinstance(ts, str):
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TZ)
        else:
            return None
    except (ValueError, OSError, OverflowError):
        return None
    return dt.astimezone(TZ).date()


def altas_hoy(live_dir: Path | None = None, hoy: date | None = None) -> AltasHoy:
    live_dir = live_dir or LIVE_DIR
    hoy = hoy or datetime.now(TZ).date()
    filas, disponible = _leer_jsonl(live_dir / "altas.jsonl")
    filas = [f for f in filas if not _es_demo(f)]
    n_hoy = sum(1 for fila in filas if _fecha_local(fila.get("ts")) == hoy)
    return AltasHoy(
        fecha=hoy.isoformat(),
        hoy=n_hoy,
        total=len(filas),
        tipo_dato="real",
        fuente=FUENTE_ALTAS,
        archivo_disponible=disponible,
    )


def rutas_por_hexagono(live_dir: Path | None = None) -> RutasPorHexagono:
    live_dir = live_dir or LIVE_DIR
    filas, disponible = _leer_jsonl(live_dir / "eventos.jsonl")
    conteo = Counter(
        str(f["h3"])
        for f in filas
        if f.get("tipo") == "aparicion_ruta" and f.get("h3") and not _es_demo(f)
    )
    hexagonos = [RutaHexagono(h3=h, rutas=n) for h, n in conteo.most_common(12)]
    return RutasPorHexagono(
        hexagonos=hexagonos,
        total=sum(conteo.values()),
        tipo_dato="real",
        fuente=FUENTE_EVENTOS,
        archivo_disponible=disponible,
    )


def escala(alcaldias: list[str]) -> Escala:
    return Escala(
        alcaldias_activas=[NOMBRES_ALCALDIAS.get(c, c) for c in alcaldias],
        alcaldias_totales=len(NOMBRES_ALCALDIAS),
        parametro="ALCALDIAS",
        costo="Casi cero: bot de Telegram gratuito, datos abiertos de la CDMX e INEGI, código abierto.",
        piezas=[
            "Telegram como canal de alta: sin app que instalar.",
            "Datos abiertos (DENUE, tianguis y mercados SEDECO) como base.",
            "Código abierto: cualquier alcaldía puede correrlo.",
            "Cambiar la variable ALCALDIAS agrega una alcaldía sin tocar código.",
        ],
        tipo_dato="estimado",
        fuente="Diseño de colonIA (estimación del equipo)",
    )


def crecimiento(
    alcaldias: list[str] | None = None,
    live_dir: Path | None = None,
    hoy: date | None = None,
) -> Crecimiento:
    alcaldias = alcaldias or settings.alcaldias_list
    nombre = lambda c: NOMBRES_ALCALDIAS.get(c, c)
    return Crecimiento(
        generado=datetime.now(TZ).isoformat(timespec="seconds"),
        alcaldias=alcaldias,
        serie_trimestral=[
            SerieAlcaldia(
                alcaldia_cvegeo=c,
                alcaldia=nombre(c),
                indicador="Cuentas de captación por cada 10 mil adultos",
                puntos=_serie_trimestral(c),
                tipo_dato="simulado",
                fuente=FUENTE_CNBV,
            )
            for c in alcaldias
        ],
        altas_negocios_por_anio=[
            SerieAlcaldia(
                alcaldia_cvegeo=c,
                alcaldia=nombre(c),
                indicador="Altas de negocios por año",
                puntos=_altas_por_anio(c),
                tipo_dato="simulado",
                fuente=FUENTE_DENUE,
            )
            for c in alcaldias
        ],
        altas_plataforma=altas_hoy(live_dir, hoy),
        rutas_por_hexagono=rutas_por_hexagono(live_dir),
        escala=escala(alcaldias),
        demo_data=settings.demo_mode,
    )
