"""Lista del mandado → artículos con sus clases SCIAN (IDEA.md A.5, en ejecución).

Orden: reglas para separar la lista → diccionario exacto → sinónimo → difuso (rapidfuzz ≥ 88) → LLM con enum cerrado,
solo si hay llave y DEMO_MODE=0. El LLM nunca produce una cifra: solo elige una clase de la lista dada.
"""

import json
import re
from functools import lru_cache

from rapidfuzz import fuzz, process

from app import config
from pipeline.articulos.__main__ import normalizar

UMBRAL_DIFUSO = 88
_CANTIDAD = re.compile(
    r"^\s*(?P<cantidad>\d+(?:[.,]\d+)?|medio|media|un|una|dos|tres)\s*"
    r"(?P<unidad>kilos?|kg|gramos?|g|litros?|l|piezas?|pzas?|paquetes?|bolsas?|docenas?)?\s*(?:de\s+)?",
    re.IGNORECASE,
)
_PALABRAS = {"medio": 0.5, "media": 0.5, "un": 1, "una": 1, "dos": 2, "tres": 3}


@lru_cache(maxsize=1)
def diccionario() -> tuple[dict[str, list[str]], dict[str, str]]:
    """(nombre → clases, nombre → fuente) para artículos y sinónimos."""
    datos = json.loads((config.PROCESSED_DIR / "articulo_giro.json").read_text(encoding="utf-8"))
    clases: dict[str, list[str]] = {}
    fuente: dict[str, str] = {}
    for a in datos:
        for nombre, tipo in [(a["articulo"], "diccionario")] + [(s, "sinonimo") for s in a["sinonimos"]]:
            actuales = clases.setdefault(nombre, [])
            actuales.extend(c for c in a["clases_scian"] if c not in actuales)
            fuente.setdefault(nombre, tipo)
    return clases, fuente


def separar(texto: str) -> list[str]:
    partes = re.split(r"[,;\n]+|\s+y\s+|\s+e\s+", texto or "")
    return [p.strip() for p in partes if p.strip()]


def _cantidad(frase: str) -> tuple[float | None, str | None]:
    m = _CANTIDAD.match(frase)
    if not m or not m.group("cantidad"):
        return None, None
    valor = m.group("cantidad").lower()
    cantidad = _PALABRAS.get(valor) or float(valor.replace(",", "."))
    return cantidad, (m.group("unidad") or "").lower() or None


def _llm_clase(frase: str, opciones: list[str]) -> str | None:
    """Elige una clase de `opciones` o None. Solo con llave y fuera de DEMO_MODE; cualquier falla → None."""
    if config.settings.demo_mode or not config.settings.openai_api_key:
        return None
    try:
        from openai import OpenAI

        cliente = OpenAI(api_key=config.settings.openai_api_key, timeout=8)
        esquema = {
            "type": "object",
            "properties": {"clase": {"type": "string", "enum": [*opciones, "ninguna"]}},
            "required": ["clase"],
            "additionalProperties": False,
        }
        respuesta = cliente.chat.completions.create(
            model=config.settings.openai_model,
            messages=[
                {"role": "system", "content": "Clasifica un artículo de compra de México en una clase SCIAN de la lista. "
                 "Responde 'ninguna' si no corresponde a ninguna."},
                {"role": "user", "content": frase},
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "clase", "schema": esquema, "strict": True}},
        )
        clase = json.loads(respuesta.choices[0].message.content or "{}").get("clase")
        return clase if clase in opciones else None
    except Exception:  # noqa: BLE001 - el LLM es opcional: si falla, el artículo va a sin_resultado
        return None


def interpretar(texto: str, clases_zona: list[str] | None = None) -> dict:
    clases, fuente = diccionario()
    nombres = list(clases)
    items, sin_resultado = [], []
    for frase in separar(texto):
        cantidad, unidad = _cantidad(frase)
        clave = normalizar(frase)
        if not clave:
            continue
        encontrado, origen = None, None
        if clave in clases:
            encontrado, origen = clave, fuente[clave]
        else:
            mejor = process.extractOne(clave, nombres, scorer=fuzz.WRatio, score_cutoff=UMBRAL_DIFUSO)
            if mejor:
                encontrado, origen = mejor[0], "difuso"
        if encontrado:
            items.append({"texto": frase, "articulo": encontrado, "cantidad": cantidad, "unidad": unidad,
                          "clases": clases[encontrado], "fuente": origen})
            continue
        clase = _llm_clase(frase, clases_zona or sorted({c for cs in clases.values() for c in cs}))
        if clase:
            items.append({"texto": frase, "articulo": clave, "cantidad": cantidad, "unidad": unidad,
                          "clases": [clase], "fuente": "llm"})
        else:
            sin_resultado.append(frase)
    return {"items": items, "sin_resultado": sin_resultado}
