import json
from pathlib import Path

from pipeline.negocios.__main__ import SALIDA, generar
from pipeline.negocios.filtros import CADENAS, clasificar, es_nombre_de_cadena, normalizar

ROOT = Path(__file__).resolve().parents[2]


def test_ningun_nombre_de_la_lista_negra_es_barrial() -> None:
    negocios = json.loads(SALIDA.read_text(encoding="utf-8"))
    for n in negocios:
        if n["es_barrial"]:
            for cadena in CADENAS:
                assert normalizar(cadena) not in normalizar(n["nombre"]), n["nombre"]
            assert n["motivo_exclusion"] is None


def test_cada_registro_tiene_h3_y_motivo_si_se_excluye() -> None:
    negocios = json.loads(SALIDA.read_text(encoding="utf-8"))
    assert len(negocios) >= 400
    for n in negocios:
        assert n["h3"] and n["tipo_dato"] == "simulado"
        assert n["es_barrial"] or n["motivo_exclusion"]


def test_los_cuatro_filtros_excluyen() -> None:
    motivos = {n["motivo_exclusion"].split(":")[0] for n in generar() if n["motivo_exclusion"]}
    assert motivos == {"giro", "tamaño", "nombre", "repetición"}


def test_el_archivo_es_lo_que_genera_el_script() -> None:
    assert json.loads(SALIDA.read_text(encoding="utf-8")) == generar()


def test_filtro_de_nombre() -> None:
    assert es_nombre_de_cadena("OXXO Copilco")
    assert es_nombre_de_cadena("Farmacias Similares Sucursal 12")
    assert not es_nombre_de_cadena("Abarrotes Doña Mary")
    assert not es_nombre_de_cadena("Tortillería La Esperanza")


def test_repeticion_marca_cadena_sin_lista() -> None:
    base = {"clase_scian": "722514", "estrato": "0 a 5 personas", "razon_social": ""}
    negocios = clasificar([{**base, "nombre": "Tacos El Famoso"} for _ in range(5)])
    assert not any(n["es_barrial"] for n in negocios)


def test_programas() -> None:
    programas = json.loads((ROOT / "data" / "processed" / "programas.json").read_text(encoding="utf-8"))
    estados = {p["id"]: p["estado"] for p in programas}
    assert estados["mercomuna"] == "existe" and estados["puntos-de-barrio"] == "propuesta"
    assert set(estados.values()) <= {"existe", "por_verificar", "propuesta"}
