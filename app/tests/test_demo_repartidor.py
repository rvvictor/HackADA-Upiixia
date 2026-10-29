"""Simulación de la demo (CO-010): alta → código → sesión → ofertas sembradas → tomar → completar."""

import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import ofertas, repartidores

client = TestClient(app)
RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("simular_repartidor", RAIZ / "scripts/simular_repartidor.py")
sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sim)

PROHIBIDAS = ("prioridad", "foto_id", "edad", "estudiante", "chat_id")


@pytest.fixture()
def live(tmp_path, monkeypatch):
    for mod in (repartidores, ofertas):
        monkeypatch.setattr(mod, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(repartidores, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(repartidores.settings, "demo_mode", True)
    repartidores.reiniciar_accesos()


def _limpio(obj) -> None:
    texto = json.dumps(obj, ensure_ascii=False).lower()
    for p in PROHIBIDAS:
        assert p not in texto, p


def test_flujo_demo_completo(live) -> None:
    pool = sim.negocios("09003")
    colonias = sorted({n["colonia"] for n in pool})[:3]
    r = client.post("/api/repartidores", json={
        "nombre_mostrar": "Rafa", "edad": 19, "estudiante": True, "alcaldia_cvegeo": "09003",
        "colonias": colonias, "transporte": "bici", "demo_data": True})
    assert r.status_code == 201
    rep = r.json()
    _limpio(rep)
    rid = rep["id"]
    assert rid.startswith("R-")

    c = client.post("/api/repartidores/codigo", json={"id": rid}).json()
    assert c["demo_data"] is True
    s = client.post("/api/repartidores/sesion", json={"id": rid, "codigo": c["codigo"]})
    assert s.status_code == 200
    h = {"Authorization": f"Bearer {s.json()['token']}"}

    creadas = sim.sembrar_ofertas(3, colonias, pool)
    assert len(creadas) == 3 and all(o["demo_data"] for o in creadas)
    vistas = client.get("/api/ofertas", params={"repartidor_id": rid}).json()
    ids = {o["id"] for o in vistas}
    assert {o["id"] for o in creadas} <= ids
    assert all(o["demo_data"] for o in vistas if o["id"] in {c["id"] for c in creadas})
    _limpio(vistas)

    antes = client.get(f"/api/repartidores/{rid}").json()
    bici0 = next(i for i in antes["incentivos"] if i["id"] == "bici")["avance"]
    oid = creadas[0]["id"]
    t = client.post(f"/api/ofertas/{oid}/tomar", headers=h)
    assert t.status_code == 200 and t.json()["estado"] == "tomada"
    done = client.post(f"/api/ofertas/{oid}/completar", headers=h)
    assert done.status_code == 200 and done.json()["estado"] == "completada"
    _limpio([t.json(), done.json()])

    despues = client.get(f"/api/repartidores/{rid}").json()
    _limpio(despues)
    bici1 = next(i for i in despues["incentivos"] if i["id"] == "bici")["avance"]
    assert bici1 > bici0
