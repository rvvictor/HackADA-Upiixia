import json
from datetime import datetime

import h3
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import mapa

SEDE = (19.3467, -99.1617)


def _hex_geojson() -> dict:
    celdas = sorted(h3.grid_disk(h3.latlng_to_cell(*SEDE, 9), 3))
    features = []
    for i, c in enumerate(celdas):
        oculto = i % 7 == 0
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [[[lng, lat] for lat, lng in h3.cell_to_boundary(c)]]},
            "properties": {
                "h3": c, "alcaldia_cvegeo": "09003", "poblacion": 100 + 10 * i,
                "negocios_barriales": 2 if oculto else 5, "negocios_total": 2 if oculto else 6,
                "actividad_tpv_est": 1000.0 + i, "monto_est": None, "impulso": 0.5, "cluster_id": None,
                "oculto": oculto, "periodo_cnbv": "2023-T2",
                "tipo_campos": {"poblacion": "simulado", "actividad_tpv_est": "simulado"},
            },
        })
    return {"type": "FeatureCollection", "meta": {"tipo_dato": "simulado"}, "features": features}


def _punto(i: int, dias: list[int], abre: str = "07:00", cierra: str = "15:00") -> dict:
    lat, lng = SEDE
    return {
        "id": f"t-{i}", "tipo": "tianguis", "nombre": f"Tianguis {i}", "alcaldia_cvegeo": "09003",
        "lat": lat + 0.002 * i, "lng": lng, "h3": h3.latlng_to_cell(lat + 0.002 * i, lng, 9),
        "dias": dias, "abre": abre, "cierra": cierra, "tipo_dato": "simulado",
    }


@pytest.fixture()
def datos(tmp_path, monkeypatch):
    processed, live, fixtures = tmp_path / "processed", tmp_path / "live", tmp_path / "fixtures"
    for d in (processed, live, fixtures):
        d.mkdir()
    (processed / "hex.geojson").write_text(json.dumps(_hex_geojson()))
    (processed / "cnbv_tpv_municipios.json").write_text(json.dumps([
        {"cvegeo": "09003", "municipio": "Coyoacán", "tpv_por_adulto": 3.9, "tipo_dato": "simulado"},
        {"cvegeo": "09007", "municipio": "Iztapalapa", "tpv_por_adulto": 1.6, "tipo_dato": "simulado"},
    ]))
    # domingo (6) lleno; martes (1) solo un punto
    puntos = [_punto(i, [5, 6]) for i in range(5)] + [_punto(9, [1, 6])]
    (processed / "tianguis_abierto.json").write_text(json.dumps(puntos))
    monkeypatch.setattr(mapa, "PROCESSED_DIR", processed)
    monkeypatch.setattr(mapa, "LIVE_DIR", live)
    monkeypatch.setattr(mapa, "FIXTURES_DIR", fixtures)
    return tmp_path


client = TestClient(app)


def test_hex_oculto_sin_dinero(datos) -> None:
    body = client.get("/api/hex").json()
    assert body["type"] == "FeatureCollection" and len(body["features"]) == 37
    for f in body["features"]:
        p = f["properties"]
        if p["oculto"]:
            assert p["actividad_tpv_est"] is None and p["monto_est"] is None
        else:
            assert p["actividad_tpv_est"] is not None


def test_dinero_alcaldias(datos) -> None:
    body = client.get("/api/dinero/alcaldias").json()
    assert {a["cvegeo"] for a in body} == {"09003", "09007"}


def test_martes_menos_abiertos_que_domingo(datos) -> None:
    domingo = client.get("/api/tianguis", params={"dia": 6, "hora": "10:00"}).json()
    martes = client.get("/api/tianguis", params={"dia": 1, "hora": "10:00"}).json()
    assert domingo["abiertos"] == 6 and martes["abiertos"] == 1
    assert martes["cobertura"]["poblacion_cubierta_pct"] < domingo["cobertura"]["poblacion_cubierta_pct"]
    assert len(martes["cobertura"]["desiertos"]) >= len(domingo["cobertura"]["desiertos"])
    assert domingo["total"] == martes["total"] == 6  # los cerrados vienen con abierto=false


def test_fuera_de_horario_cerrado(datos) -> None:
    body = client.get("/api/tianguis", params={"dia": 6, "hora": "15:00"}).json()
    assert body["abiertos"] == 0 and body["cobertura"]["poblacion_cubierta_pct"] == 0.0


def test_dia_invalido_422(datos) -> None:
    assert client.get("/api/tianguis", params={"dia": 7}).status_code == 422


def test_sin_archivos_nunca_500(tmp_path, monkeypatch) -> None:
    for attr in ("PROCESSED_DIR", "LIVE_DIR", "FIXTURES_DIR"):
        monkeypatch.setattr(mapa, attr, tmp_path / "no-existe")
    assert client.get("/api/hex").json()["features"] == []
    assert client.get("/api/dinero/alcaldias").json() == []
    assert client.get("/api/tianguis").json()["abiertos"] == 0
    assert client.get("/api/sedeco/resumen").status_code == 200


def test_respaldo_a_fixture(datos) -> None:
    (datos / "processed" / "cnbv_tpv_municipios.json").unlink()
    (datos / "fixtures" / "dinero_alcaldias.json").write_text(json.dumps({"alcaldias": [{"cvegeo": "09003"}]}))
    assert client.get("/api/dinero/alcaldias").json() == [{"cvegeo": "09003"}]


def test_resumen_altas_hoy_y_rutas(datos) -> None:
    hoy = datetime.now(mapa.ZONA).isoformat()
    live = datos / "live"
    (live / "altas.jsonl").write_text(
        json.dumps({"id": "a1", "ts": hoy}) + "\n" + json.dumps({"id": "a0", "ts": "2020-01-01T10:00:00"}) + "\n"
    )
    (live / "eventos.jsonl").write_text(
        "\n".join(json.dumps({"tipo": "aparicion_ruta", "h3": "89x"}) for _ in range(3)) + "\nbasura\n"
    )
    body = client.get("/api/sedeco/resumen", params={"dia": 6, "hora": "10:00"}).json()
    assert body["altas_hoy"] == 1
    assert body["rutas_por_hexagono"] == {"89x": 3}
    assert body["abiertos"] == 6 and body["poblacion_cubierta_pct"] > 0
    assert body["tipo_campos"]["poblacion_cubierta_pct"] == "estimado"
