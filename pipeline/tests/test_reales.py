"""Pruebas de pipeline.reales con mini-muestras (sin depender de data/raw/)."""

import json
from pathlib import Path

from pipeline.reales import procesar as p

M = Path(__file__).parent / "muestras" / "reales"


def test_arreglar_acentos():
    assert p.arreglar_acentos("BRASILEÃ‘OS") == "BRASILEÑOS"
    assert p.arreglar_acentos("COYOACÁN") == "COYOACÁN"


def test_alcaldias_unificadas():
    assert p.cve_alcaldia("COYOACAN") == p.cve_alcaldia("COYOACÁN") == "09003"
    assert sorted(p.ALCALDIAS.values()) == [f"09{n:03d}" for n in range(2, 18)]
    assert len(p.NOMBRES) == 16


def test_tianguis():
    filas, extra = p.procesar_tianguis(M / "ubicacion_tianguis.csv")
    assert len(filas) == 3 and extra["sin_alcaldia"] == 0
    assert {f["alcaldia_cvegeo"] for f in filas} == {"09003", "09007"}
    assert filas[0]["colonia"] == "LA CAÑADA"
    assert filas[0]["abre"] == "08:00" and filas[0]["cierra"] == "17:00" and filas[0]["dias"] == [0]
    assert filas[1]["dias"] == [5, 6] and filas[1]["giros"] == ["ABASTO"] and filas[2]["giros"] == []
    for f in filas:
        assert f["tipo"] == "tianguis" and f["tipo_dato"] == "real"
        assert f["fecha_consulta"] == "2026-10-25" and f["fuente"] and len(f["h3"]) == 15


def test_mercados_descarta_sin_coordenadas():
    filas, extra = p.procesar_mercados(M / "diccionario_tianguis.csv")
    assert len(filas) == 1 and extra["descartados"] == 1
    assert filas[0]["tipo"] == "mercado" and filas[0]["alcaldia_cvegeo"] == "09002"
    assert filas[0]["locales"] == 135 and filas[0]["lng"] < 0


def test_colonias_prioridad_y_cruces():
    marg, _ = p.procesar_marginacion(M / "indice_marginacion" / "marginacion.json")
    cont, _ = p.procesar_contaminacion(M / "colonias_prioritarias.csv")
    col, extra = p.procesar_colonias(M / "diccionario_colonias.json", marg, cont)
    por_id = {c["id"]: c for c in col}
    assert [c["prioridad"] for c in col] == [True, True, False]
    assert por_id["003-001"]["marginacion_gm"] == "Bajo"
    assert por_id["003-001"]["nivel_contaminacion"] == "alto"
    assert por_id["010-001"]["marginacion_gm"] is None and por_id["010-001"]["nivel_contaminacion"] is None
    assert por_id["007-001"]["lat"] is not None and "geometry" not in por_id["007-001"]
    assert extra["con_marginacion"] == 1 and extra["con_contaminacion"] == 1
    assert p.cruzar_indices(col, marg) == 1 and marg[1]["colonia_id"] is None


def test_ejecutar_escribe_json(tmp_path):
    raw = M
    res = p.ejecutar(raw, tmp_path)
    assert res["tianguis"] == 3 and res["mercados"] == 1
    tian = json.loads((tmp_path / "tianguis_abierto.json").read_text(encoding="utf-8"))
    assert {t["tipo"] for t in tian} == {"tianguis", "mercado"}
    assert all(t["tipo_dato"] == "real" for t in tian)
    for nombre in ("mercados", "colonias", "marginacion_colonia", "contaminacion_colonia"):
        assert (tmp_path / f"{nombre}.json").exists()
