"""Genera data/processed/articulo_giro.json: diccionario artículo → clases SCIAN (IDEA.md A.5, versión corta a mano).

Uso: uv run python -m pipeline.articulos
"""

import json
import re
import unicodedata
from pathlib import Path

from pipeline.articulos.catalogo import CATALOGO, CATEGORIA_UI

ROOT = Path(__file__).resolve().parents[2]
SALIDA = ROOT / "data" / "processed" / "articulo_giro.json"
MAX_CLASES = 3


def normalizar(texto: str) -> str:
    """Minúsculas, sin acentos, sin cantidades; la misma regla que usa app/services/articulos.py al buscar."""
    texto = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    texto = re.sub(r"\d+([.,]\d+)?\s*(kilos?|kg|gramos?|g|litros?|l|piezas?|pzas?)?\b", " ", texto)
    texto = re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", texto)).strip()
    return re.sub(r"^((de|del|un|una|unos|unas|medio|media|kilo|kilos|litro|litros) )+", "", texto)


def construir() -> list[dict]:
    entradas: dict[str, dict] = {}
    for clase, lineas in CATALOGO.items():
        for linea in lineas:
            nombres = [normalizar(n) for n in linea.split("|")]
            principal, sinonimos = nombres[0], nombres[1:]
            e = entradas.setdefault(principal, {"articulo": principal, "sinonimos": [], "clases_scian": []})
            e["sinonimos"] = sorted(set(e["sinonimos"]) | {s for s in sinonimos if s != principal})
            if clase not in e["clases_scian"]:
                e["clases_scian"].append(clase)
    salida = []
    for e in entradas.values():
        # Ambiguos en más de 3 clases no ayudan a elegir negocio (A.5 paso 4).
        if len(e["clases_scian"]) > MAX_CLASES:
            continue
        e["categoria_ui"] = CATEGORIA_UI[e["clases_scian"][0]]
        e["fuente"] = "construido a mano por el equipo (sin LLM)"
        salida.append(e)
    return sorted(salida, key=lambda e: e["articulo"])


def main() -> None:
    articulos = construir()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(articulos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"articulo_giro.json: {len(articulos)} artículos, {sum(len(a['sinonimos']) for a in articulos)} sinónimos")


if __name__ == "__main__":
    main()
