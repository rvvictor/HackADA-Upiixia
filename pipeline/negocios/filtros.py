"""Regla anti-cadenas (IDEA.md A.7): un establecimiento es barrial solo si pasa los 4 filtros.

Es código real; hoy corre sobre negocios simulados con forma de DENUE y mañana sobre la descarga del DENUE.
"""

import re
import unicodedata
from collections import Counter
from pathlib import Path

from rapidfuzz import fuzz

# Supermercados, minisúpers y tiendas de conveniencia, departamentales. Claves SCIAN 2018 por confirmar con el catálogo INEGI.
GIROS_EXCLUIDOS = {
    "462111": "supermercado",
    "462112": "minisúper o tienda de conveniencia",
    "462210": "tienda departamental",
}
ESTRATOS_BARRIALES = {"0 a 5 personas", "6 a 10 personas"}
UMBRAL_NOMBRE = 90
UMBRAL_REPETICION = 5

CADENAS = [
    line.strip()
    for line in (Path(__file__).with_name("cadenas.txt")).read_text(encoding="utf-8").splitlines()
    if line.strip()
]


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9& ]", " ", texto.upper())).strip()


_CADENAS_NORM = [normalizar(c) for c in CADENAS]


def es_nombre_de_cadena(nombre: str) -> bool:
    texto = normalizar(nombre)
    if not texto:
        return False
    for cadena in _CADENAS_NORM:
        # Las marcas cortas (NETO, KFC, OXXO) solo cuentan como palabra completa; con difuso, "KFC" saldría en cualquier lado.
        if len(cadena) <= 5:
            if re.search(rf"(?<![A-Z0-9]){re.escape(cadena)}(?![A-Z0-9])", texto):
                return True
        elif fuzz.partial_ratio(cadena, texto) >= UMBRAL_NOMBRE:
            return True
    return False


def clasificar(negocios: list[dict]) -> list[dict]:
    """Llena es_barrial y motivo_exclusion en cada negocio, aplicando los 4 filtros en orden."""
    repeticiones = Counter(normalizar(n["nombre"]) for n in negocios) + Counter(
        normalizar(n["razon_social"]) for n in negocios if n.get("razon_social")
    )
    for n in negocios:
        motivo = None
        if n["clase_scian"] in GIROS_EXCLUIDOS:
            motivo = f"giro: {GIROS_EXCLUIDOS[n['clase_scian']]} ({n['clase_scian']})"
        elif n["estrato"] not in ESTRATOS_BARRIALES:
            motivo = f"tamaño: {n['estrato']}"
        elif es_nombre_de_cadena(n["nombre"]) or es_nombre_de_cadena(n.get("razon_social") or ""):
            motivo = "nombre: coincide con la lista de cadenas"
        elif max(
            repeticiones[normalizar(n["nombre"])],
            repeticiones[normalizar(n["razon_social"])] if n.get("razon_social") else 0,
        ) >= UMBRAL_REPETICION:
            motivo = f"repetición: el nombre aparece {UMBRAL_REPETICION} o más veces"
        n["es_barrial"] = motivo is None
        n["motivo_exclusion"] = motivo
    return negocios
