import json
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import crecimiento as svc

client = TestClient(app)


@pytest.fixture
def live(tmp_path, monkeypatch):
    monkeypatch.setattr(svc, "LIVE_DIR", tmp_path)
    return tmp_path


def test_forma_y_etiquetas(live) -> None:
    r = client.get("/api/sedeco/crecimiento")
    assert r.status_code == 200
    d = r.json()
    assert set(d["alcaldias"]) >= {"09003", "09007"}
    for bloque in ("serie_trimestral", "altas_negocios_por_anio"):
        assert d[bloque]
        for serie in d[bloque]:
            assert serie["tipo_dato"] == "simulado"
            assert serie["fuente"]
            assert serie["puntos"]
    assert len(d["serie_trimestral"][0]["puntos"]) == 12
    assert d["altas_plataforma"]["tipo_dato"] == "real"
    assert d["rutas_por_hexagono"]["tipo_dato"] == "real"
    assert d["escala"]["alcaldias_totales"] == 16
    assert d["escala"]["parametro"] == "ALCALDIAS"


def test_series_deterministas(live) -> None:
    a = client.get("/api/sedeco/crecimiento").json()
    b = client.get("/api/sedeco/crecimiento").json()
    assert a["serie_trimestral"] == b["serie_trimestral"]
    assert a["altas_negocios_por_anio"] == b["altas_negocios_por_anio"]


def test_sin_archivos_no_falla(live) -> None:
    r = client.get("/api/sedeco/crecimiento")
    assert r.status_code == 200
    d = r.json()
    assert d["altas_plataforma"]["hoy"] == 0
    assert d["altas_plataforma"]["archivo_disponible"] is False
    assert d["rutas_por_hexagono"]["hexagonos"] == []


def test_cuenta_altas_hoy_y_rutas(live) -> None:
    ahora = datetime.now(svc.TZ)
    ayer = ahora - timedelta(days=2)
    filas = [
        {"id": "a1", "ts": ahora.isoformat()},
        {"id": "a2", "ts": ahora.isoformat()},
        {"id": "a3", "ts": ayer.isoformat()},
        {"id": "d1", "ts": ahora.isoformat(), "origen": "demo", "demo_data": True},
    ]
    (live / "altas.jsonl").write_text(
        "\n".join(json.dumps(f) for f in filas) + "\nno-es-json\n", encoding="utf-8"
    )
    eventos = [
        {"tipo": "aparicion_ruta", "h3": "8a4995b"},
        {"tipo": "aparicion_ruta", "h3": "8a4995b"},
        {"tipo": "busqueda", "h3": "8a4995b"},
        {"tipo": "aparicion_ruta", "h3": "8a49960"},
        {"tipo": "aparicion_ruta", "h3": "8a49960", "demo_data": True},
    ]
    (live / "eventos.jsonl").write_text(
        "\n".join(json.dumps(e) for e in eventos), encoding="utf-8"
    )
    d = client.get("/api/sedeco/crecimiento").json()
    assert d["altas_plataforma"]["hoy"] == 2
    assert d["altas_plataforma"]["total"] == 3
    assert d["altas_plataforma"]["archivo_disponible"] is True
    rutas = d["rutas_por_hexagono"]
    assert rutas["total"] == 3
    assert rutas["hexagonos"][0] == {"h3": "8a4995b", "rutas": 2}
