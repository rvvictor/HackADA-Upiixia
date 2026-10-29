"""Altas de negocios en vivo (bot de Telegram, equipo de campo o demo).

Voz → transcripción → ficha con salida estructurada → el comerciante confirma → `data/live/altas.jsonl`.
Sin llave de OpenAI o con `DEMO_MODE=1` se usan la transcripción y la ficha grabadas de Doña Lupe.
Días: 0 = lunes … 6 = domingo (misma convención que `pipeline.geo` y `/api/tianguis`).
"""

import json
import logging
import math
import re
import time
import unicodedata
from pathlib import Path
from typing import Literal

import h3
from pydantic import BaseModel, Field, ValidationError

from app.config import LIVE_DIR, PROCESSED_DIR, settings

log = logging.getLogger(__name__)
FIXTURES = Path(__file__).resolve().parent.parent / "bot" / "fixtures"
RADIO_TIANGUIS_M = 150

FormaPago = Literal["efectivo", "transferencia", "dimo", "codi", "tarjeta"]

# Giros de barrio que el LLM puede elegir (lista cerrada): las clases barriales de data/processed/negocios.json
# (PB-005), sin las de cadenas (462111, 462112, 462210). "999999" = ninguna de la lista.
GIROS: dict[str, str] = {
    "461110": "Abarrotes, ultramarinos y misceláneas",
    "461121": "Carnicería",
    "461122": "Pollería",
    "461130": "Frutas y verduras frescas",
    "461140": "Semillas, granos, especias y chiles secos",
    "461150": "Lácteos y embutidos (cremería)",
    "461160": "Dulces y materias primas para repostería",
    "311830": "Tortillería y molino de nixtamal",
    "311812": "Panadería tradicional",
    "463211": "Ropa",
    "463310": "Calzado",
    "464111": "Farmacia",
    "465311": "Papelería",
    "466410": "Celulares y accesorios",
    "467111": "Ferretería y tlapalería",
    "722514": "Taquería",
    "722519": "Fonda y cocina económica",
    "811211": "Reparación de celulares y electrónicos",
    "811430": "Reparación de calzado",
    "812110": "Estética y peluquería",
    "999999": "Otro",
}


class Producto(BaseModel):
    nombre: str
    precio: float | None = None
    unidad: str | None = None


class Ficha(BaseModel):
    nombre: str = Field(description="Nombre del puesto o negocio, p. ej. 'Puesto de Doña Lupe'")
    giro: str = ""
    clase_scian: str = Field(description="Una clave de la lista de giros dada")
    productos: list[Producto] = []
    dias: list[int] = Field(default=[], description="0 = lunes … 6 = domingo")
    abre: str | None = Field(None, description="HH:MM")
    cierra: str | None = Field(None, description="HH:MM")
    formas_pago: list[FormaPago] = ["efectivo"]
    acepta_mercomuna: bool | None = None
    telefono: str | None = Field(None, description="Solo si la persona lo dijo para su ficha")


class AltaIn(BaseModel):
    ficha: Ficha
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    origen: Literal["telegram", "campo", "demo"] = "telegram"
    verificado_por: str | None = None
    confirmado: bool = Field(False, description="El comerciante tocó 'Así queda'")
    consentimiento_publicar: bool = True
    demo_data: bool = False


class Alta(AltaIn):
    id: str
    slug: str
    ts: float
    h3: str
    tianguis_id: str | None = None
    tianguis_nombre: str | None = None


class SinConfirmar(ValueError):
    """Nada se publica sin 'Así queda'."""


# ---------- utilidades ----------

def _jsonl(ruta: Path) -> list[dict]:
    if not ruta.is_file():
        return []
    filas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        try:
            filas.append(json.loads(linea))
        except ValueError:
            continue
    return [f for f in filas if isinstance(f, dict)]


def _append(ruta: Path, fila: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def slugify(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-") or "negocio"


def _distancia_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(a))


def tianguis_cercano(lat: float, lng: float) -> dict | None:
    ruta = PROCESSED_DIR / "tianguis_abierto.json"
    try:
        puntos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    mejor, mejor_d = None, RADIO_TIANGUIS_M
    for p in puntos if isinstance(puntos, list) else []:
        try:
            d = _distancia_m(lat, lng, p["lat"], p["lng"])
        except (KeyError, TypeError):
            continue
        if d <= mejor_d:
            mejor, mejor_d = p, d
    return mejor


# ---------- altas ----------

def crear_alta(entrada: AltaIn) -> Alta:
    if not entrada.confirmado:
        raise SinConfirmar("Falta la confirmación 'Así queda' del comerciante")
    ficha = entrada.ficha
    if not ficha.giro:
        ficha.giro = GIROS.get(ficha.clase_scian, "Otro")
    ts = time.time()
    existentes = {a.get("slug") for a in _jsonl(LIVE_DIR / "altas.jsonl")}
    slug = slugify(ficha.nombre)
    if slug in existentes:
        slug = f"{slug}-{int(ts) % 100000}"
    cercano = tianguis_cercano(entrada.lat, entrada.lng)
    alta = Alta(
        **entrada.model_dump(),
        id=f"alta-{slug}",
        slug=slug,
        ts=ts,
        h3=h3.latlng_to_cell(entrada.lat, entrada.lng, 9),
        tianguis_id=cercano.get("id") if cercano else None,
        tianguis_nombre=cercano.get("nombre") if cercano else None,
    )
    _append(LIVE_DIR / "altas.jsonl", alta.model_dump())
    _append(LIVE_DIR / "eventos.jsonl", {
        "ts": ts, "tipo": "alta", "negocio_id": alta.id, "h3": alta.h3, "demo_data": alta.demo_data,
    })
    return alta


def altas_desde(desde: float = 0) -> list[dict]:
    return [a for a in _jsonl(LIVE_DIR / "altas.jsonl") if (a.get("ts") or 0) > desde]


# ---------- IA: transcripción y ficha (con respaldo grabado) ----------

def _sin_remedio(e: Exception) -> bool:
    """Sin crédito o llave inválida: reintentar no sirve; pasar directo al respaldo grabado."""
    from openai import AuthenticationError, PermissionDeniedError, RateLimitError

    if isinstance(e, (AuthenticationError, PermissionDeniedError)):
        return True
    return isinstance(e, RateLimitError) and "insufficient_quota" in str(e)


def usar_respaldo() -> bool:
    return settings.demo_mode or not settings.openai_api_key


def ficha_grabada() -> Ficha:
    return Ficha.model_validate_json((FIXTURES / "dona_lupe_ficha.json").read_text(encoding="utf-8"))


def transcribir(audio: bytes, nombre: str = "voz.ogg") -> tuple[str, bool]:
    """Devuelve (texto, grabado)."""
    if not usar_respaldo():
        try:
            from openai import OpenAI

            cliente = OpenAI(api_key=settings.openai_api_key, timeout=30, max_retries=0)
            for modelo in (settings.openai_transcribe_model, "whisper-1"):
                try:
                    r = cliente.audio.transcriptions.create(model=modelo, file=(nombre, audio), language="es")
                    return r.text, False
                except Exception as e:  # noqa: BLE001 — probar el respaldo
                    log.warning("transcripción con %s falló: %s", modelo, e)
                    if _sin_remedio(e):
                        break
        except Exception as e:  # noqa: BLE001
            log.warning("transcripción no disponible: %s", e)
    return (FIXTURES / "dona_lupe_transcripcion.txt").read_text(encoding="utf-8").strip(), True


PROMPT_FICHA = (
    "Eres un asistente que llena la ficha de un puesto o negocio de barrio de la Ciudad de México a partir de lo "
    "que dice su dueña o dueño. Usa solo lo que se dice; no inventes precios ni horarios. Días: 0 = lunes … "
    "6 = domingo; si dice 'fines de semana' son [5, 6]. Horas en formato HH:MM de 24 h ('de 7 a 3' = 07:00 a "
    "15:00). formas_pago solo de: efectivo, transferencia, dimo, codi, tarjeta (efectivo siempre). clase_scian "
    "debe ser una de estas claves: {giros}. Si no dice nombre del negocio, usa 'Puesto de <nombre de la persona>'. "
    "telefono solo si lo dicta para su ficha."
)


def extraer_ficha(texto: str) -> tuple[Ficha, bool]:
    """Texto libre → ficha validada. Devuelve (ficha, grabada). Reintenta una vez y luego usa el respaldo."""
    if not usar_respaldo():
        from openai import OpenAI

        cliente = OpenAI(api_key=settings.openai_api_key, timeout=30, max_retries=0)
        giros = ", ".join(f"{k} ({v})" for k, v in GIROS.items())
        for modelo in (settings.openai_model, settings.openai_model, settings.openai_fallback_model):
            try:
                r = cliente.responses.parse(
                    model=modelo,
                    input=[
                        {"role": "system", "content": PROMPT_FICHA.format(giros=giros)},
                        {"role": "user", "content": texto},
                    ],
                    text_format=Ficha,
                )
                ficha = r.output_parsed
                if ficha is None:
                    continue
                ficha = Ficha.model_validate(ficha.model_dump())
                if ficha.clase_scian not in GIROS:
                    ficha.clase_scian = "999999"
                ficha.giro = GIROS[ficha.clase_scian]
                ficha.dias = sorted({d for d in ficha.dias if 0 <= d <= 6})
                return ficha, False
            except (ValidationError, Exception) as e:  # noqa: BLE001 — un fallo del modelo nunca tumba la demo
                log.warning("ficha con %s falló: %s", modelo, e)
                if _sin_remedio(e):
                    break
    return ficha_grabada(), True


def ficha_texto(ficha: Ficha) -> str:
    """La ficha como la lee el comerciante en Telegram (lenguaje claro)."""
    nombres = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
    lineas = [f"🧺 {ficha.nombre}", f"Giro: {ficha.giro or GIROS.get(ficha.clase_scian, 'Otro')}"]
    if ficha.productos:
        lineas.append("Productos:")
        for p in ficha.productos:
            precio = f" — ${p.precio:g}" + (f" el {p.unidad}" if p.unidad else "") if p.precio is not None else ""
            lineas.append(f"  • {p.nombre}{precio}")
    if ficha.dias:
        lineas.append("Días: " + ", ".join(nombres[d] for d in ficha.dias))
    if ficha.abre and ficha.cierra:
        lineas.append(f"Horario: {ficha.abre} a {ficha.cierra}")
    lineas.append("Pagos: " + ", ".join(ficha.formas_pago))
    if ficha.acepta_mercomuna:
        lineas.append("Acepta Mercomuna ✅")
    if ficha.telefono:
        lineas.append(f"WhatsApp: {ficha.telefono}")
    return "\n".join(lineas)
