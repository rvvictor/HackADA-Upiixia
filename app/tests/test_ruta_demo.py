"""Ruta de la demo en la API (CO-040): con DEMO_MODE el repartidor R-00001 entra con su número y ve ofertas;
el mapa y la ruta etiquetan sus cifras; lo desconocido da 404 sin romper."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import ofertas, repartidores

client = TestClient(app)
TIPOS = {"real", "estimado", "simulado"}
RUTA_REQUEST = Path(__file__).resolve().parents[1] / "fixtures" / "ruta_request.json"


@pytest.fixture()
def demo(tmp_path, monkeypatch):
    """DEMO_MODE on, with live files in a temp dir so the test never touches data/live."""
    for mod in (repartidores, ofertas):
        monkeypatch.setattr(mod, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(repartidores, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(repartidores.settings, "demo_mode", True)
    repartidores.reiniciar_accesos()


def test_repartidor_demo_entra_con_su_numero(demo) -> None:
    rid = repartidores.DEMO_ID
    s = client.post("/api/repartidores/sesion", json={"id": rid})
    assert s.status_code == 200
    assert s.json()["repartidor_id"] == rid and s.json()["token"]

    r = client.get("/api/ofertas", params={"repartidor_id": rid})
    assert r.status_code == 200
    ids = {o["id"] for o in r.json()}
    # The fixed demo routes (O-FIJA*) are seeded the first time R-00001 enters.
    assert any(i.startswith("O-FIJA") for i in ids), ids


def test_mapa_responde_con_tipo_dato_en_cada_cifra(demo) -> None:
    hexes = client.get("/api/hex").json()["features"]
    assert hexes
    for f in hexes[:200]:
        p = f["properties"]
        numericos = {k for k, v in p.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
        assert numericos <= set(p["tipo_campos"]), numericos - set(p["tipo_campos"])
        assert set(p["tipo_campos"].values()) <= TIPOS

    ruta = client.post("/api/ruta", json=json.loads(RUTA_REQUEST.read_text(encoding="utf-8")))
    assert ruta.status_code == 200
    cuerpo = ruta.json()
    assert cuerpo["paradas"]
    for parada in cuerpo["paradas"]:
        assert parada["negocio"]["tipo_dato"] in TIPOS
    # Route totals are computed from those stops; in demo they travel flagged as demo data.
    assert cuerpo["demo_data"] is True


def test_ruta_desconocida_da_404(demo) -> None:
    assert client.get("/api/no-existe").status_code == 404
    r = client.get("/api/repartidores/R-99999")
    assert r.status_code == 404
    assert r.json()["detail"] == "repartidor no encontrado"
    # The app keeps answering after the 404s.
    assert client.get("/api/health").json() == {"status": "ok"}
