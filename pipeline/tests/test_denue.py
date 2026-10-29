import json
from pathlib import Path

from pipeline.denue.__main__ import centros, es_giro_objetivo, filtrar

AQUI = Path(__file__).parent
CRUDOS = json.loads((AQUI / "muestras" / "denue.json").read_text(encoding="utf-8"))
SALIDA = AQUI.parents[1] / "data" / "processed" / "negocios_denue.json"


def test_filtra_sin_red_con_muestra_grabada() -> None:
    negocios = filtrar(CRUDOS)
    assert 0 < len(negocios) < len(CRUDOS)
    for n in negocios:
        assert n["tipo"] == "negocio_local" and n["tipo_dato"] == "real"
        assert n["fuente"] == "DENUE INEGI" and n["fecha_consulta"] == "2026-10-29"
        assert n["id_denue"] and n["nombre"] and n["giro"]
        assert isinstance(n["lat"], float) and isinstance(n["lng"], float)
        assert not {"Telefono", "Correo_e", "telefono", "correo"} & set(n)


def test_excluye_cadenas_autoservicio_y_estratos_grandes() -> None:
    ids_ok = {n["id_denue"] for n in filtrar(CRUDOS)}
    for r in CRUDOS:
        if r["Id"] in ids_ok:
            assert r["Estrato"] in {"0 a 5 personas", "6 a 10 personas"}
            assert "minisupers" not in r["Clase_actividad"].lower()
    assert any(r["Estrato"] not in {"0 a 5 personas", "6 a 10 personas"} for r in CRUDOS)
    assert any("minisuper" in r["Clase_actividad"].lower() for r in CRUDOS)


def test_giros_objetivo() -> None:
    assert es_giro_objetivo("Comercio al por menor de frutas y verduras frescas")
    assert es_giro_objetivo("Salones y clínicas de belleza y peluquerías")
    assert not es_giro_objetivo("Comercio al por mayor de mobiliario")
    assert not es_giro_objetivo("Comercio al por menor en minisupers")
    assert not es_giro_objetivo("Banca múltiple")


def test_centros_cubren_coyoacan_e_iztapalapa_completas() -> None:
    # muestra grabada del CSV real: 3 colonias de Coyoacán (3), 3 de Iztapalapa (7) y 20 de Gustavo A. Madero (5)
    alcs = [a for a, _, _ in centros(AQUI / "muestras" / "denue_colonias.csv")]
    assert alcs.count("3") == 3 and alcs.count("7") == 3  # las dos alcaldías completas, sin recorte
    assert alcs.count("5") <= 8  # el resto, acotado


def test_salida_y_sin_token() -> None:
    texto = SALIDA.read_text(encoding="utf-8")
    negocios = json.loads(texto)
    assert len(negocios) > 0 and all(n["tipo_dato"] == "real" for n in negocios)
    assert len({n["id_denue"] for n in negocios}) == len(negocios)
    assert "inegi.org.mx" not in texto
