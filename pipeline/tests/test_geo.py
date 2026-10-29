"""Pruebas de PB-004: datos simulados de hexágonos, dinero CNBV y tianguis."""

from __future__ import annotations

import json
from bisect import bisect_right
from pathlib import Path

import h3
import pytest

from pipeline.geo import ALCALDIAS, build
from pipeline.geo.generar import (
    CENTRO_DEMO,
    PERIODO_CNBV,
    UMBRAL_CLUSTER,
    UMBRAL_OCULTO,
)

RAIZ = Path(__file__).resolve().parents[2]
CAMPOS_HEX = {
    "h3", "alcaldia_cvegeo", "poblacion", "negocios_barriales", "negocios_total",
    "actividad_tpv_est", "monto_est", "impulso", "cluster_id", "oculto", "tipo_campos",
    "periodo_cnbv",
}
ETIQUETAS = {"real", "estimado", "simulado"}


@pytest.fixture(scope="module")
def salida(tmp_path_factory) -> dict[str, Path]:
    # Sin CSV de campo: todo simulado.
    return build(tmp_path_factory.mktemp("geo_a"), campo_csv=None)


@pytest.fixture(scope="module")
def hexes(salida) -> list[dict]:
    return json.loads(salida["hex"].read_text(encoding="utf-8"))["features"]


@pytest.fixture(scope="module")
def tianguis(salida) -> list[dict]:
    return json.loads(salida["tianguis"].read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cnbv(salida) -> list[dict]:
    return json.loads(salida["cnbv"].read_text(encoding="utf-8"))


def _props(hexes: list[dict]) -> list[dict]:
    return [f["properties"] for f in hexes]


def test_determinista(tmp_path, salida):
    otra = build(tmp_path, campo_csv=None)
    for clave in salida:
        assert salida[clave].read_bytes() == otra[clave].read_bytes(), clave


def test_rejilla_res9_y_geometria(hexes):
    assert hexes, "no hay hexágonos"
    alcaldias = {p["alcaldia_cvegeo"] for p in _props(hexes)}
    assert alcaldias == set(ALCALDIAS)
    for f in hexes:
        p = f["properties"]
        assert h3.get_resolution(p["h3"]) == 9
        assert f["geometry"]["type"] == "Polygon"
        assert set(p) == CAMPOS_HEX
        assert set(p["tipo_campos"]) >= {"poblacion", "negocios_total", "actividad_tpv_est", "impulso"}
        assert set(p["tipo_campos"].values()) <= ETIQUETAS
        assert p["periodo_cnbv"] == PERIODO_CNBV


def test_oculto_y_negocios(hexes):
    for p in _props(hexes):
        assert p["oculto"] == (p["negocios_total"] < UMBRAL_OCULTO)
        assert 0 <= p["negocios_barriales"] <= p["negocios_total"]


def test_impulso_formula_a3(hexes):
    props = _props(hexes)
    n = len(props)
    pobs = sorted(p["poblacion"] for p in props)
    acts = sorted(p["actividad_tpv_est"] for p in props)
    for p in props:
        if p["negocios_barriales"] >= 1:
            esperado = (bisect_right(pobs, p["poblacion"]) / n) * (
                1 - bisect_right(acts, p["actividad_tpv_est"]) / n
            )
            assert p["impulso"] == pytest.approx(esperado, abs=1e-4)
        else:
            assert p["impulso"] == 0


def test_actividad_suma_por_alcaldia_igual_al_total(hexes, cnbv):
    for fila in cnbv:
        suma = sum(p["actividad_tpv_est"] for p in _props(hexes)
                   if p["alcaldia_cvegeo"] == fila["cvegeo"])
        assert suma == pytest.approx(fila["transacciones_tpv"], rel=0.005)


def test_iztapalapa_mas_densa_y_menos_actividad_por_adulto(hexes, cnbv):
    def densidad(cvegeo: str) -> float:
        ps = [p for p in _props(hexes) if p["alcaldia_cvegeo"] == cvegeo]
        area = sum(h3.cell_area(p["h3"], "km^2") for p in ps)
        return sum(p["poblacion"] for p in ps) / area

    coy, izt = "09003", "09007"
    assert densidad(izt) > densidad(coy)
    por_adulto = {f["cvegeo"]: f["tpv_por_adulto"] for f in cnbv}
    assert por_adulto[izt] < por_adulto[coy]


def test_clusters_por_vecinos_h3(hexes):
    props = {p["h3"]: p for p in _props(hexes)}
    for h, p in props.items():
        if p["negocios_barriales"] >= UMBRAL_CLUSTER:
            assert isinstance(p["cluster_id"], int)
        else:
            assert p["cluster_id"] is None
    for h, p in props.items():
        if p["cluster_id"] is None:
            continue
        for vecino in h3.grid_disk(h, 1):
            q = props.get(vecino)
            if q and q["cluster_id"] is not None:
                assert q["cluster_id"] == p["cluster_id"]


def test_cnbv_etiquetado_simulado(cnbv):
    assert {f["cvegeo"] for f in cnbv} == set(ALCALDIAS)
    for f in cnbv:
        assert f["tipo_dato"] == "simulado"
        assert f["tpv_por_adulto"] == pytest.approx(f["transacciones_tpv"] / f["adultos"], abs=1e-3)


def test_tianguis_60_con_dias_y_horarios(tianguis):
    assert len(tianguis) == 60
    for t in tianguis:
        assert t["tipo_dato"] == "simulado"
        assert t["tipo"] in {"tianguis", "mercado"}
        assert t["dias"] and set(t["dias"]) <= set(range(7))
        assert t["abre"] < t["cierra"]
        assert t["alcaldia_cvegeo"] in ALCALDIAS
        assert h3.get_resolution(t["h3"]) == 9


def test_domingo_abren_mas_tianguis_que_martes(tianguis):
    """Demo paso 2: el domingo abren muchos tianguis y el martes cierran casi todos."""
    tianguis_dia = [t for t in tianguis if t["tipo"] == "tianguis"]
    domingo = sum(6 in t["dias"] for t in tianguis_dia)
    martes = sum(1 in t["dias"] for t in tianguis_dia)
    assert domingo >= 2 * martes + 5, (domingo, martes)
    assert domingo >= 0.35 * len(tianguis_dia)
    assert all(6 in t["dias"] for t in tianguis if t["tipo"] == "mercado")


def test_oculto_entre_3_y_5_por_ciento(hexes):
    ocultos = sum(p["oculto"] for p in _props(hexes))
    assert 0.03 <= ocultos / len(hexes) <= 0.05, (ocultos, len(hexes))
    for p in _props(hexes):
        if p["oculto"]:
            assert p["negocios_total"] <= 2
            assert p["negocios_barriales"] <= p["negocios_total"]


def test_tianguis_reales_desde_csv(tmp_path):
    csv_path = tmp_path / "tianguis_verificados.csv"
    csv_path.write_text(
        "nombre,alcaldia_cvegeo,colonia,lat,lng,dias,abre,cierra,giros,formas_pago,"
        "acepta_mercomuna,fuente,fecha_verificacion,verificado_por\n"
        "Tianguis Prueba,09003,Del Carmen,19.3300,-99.1600,6,08:00,15:00,frutas|carne,efectivo|CoDi,si,"
        "Campo,2026-10-24,equipo\n",
        encoding="utf-8",
    )
    rutas = build(tmp_path / "salida", campo_csv=csv_path)
    tianguis = json.loads(rutas["tianguis"].read_text(encoding="utf-8"))
    reales = [t for t in tianguis if t["tipo_dato"] == "real"]
    assert len(reales) == 1
    assert reales[0]["nombre"] == "Tianguis Prueba"
    assert reales[0]["dias"] == [6] and reales[0]["acepta_mercomuna"] is True
    assert len(tianguis) == 60
    assert sum(t["tipo_dato"] == "simulado" for t in tianguis) == 59


def test_geo_md_declara_simulado_y_fuentes_reales():
    texto = (RAIZ / "data" / "fuentes" / "geo.md").read_text(encoding="utf-8")
    for palabra in ("simulado", "real", "CNBV", "Censo 2020", "SEDECO", "aproximad"):
        assert palabra in texto, palabra


def test_bolsa_de_impulso_junto_a_la_sede(hexes):
    """La ruta de la demo pasa por zonas que necesitan clientes (impulso >= p70) cerca de la sede."""
    props = {p["h3"]: p for p in _props(hexes)}
    valores = sorted(p["impulso"] for p in props.values() if p["impulso"] > 0)
    p70 = valores[int(len(valores) * 0.7)]
    cerca = [props[c] for c in h3.grid_disk(h3.latlng_to_cell(*CENTRO_DEMO, 9), 6) if c in props]
    altos = [p for p in cerca if p["impulso"] >= p70]
    assert len(altos) >= len(cerca) // 3
