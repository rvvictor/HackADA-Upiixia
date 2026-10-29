"""Los 6 pasos de la demo (IDEA.md §4) de punta a punta, con DEMO_MODE=1, sin red y sin llaves."""

import importlib
import pkgutil

import pytest
from fastapi.testclient import TestClient

from app import config
from app import services as servicios
from app.main import app
from app.services import altas, demo


@pytest.fixture(autouse=True)
def sin_red(tmp_path, monkeypatch):
    monkeypatch.setattr(config.settings, "demo_mode", True)
    monkeypatch.setattr(config.settings, "openai_api_key", "")
    monkeypatch.setattr(config.settings, "mapbox_token", "")
    # data/live temporal: algunos servicios importan LIVE_DIR por valor, así que se cambia en cada uno.
    monkeypatch.setattr(config, "LIVE_DIR", tmp_path)
    for modulo in pkgutil.iter_modules(servicios.__path__):
        m = importlib.import_module(f"app.services.{modulo.name}")
        if hasattr(m, "LIVE_DIR"):
            monkeypatch.setattr(m, "LIVE_DIR", tmp_path)
    yield tmp_path


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _alta_dona_lupe() -> dict:
    entrada = altas.AltaIn(ficha=altas.ficha_grabada(), origen="demo", confirmado=True, demo_data=True, **demo.DONA_LUPE)
    return altas.crear_alta(entrada).model_dump()


def test_paso_1_mapa_sedeco(client) -> None:
    hexes = client.get("/api/hex").json()["features"]
    assert len(hexes) > 1000
    ocultos = [f["properties"] for f in hexes if f["properties"]["oculto"]]
    assert ocultos and all(p["actividad_tpv_est"] is None for p in ocultos)
    alcaldias = {a["cvegeo"] for a in client.get("/api/dinero/alcaldias").json()}
    assert alcaldias == {"09003", "09007"}


def test_paso_2_domingo_a_martes(client) -> None:
    domingo = client.get("/api/tianguis", params={"dia": 6, "hora": "10:00"}).json()
    martes = client.get("/api/tianguis", params={"dia": 1, "hora": "10:00"}).json()
    assert domingo["abiertos"] > martes["abiertos"]
    assert domingo["cobertura"]["poblacion_cubierta_pct"] > martes["cobertura"]["poblacion_cubierta_pct"]


def test_paso_3_ruta_sin_cadenas(client) -> None:
    ruta = client.post("/api/ruta", json={"origen": demo.SEDE, "texto_lista": demo.LISTA_DEMO, "dia": 6,
                                          "hora": "10:00"}).json()
    assert 3 <= len(ruta["paradas"]) <= 6
    assert ruta["resumen"]["cadenas"] == 0 and ruta["sin_resultado"] == []


def test_pasos_4_a_6_alta_por_voz_entra_al_mapa_la_ruta_y_el_tablero(client) -> None:
    alta = _alta_dona_lupe()
    # 4. El alta aparece en vivo para la vista SEDECO.
    vivas = client.get("/api/altas/live", params={"desde": 0}).json()["altas"]
    assert alta["id"] in {a["id"] for a in vivas}
    # 3 + 4. La ruta de Karla pasa por el puesto de Doña Lupe un minuto después.
    ruta = client.post("/api/ruta", json={"origen": demo.SEDE, "texto_lista": demo.LISTA_DEMO, "dia": 6,
                                          "hora": "10:00"}).json()
    assert alta["id"] in {p["negocio"]["id"] for p in ruta["paradas"]}
    assert ruta["resumen"]["cadenas"] == 0
    # 5. Su vista Negocio y su página web.
    negocio = client.get(f"/api/negocio/{alta['id']}")
    assert negocio.status_code == 200
    pagina = client.get(f"/n/{alta['slug']}")
    assert pagina.status_code == 200 and "Doña Lupe" in pagina.text
    # 6. El tablero de SEDECO suma el alta de hoy y las rutas por hexágono.
    resumen = client.get("/api/sedeco/resumen", params={"dia": 6, "hora": "10:00"}).json()
    assert resumen["altas_hoy"] >= 1
    assert resumen["rutas_por_hexagono"]


def test_historia_simulada_etiquetada() -> None:
    eventos = demo.historia()
    assert len(eventos) > 300
    assert all(e["demo_data"] is True for e in eventos)
    assert demo.eventos_de(eventos[-1]["negocio_id"] or "") or eventos[-1]["tipo"] == "busqueda"
