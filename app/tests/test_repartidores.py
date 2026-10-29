import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import repartidores

client = TestClient(app)


@pytest.fixture()
def live(tmp_path, monkeypatch):
    monkeypatch.setattr(repartidores, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(repartidores, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(repartidores.settings, "demo_mode", True)
    repartidores.reiniciar_accesos()
    return tmp_path / "live"


def alta(**cambios) -> dict:
    return {"nombre_mostrar": "Ana", "edad": 21, "estudiante": True, "alcaldia_cvegeo": "09003",
            "colonias": ["San Lucas"], "transporte": "bici", "tipo_id": "credencial_escolar",
            "chat_id": "12345", "foto_id_b64": "Zm90bw==", "demo_data": True, **cambios}


def test_prioridad() -> None:
    assert repartidores.calcular_prioridad(21, True) == 2
    assert repartidores.calcular_prioridad(21, False) == 1
    assert repartidores.calcular_prioridad(45, True) == 1
    assert repartidores.calcular_prioridad(45, False) == 0


def test_alta_pendiente_sin_datos_privados(live) -> None:
    res = client.post("/api/repartidores", json=alta())
    assert res.status_code == 201
    r = res.json()
    assert r["id"].startswith("R-") and len(r["id"]) == 7
    assert r["estado"] == "pendiente_verificacion" and r["id_verificada"] is False
    texto = res.text
    for privado in ("prioridad", "foto", "Zm90bw==", "chat_id", "estudiante", "rango_edad", "12345"):
        assert privado not in texto
    guardado = repartidores.obtener(r["id"])
    assert guardado["prioridad"] == 2 and "Zm90bw==" not in (live / "repartidores.jsonl").read_text()


def test_codigo_y_sesion(live) -> None:
    rid = client.post("/api/repartidores", json=alta()).json()["id"]
    cod = client.post("/api/repartidores/codigo", json={"id": rid}).json()["codigo"]
    assert len(cod) == 6 and cod.isdigit()
    assert client.post("/api/repartidores/sesion", json={"id": rid, "codigo": "000000" if cod != "000000" else "111111"}).status_code == 401
    ses = client.post("/api/repartidores/sesion", json={"id": rid, "codigo": cod})
    assert ses.status_code == 200 and ses.json()["token"] and ses.json()["expira"]
    # un solo uso
    assert client.post("/api/repartidores/sesion", json={"id": rid, "codigo": cod}).status_code == 401


def test_codigo_vence(live) -> None:
    rid = repartidores.crear(repartidores.RepartidorIn(**alta()))["id"]
    cod = repartidores.pedir_codigo(rid, ahora=1000.0)
    with pytest.raises(repartidores.AccesoInvalido):
        repartidores.abrir_sesion(rid, cod, ahora=1000.0 + repartidores.CODIGO_TTL_S + 1)


def test_codigo_fuera_de_demo_no_se_devuelve(live, monkeypatch) -> None:
    monkeypatch.setattr(repartidores.settings, "demo_mode", False)
    rid = repartidores.crear(repartidores.RepartidorIn(**alta()))["id"]
    assert "codigo" not in client.post("/api/repartidores/codigo", json={"id": rid}).json()


def test_perfil_e_incentivos_bici_primero(live) -> None:
    rid = client.post("/api/repartidores", json=alta()).json()["id"]
    perfil = client.get(f"/api/repartidores/{rid}")
    assert perfil.status_code == 200 and "prioridad" not in perfil.text
    assert perfil.json()["incentivos"][0]["id"] == "bici"
    cat = client.get("/api/incentivos").json()
    assert cat[0]["id"] == "bici" and cat[0]["destacado"] is True
    assert all(i["tipo_dato"] == "simulado" for i in cat)
    assert client.get("/api/repartidores/R-00000").status_code == 404


def test_sesion_solo_con_numero_valido(live) -> None:
    rid = client.post("/api/repartidores", json=alta()).json()["id"]
    ses = client.post("/api/repartidores/sesion", json={"id": rid})
    assert ses.status_code == 200 and ses.json()["repartidor_id"] == rid and ses.json()["token"]
    assert client.post("/api/repartidores/sesion", json={"id": "R-99999"}).status_code == 401


def test_repartidor_demo_fijo_entra_siempre(live) -> None:
    rid, cod = repartidores.DEMO_ID, repartidores.DEMO_CODIGO
    assert client.get(f"/api/repartidores/{rid}").status_code == 200  # existe aunque no haya altas
    for _ in range(2):  # el código no se gasta
        ses = client.post("/api/repartidores/sesion", json={"id": rid, "codigo": cod})
        assert ses.status_code == 200 and ses.json()["repartidor_id"] == rid
    assert client.post("/api/repartidores/sesion", json={"id": rid, "codigo": "000001"}).status_code == 401
    assert "prioridad" not in client.get(f"/api/repartidores/{rid}").text


def test_repartidor_demo_entra_solo_con_numero(live) -> None:
    ses = client.post("/api/repartidores/sesion", json={"id": repartidores.DEMO_ID})
    assert ses.status_code == 200 and ses.json()["repartidor_id"] == repartidores.DEMO_ID
