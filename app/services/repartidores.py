"""Repartidores de barrio: alta, acceso por código de 6 dígitos, sesión corta e incentivos (IDEA-v2 §4).

La foto de identificación y la prioridad nunca salen de aquí: `publico()` es lo único que ven los routers.
"""

import hashlib
import json
import random
import secrets
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from app.config import LIVE_DIR, PROCESSED_DIR, settings

Transporte = Literal["bici", "bici_electrica", "a_pie", "scooter_electrico", "moto", "auto"]
ECOLOGICOS = {"bici", "bici_electrica", "a_pie", "scooter_electrico"}

# Peso de §4.3: 18–30 años y estudiante suman un punto cada uno (0–2). Prioriza, nunca excluye.
PESO_EDAD_JOVEN = 1
PESO_ESTUDIANTE = 1
CODIGO_TTL_S = 10 * 60
SESION_TTL_S = 30 * 60
# Campos que nunca salen en una respuesta (§4.5).
PRIVADOS = {"prioridad", "chat_id_hash", "foto_id_ruta", "edad", "rango_edad", "estudiante"}

_codigos: dict[str, tuple[str, float]] = {}
_sesiones: dict[str, tuple[str, float]] = {}


class Disponibilidad(BaseModel):
    dias: list[str] = []
    desde: str = "09:00"
    hasta: str = "18:00"


class RepartidorIn(BaseModel):
    nombre_mostrar: str = Field(min_length=1, max_length=60)
    edad: int = Field(ge=18, le=99)
    estudiante: bool
    alcaldia_cvegeo: str
    colonias: list[str] = Field(min_length=1, max_length=3)
    transporte: Transporte
    disponibilidad: Disponibilidad = Disponibilidad()
    tipo_id: str | None = None
    chat_id: str | None = None
    negocio_id: str | None = None
    foto_id_b64: str | None = None
    demo_data: bool = False


class NoEncontrado(Exception):
    pass


class AccesoInvalido(Exception):
    pass


def calcular_prioridad(edad: int, estudiante: bool) -> int:
    return (PESO_EDAD_JOVEN if 18 <= edad <= 30 else 0) + (PESO_ESTUDIANTE if estudiante else 0)


def publico(r: dict) -> dict:
    return {k: v for k, v in r.items() if k not in PRIVADOS}


# ---------- almacenamiento ----------

def _ruta() -> Path:
    return LIVE_DIR / "repartidores.jsonl"


def _todos() -> list[dict]:
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


def todos() -> list[dict]:
    """Uso interno del backend (ofertas): incluye prioridad. Nunca devolverlo tal cual."""
    return _todos()


def obtener(rid: str) -> dict:
    for r in _todos():
        if r.get("id") == rid:
            return r
    raise NoEncontrado(rid)


def actualizar(rid: str, **cambios) -> dict:
    filas = _todos()
    for r in filas:
        if r.get("id") == rid:
            r.update(cambios)
            _guardar(filas)
            return r
    raise NoEncontrado(rid)


# ---------- alta ----------

def _nuevo_id(existentes: set[str]) -> str:
    while True:
        rid = f"R-{random.randint(0, 99999):05d}"
        if rid not in existentes:
            return rid


def crear(entrada: RepartidorIn, ahora: float | None = None) -> dict:
    filas = _todos()
    rid = _nuevo_id({f.get("id") for f in filas})
    foto_ruta = None
    if entrada.foto_id_b64:
        # Fuera de git (data/live/ está ignorado); se borra al verificar y solo queda id_verificada.
        ids = LIVE_DIR / "ids"
        ids.mkdir(parents=True, exist_ok=True)
        foto_ruta = str(ids / f"{rid}.b64")
        Path(foto_ruta).write_text(entrada.foto_id_b64, encoding="utf-8")
    r = {
        "id": rid,
        "ts_alta": ahora if ahora is not None else time.time(),
        "chat_id_hash": hashlib.sha256(entrada.chat_id.encode()).hexdigest() if entrada.chat_id else None,
        "nombre_mostrar": entrada.nombre_mostrar,
        "rango_edad": "18-30" if entrada.edad <= 30 else "31+",
        "estudiante": entrada.estudiante,
        "alcaldia_cvegeo": entrada.alcaldia_cvegeo,
        "colonias": entrada.colonias,
        "transporte": entrada.transporte,
        "transporte_ecologico": entrada.transporte in ECOLOGICOS,
        "disponibilidad": entrada.disponibilidad.model_dump(),
        "id_verificada": False,
        "tipo_id": entrada.tipo_id,
        "foto_id_ruta": foto_ruta,
        "estado": "pendiente_verificacion",
        "negocio_id": entrada.negocio_id,
        "prioridad": calcular_prioridad(entrada.edad, entrada.estudiante),
        "rutas_completadas": 0,
        "demo_data": entrada.demo_data,
    }
    filas.append(r)
    _guardar(filas)
    return r


# ---------- acceso: código de 6 dígitos → sesión corta ----------

def pedir_codigo(rid: str, ahora: float | None = None) -> str:
    """Genera el código que el bot entrega por Telegram."""
    obtener(rid)
    codigo = f"{secrets.randbelow(10**6):06d}"
    _codigos[rid] = (codigo, (ahora or time.time()) + CODIGO_TTL_S)
    return codigo


def abrir_sesion(rid: str, codigo: str | None = None, ahora: float | None = None) -> dict:
    """Sin `codigo` basta un número de repartidor que exista (decisión del equipo para la demo, CO-026)."""
    ahora = ahora or time.time()
    if codigo is None:
        try:
            obtener(rid)
        except NoEncontrado:
            raise AccesoInvalido("número de repartidor no encontrado") from None
    else:
        guardado = _codigos.get(rid)
        if not guardado or guardado[1] < ahora or not secrets.compare_digest(guardado[0], codigo):
            raise AccesoInvalido("código inválido o vencido")
        del _codigos[rid]  # un solo uso
    token = secrets.token_urlsafe(24)
    _sesiones[token] = (rid, ahora + SESION_TTL_S)
    return {"token": token, "repartidor_id": rid, "expira": ahora + SESION_TTL_S}


def repartidor_de_sesion(token: str | None, ahora: float | None = None) -> str:
    sesion = _sesiones.get(token or "")
    if not sesion or sesion[1] < (ahora or time.time()):
        raise AccesoInvalido("sesión inválida o vencida")
    return sesion[0]


# ---------- incentivos ----------

INCENTIVOS_DEMO = [
    {"id": "casco", "nombre": "Casco", "descripcion": "Casco certificado para ciclista.", "rutas_requeridas": 10,
     "destacado": False, "imagen": None, "estado": "propuesta", "tipo_dato": "simulado"},
    {"id": "luces", "nombre": "Luces delantera y trasera", "descripcion": "Para rodar seguro de noche.",
     "rutas_requeridas": 15, "destacado": False, "imagen": None, "estado": "propuesta", "tipo_dato": "simulado"},
    {"id": "mochila", "nombre": "Mochila térmica", "descripcion": "Mantiene la comida a buena temperatura.",
     "rutas_requeridas": 25, "destacado": False, "imagen": None, "estado": "propuesta", "tipo_dato": "simulado"},
    {"id": "bici", "nombre": "Bici urbana", "descripcion": "Tu propia bici para repartir en el barrio.",
     "rutas_requeridas": 100, "destacado": True, "imagen": None, "estado": "propuesta", "tipo_dato": "simulado"},
]


def incentivos() -> list[dict]:
    """Catálogo con el destacado (la bici) primero; luego por rutas requeridas."""
    ruta = PROCESSED_DIR / "incentivos.json"
    catalogo = INCENTIVOS_DEMO
    if ruta.is_file():
        try:
            leido = json.loads(ruta.read_text(encoding="utf-8"))
            if isinstance(leido, list) and leido:
                catalogo = leido
        except ValueError:
            pass
    return sorted(catalogo, key=lambda i: (not i.get("destacado"), i.get("rutas_requeridas") or 0))


def avance(r: dict) -> list[dict]:
    hechas = r.get("rutas_completadas") or 0
    return [{"id": i["id"], "rutas_requeridas": i["rutas_requeridas"],
             "avance": min(1.0, hechas / i["rutas_requeridas"]) if i.get("rutas_requeridas") else 1.0}
            for i in incentivos()]


def reiniciar_accesos() -> None:
    """Para pruebas."""
    _codigos.clear()
    _sesiones.clear()


def demo_mode() -> bool:
    return bool(settings.demo_mode)
