import json
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import altas

ROOT = Path(__file__).resolve().parent.parent.parent
client = TestClient(app)


@pytest.fixture()
def live(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    processed.mkdir()
    (processed / "tianguis_abierto.json").write_text(json.dumps([
        {"id": "t-cerca", "nombre": "Tianguis de San Lucas", "lat": 19.3468, "lng": -99.1617},
        {"id": "t-lejos", "nombre": "Tianguis lejano", "lat": 19.40, "lng": -99.10},
    ]))
    monkeypatch.setattr(altas, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(altas, "PROCESSED_DIR", processed)
    monkeypatch.setattr(altas.settings, "demo_mode", True)
    return tmp_path / "live"


def _entrada(confirmado: bool = True) -> dict:
    return {
        "ficha": altas.ficha_grabada().model_dump(),
        "lat": 19.3467, "lng": -99.1617, "origen": "demo", "confirmado": confirmado, "demo_data": True,
    }


def test_demo_mode_voz_y_ficha_grabadas(live) -> None:
    texto, grabada = altas.transcribir(b"\x00ogg")
    assert grabada and "Doña Lupe" in texto
    ficha, grabada = altas.extraer_ficha(texto)
    assert grabada and ficha.clase_scian in altas.GIROS
    assert {p.nombre for p in ficha.productos} == {"nopales", "jitomate"}
    assert "transferencia" in ficha.formas_pago


def test_ficha_preview_no_publica(live) -> None:
    body = client.post("/api/altas/ficha", json={"texto": "vendo nopales"}).json()
    assert body["ficha"]["nombre"] == "Puesto de Doña Lupe" and body["demo_data"] is True
    assert not (live / "altas.jsonl").exists()


def test_sin_asi_queda_no_hay_alta(live) -> None:
    r = client.post("/api/altas", json=_entrada(confirmado=False))
    assert r.status_code == 409
    assert not (live / "altas.jsonl").exists()


def test_alta_confirmada_escribe_jsonl_evento_y_live(live) -> None:
    r = client.post("/api/altas", json=_entrada())
    assert r.status_code == 201
    alta = r.json()
    assert alta["h3"].startswith("89") and alta["tianguis_id"] == "t-cerca"
    assert alta["pagina"] == f"/n/{alta['slug']}"
    filas = (live / "altas.jsonl").read_text().splitlines()
    assert json.loads(filas[0])["id"] == alta["id"]
    evento = json.loads((live / "eventos.jsonl").read_text().splitlines()[0])
    assert evento["tipo"] == "alta" and evento["negocio_id"] == alta["id"]

    nuevas = client.get("/api/altas/live", params={"desde": 0}).json()
    assert [a["id"] for a in nuevas["altas"]] == [alta["id"]]
    assert client.get("/api/altas/live", params={"desde": nuevas["ultimo_ts"]}).json()["altas"] == []


def test_slug_repetido_no_choca(live) -> None:
    a = client.post("/api/altas", json=_entrada()).json()
    b = client.post("/api/altas", json=_entrada()).json()
    assert a["slug"] != b["slug"]


def test_ubicacion_invalida_422(live) -> None:
    assert client.post("/api/altas", json={**_entrada(), "lat": 200}).status_code == 422


def test_simular_alta_script(tmp_path) -> None:
    # El script escribe en data/live/ del repo; se corre en una copia aislada vía variable de módulo.
    codigo = (
        "import sys, runpy; from pathlib import Path; from app.services import altas;"
        f"altas.LIVE_DIR = Path({str(tmp_path)!r});"
        "sys.argv = ['simular_alta.py', '--caso', 'dona-lupe'];"
        "runpy.run_path('scripts/simular_alta.py', run_name='__main__')"
    )
    out = subprocess.run([sys.executable, "-c", codigo], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.startswith("ALTA alta-puesto-de-dona-lupe")
    assert json.loads((tmp_path / "altas.jsonl").read_text())["demo_data"] is True


def test_dona_lupe_entra_a_la_ruta_de_la_vecina_despues_de_las_15(live, monkeypatch) -> None:
    """Plan B de la demo: simular_alta → la ruta desde la sede de la vista Vecina pasa por Doña Lupe,
    también en la tarde (la revisión y el pitch son después de las 15:00)."""
    from app import config
    from scripts.simular_alta import CASOS

    monkeypatch.setattr(config, "LIVE_DIR", live)
    alta = altas.crear_alta(altas.AltaIn(
        ficha=altas.ficha_grabada(), origen="demo", confirmado=True, demo_data=True, **CASOS["dona-lupe"]
    ))
    for hora in ("10:00", "16:30"):
        ruta = client.post("/api/ruta", json={
            "origen": {"lat": 19.3486, "lng": -99.153}, "dia": 6, "hora": hora,
            "texto_lista": "2 kilos de jitomate, tortillas, chiles secos, tenis para niño, pilas",
        }).json()
        assert alta.id in {p["negocio"]["id"] for p in ruta["paradas"]}, hora
