"""PB-002: el contrato describe lo que la API sirve de verdad.

1. Cada fixture de app/fixtures/ valida contra su modelo.
2. Cada endpoint en vivo (DEMO_MODE, sin red) valida contra el mismo modelo: si un router cambia su respuesta,
   esta prueba avisa antes de que una vista se rompa.
"""

import importlib
import json
import pkgutil

import h3
import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from app import config
from app import schemas as S
from app import services as servicios
from app.config import FIXTURES_DIR
from app.main import app

SEDE = {"lat": 19.3486, "lng": -99.153}
LISTA = "2 kilos de jitomate, tortillas, chiles secos, tenis para niño, pilas"

FIXTURES = {
    "health.json": S.Health,
    "hex.json": S.HexagonoColeccion,
    "dinero_alcaldias.json": list[S.DineroAlcaldia],
    "tianguis_abierto.json": list[S.PuntoBarrial],
    "tianguis.json": S.TianguisResponse,
    "sedeco_resumen.json": S.SedecoResumen,
    "negocios.json": list[S.Negocio],
    "articulos_request.json": S.ArticulosRequest,
    "articulos_interpretar.json": S.ArticulosResponse,
    "ruta_request.json": S.RutaRequest,
    "ruta.json": S.RutaResponse,
    "evento_request.json": S.EventoRequest,
    "evento.json": S.EventoResponse,
    "ficha_dona_lupe.json": S.FichaAlta,
    "altas_live.json": S.AltasLive,
    "negocio_detalle.json": S.NegocioDetalle,
    "pagina.json": S.Pagina,
    "sedeco_crecimiento.json": S.SedecoCrecimiento,
}


def parse(name):
    return TypeAdapter(FIXTURES[name]).validate_python(json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8")))


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_fixture_validates(name):
    assert (FIXTURES_DIR / name).is_file(), f"missing fixture {name}"
    parse(name)


def test_hex_fixture_is_real_h3_geojson():
    hexes = parse("hex.json").features
    assert len(hexes) >= 30
    for f in hexes:
        p = f.properties
        assert h3.is_valid_cell(p.h3) and h3.get_resolution(p.h3) == 9
        anillo = f.geometry.coordinates[0]
        assert anillo[0] == anillo[-1], "ring must be closed"
        lng, lat = anillo[0]
        assert -100 < lng < -98 and 19 < lat < 20, "GeoJSON order is [lng, lat]"
        if p.oculto:
            assert p.actividad_tpv_est is None
    assert any(f.properties.oculto for f in hexes)


def test_day_convention_is_monday_zero():
    puntos = parse("tianguis_abierto.json")
    domingo = sum(p.abierto_en(6, "10:00") for p in puntos)
    martes = sum(p.abierto_en(1, "10:00") for p in puntos)
    assert domingo > martes, "0 = lunes … 6 = domingo: Sunday must be the busy tianguis day"
    assert S.dia_desde_js(0) == 6 and S.dia_desde_js(1) == 0  # JS getDay(): 0 = domingo


def test_ruta_fixture_has_no_chains():
    ruta = parse("ruta.json")
    cadenas = {n.id for n in parse("negocios.json") if not n.es_barrial}
    assert cadenas and not {p.negocio.id for p in ruta.paradas} & cadenas
    assert ruta.resumen.cadenas == 0


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config.settings, "demo_mode", True)
    monkeypatch.setattr(config.settings, "openai_api_key", "")
    monkeypatch.setattr(config.settings, "mapbox_token", "")
    monkeypatch.setattr(config, "LIVE_DIR", tmp_path)
    for modulo in pkgutil.iter_modules(servicios.__path__):
        m = importlib.import_module(f"app.services.{modulo.name}")
        if hasattr(m, "LIVE_DIR"):
            monkeypatch.setattr(m, "LIVE_DIR", tmp_path)
    return TestClient(app)


def test_live_endpoints_match_the_contract(client):
    from app.services import altas

    alta = altas.crear_alta(altas.AltaIn(ficha=altas.ficha_grabada(), origen="demo", confirmado=True, demo_data=True,
                                         lat=19.3492, lng=-99.1525))
    casos = [
        (S.Health, client.get("/api/health")),
        (S.HexagonoColeccion, client.get("/api/hex")),
        (list[S.DineroAlcaldia], client.get("/api/dinero/alcaldias")),
        (S.TianguisResponse, client.get("/api/tianguis", params={"dia": 6, "hora": "10:00"})),
        (S.SedecoResumen, client.get("/api/sedeco/resumen", params={"dia": 6, "hora": "10:00"})),
        (S.ArticulosResponse, client.post("/api/articulos/interpretar", json={"texto": LISTA})),
        (S.RutaResponse, client.post("/api/ruta", json={"origen": SEDE, "texto_lista": LISTA, "dia": 6, "hora": "10:00"})),
        (S.EventoResponse, client.post("/api/eventos", json={"tipo": "compre_aqui", "negocio_id": alta.id})),
        (S.AltasLive, client.get("/api/altas/live", params={"desde": 0})),
        (S.NegocioDetalle, client.get(f"/api/negocio/{alta.id}")),
        (S.Pagina, client.post(f"/api/negocio/{alta.id}/pagina")),
    ]
    crecimiento = client.get("/api/sedeco/crecimiento")
    if crecimiento.status_code != 404:  # PB-014 may not be merged yet
        casos.append((S.SedecoCrecimiento, crecimiento))
    for modelo, respuesta in casos:
        assert respuesta.status_code in (200, 201), respuesta.request.url
        TypeAdapter(modelo).validate_python(respuesta.json())
