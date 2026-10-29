import json
from pathlib import Path

from pipeline.articulos.__main__ import SALIDA, construir, normalizar
from pipeline.negocios.clases import CLASES

ROOT = Path(__file__).resolve().parents[2]

# La lista de la demo (IDEA.md §4 paso 3).
DEMO = ["2 kilos de jitomate", "tortillas", "chiles secos", "tenis para niño", "pilas"]


def _indice() -> dict[str, list[str]]:
    indice: dict[str, list[str]] = {}
    for a in json.loads(SALIDA.read_text(encoding="utf-8")):
        for nombre in [a["articulo"], *a["sinonimos"]]:
            indice.setdefault(nombre, []).extend(a["clases_scian"])
    return indice


def test_al_menos_300_articulos() -> None:
    assert len(json.loads(SALIDA.read_text(encoding="utf-8"))) >= 300


def test_cada_articulo_de_la_demo_resuelve() -> None:
    indice = _indice()
    for texto in DEMO:
        assert indice.get(normalizar(texto)), texto


def test_clases_validas_y_maximo_tres() -> None:
    for a in json.loads(SALIDA.read_text(encoding="utf-8")):
        assert 1 <= len(a["clases_scian"]) <= 3
        assert all(c in CLASES for c in a["clases_scian"])


def test_el_archivo_es_lo_que_genera_el_script() -> None:
    assert json.loads(SALIDA.read_text(encoding="utf-8")) == construir()


def test_normalizar_quita_cantidad_y_acentos() -> None:
    assert normalizar("2 kilos de Jitomate") == "jitomate"
    assert normalizar("medio kilo de Limón") == "limon"
