import json
import time

import h3
import pytest
from fastapi.testclient import TestClient

from app import config
from app.main import app
from app.services import ruta

DEMO = "2 kilos de jitomate, tortillas, chiles secos, tenis para niño, pilas"
SEDE = {"lat": 19.3486, "lng": -99.1530}
CADENAS = json.loads((config.PROCESSED_DIR / "negocios.json").read_text(encoding="utf-8"))
IDS_CADENA = {n["id"] for n in CADENAS if not n["es_barrial"]}


@pytest.fixture(autouse=True)
def vivo_temporal(tmp_path, monkeypatch):
    """Sin red ni llaves, y sin escribir en data/live del repo."""
    monkeypatch.setattr(config, "LIVE_DIR", tmp_path)
    monkeypatch.setattr(config.settings, "demo_mode", True)
    yield tmp_path


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_ruta_de_la_demo(client, vivo_temporal) -> None:
    inicio = time.perf_counter()
    r = client.post("/api/ruta", json={"origen": SEDE, "texto_lista": DEMO, "dia": 5, "hora": "10:00"})
    assert r.status_code == 200
    assert time.perf_counter() - inicio < 3
    datos = r.json()
    assert 3 <= len(datos["paradas"]) <= 6
    assert datos["resumen"]["cadenas"] == 0 and datos["sin_resultado"] == []
    cubiertos = sorted(a for p in datos["paradas"] for a in p["articulos"])
    assert len(cubiertos) == 5
    assert datos["geometria"]["type"] == "LineString"
    assert all(p["por_que"] for p in datos["paradas"])
    eventos = [json.loads(line) for line in (vivo_temporal / "eventos.jsonl").read_text().splitlines()]
    assert sum(e["tipo"] == "aparicion_ruta" for e in eventos) == len(datos["paradas"])


def test_articulo_inexistente_va_a_sin_resultado(client) -> None:
    datos = client.post("/api/ruta", json={"origen": SEDE, "texto_lista": "tortillas, xqzwv flurb"}).json()
    assert "xqzwv flurb" in datos["sin_resultado"]
    assert datos["paradas"]


@pytest.mark.parametrize("lista", [
    DEMO, "leche, huevo, pan dulce", "cuaderno, lapiz, colores", "bistec, cebolla, aguacate, limon",
    "paracetamol, algodon", "refresco, papitas, galletas", "pollo, arroz, frijol", "foco, cinta de aislar",
    "corte de cabello", "tacos al pastor", "queso oaxaca, crema", "chamarra, calcetines", "recarga, cargador",
    "tortillas, nopales, chile serrano", "pan de muerto, chocolate en polvo", "pilas, veladoras",
    "zapatos escolares, uniforme", "jamaica, azucar", "masa, chiles secos, queso", "jabon, cloro, suavizante",
])
def test_ninguna_ruta_pasa_por_una_cadena(client, lista) -> None:
    for dia in (0, 2, 5):
        datos = client.post("/api/ruta", json={"origen": SEDE, "texto_lista": lista, "dia": dia, "hora": "11:00"}).json()
        assert not {p["negocio"]["id"] for p in datos["paradas"]} & IDS_CADENA
        assert datos["resumen"]["cadenas"] == 0


def test_invariante_responde_500(client, monkeypatch) -> None:
    original = ruta._lugares

    def con_cadena(dia, hora):
        lugares = original(dia, hora)
        for lugar in lugares:
            lugar["es_barrial"] = False
        return lugares

    monkeypatch.setattr(ruta, "_lugares", con_cadena)
    assert client.post("/api/ruta", json={"texto_lista": "tortillas"}).status_code == 500


def test_alta_en_vivo_entra_a_la_ruta(client, vivo_temporal) -> None:
    alta = {"id": "alta-dona-lupe", "lat": SEDE["lat"] + 0.0008, "lng": SEDE["lng"] + 0.0005, "h3": None,
            "ficha": {"nombre": "Puesto de Doña Lupe", "clase_scian": "461130",
                      "productos": [{"nombre": "nopales"}, {"nombre": "jitomate"}], "dias": [], "abre": "07:00",
                      "cierra": "15:00", "formas_pago": ["efectivo", "transferencia"]}}
    (vivo_temporal / "altas.jsonl").write_text(json.dumps(alta) + "\n")
    datos = client.post("/api/ruta", json={"origen": SEDE, "texto_lista": "jitomate, nopales", "hora": "10:00"}).json()
    assert "alta-dona-lupe" in {p["negocio"]["id"] for p in datos["paradas"]}


def test_interpretar(client) -> None:
    datos = client.post("/api/articulos/interpretar", json={"texto": "2 kilos de jitomate y medio de limón"}).json()
    primero = datos["items"][0]
    assert primero["articulo"] == "jitomate" and primero["cantidad"] == 2 and primero["unidad"] == "kilos"
    assert "461130" in primero["clases"]


def test_compre_aqui(client, vivo_temporal) -> None:
    r = client.post("/api/eventos", json={"tipo": "compre_aqui", "negocio_id": "neg-0001"})
    assert r.status_code == 200
    assert "compre_aqui" in (vivo_temporal / "eventos.jsonl").read_text()


def test_alta_sin_h3_toma_el_hexagono_de_su_ubicacion(client, vivo_temporal) -> None:
    alta = {"id": "alta-sin-h3", "lat": SEDE["lat"], "lng": SEDE["lng"], "h3": None,
            "ficha": {"nombre": "Puesto sin h3", "clase_scian": "461130", "productos": [{"nombre": "nopales"}],
                      "dias": [], "abre": "00:00", "cierra": "23:59", "formas_pago": ["efectivo"]}}
    (vivo_temporal / "altas.jsonl").write_text(json.dumps(alta) + "\n")
    datos = client.post("/api/ruta", json={"origen": SEDE, "texto_lista": "nopales", "hora": "10:00"}).json()
    parada = next(p for p in datos["paradas"] if p["negocio"]["id"] == "alta-sin-h3")
    assert parada["negocio"]["h3"] == h3.latlng_to_cell(SEDE["lat"], SEDE["lng"], 9)
