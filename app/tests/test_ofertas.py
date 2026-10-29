import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import ofertas, repartidores

client = TestClient(app)
T0 = 1_000_000.0


@pytest.fixture()
def live(tmp_path, monkeypatch):
    for mod in (repartidores, ofertas):
        monkeypatch.setattr(mod, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(repartidores, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(repartidores.settings, "demo_mode", False)
    repartidores.reiniciar_accesos()
    return tmp_path / "live"


def _rep(edad: int, estudiante: bool, ts: float, colonias=("San Lucas",)) -> str:
    entrada = repartidores.RepartidorIn(nombre_mostrar="x", edad=edad, estudiante=estudiante, alcaldia_cvegeo="09003",
                                        colonias=list(colonias), transporte="bici")
    return repartidores.crear(entrada, ahora=ts)["id"]


def _token(rid: str) -> dict:
    cod = repartidores.pedir_codigo(rid)
    return {"Authorization": f"Bearer {repartidores.abrir_sesion(rid, cod)['token']}"}


def test_ordenar_candidatos() -> None:
    oferta = {"colonia": "A"}
    rs = [
        {"id": "viejo0", "prioridad": 0, "colonias": ["A"], "ts_alta": 1},
        {"id": "p2lejos", "prioridad": 2, "colonias": ["B", "A"], "ts_alta": 5},
        {"id": "p2nuevo", "prioridad": 2, "colonias": ["A"], "ts_alta": 9},
        {"id": "p2viejo", "prioridad": 2, "colonias": ["A"], "ts_alta": 3},
    ]
    assert [r["id"] for r in ofertas.ordenar_candidatos(rs, oferta)] == ["p2viejo", "p2nuevo", "p2lejos", "viejo0"]


def test_estudiante_joven_ve_primero_y_el_otro_tambien(live) -> None:
    otro = _rep(45, False, ts=T0 - 500)  # más antiguo, pero sin prioridad
    estudiante = _rep(21, True, ts=T0 - 100)
    _rep(21, True, ts=T0, colonias=("Otra",))  # otro barrio: nunca la ve
    o = ofertas.crear({"colonia": "San Lucas", "distancia_m": 500}, ahora=T0)
    assert [x["id"] for x in ofertas.ofertas_para(estudiante, ahora=T0)] == [o["id"]]
    assert ofertas.ofertas_para(otro, ahora=T0) == []
    assert [x["id"] for x in ofertas.ofertas_para(otro, ahora=T0 + ofertas.VENTANA_S)] == [o["id"]]


def test_endpoint_lista_sin_prioridad(live) -> None:
    rid = _rep(21, True, ts=T0)
    ofertas.crear({"colonia": "San Lucas", "distancia_m": 900})
    ofertas.crear({"colonia": "San Lucas", "distancia_m": 300})
    res = client.get("/api/ofertas", params={"repartidor_id": rid})
    assert res.status_code == 200 and "prioridad" not in res.text
    assert [o["distancia_m"] for o in res.json()] == [300, 900]
    assert client.get("/api/ofertas", params={"repartidor_id": "R-00000"}).status_code == 404


def test_tomar_y_completar(live) -> None:
    a = _rep(21, True, ts=T0)
    b = _rep(22, True, ts=T0 + 1)
    oid = ofertas.crear({"colonia": "San Lucas"}, ahora=T0)["id"]
    assert client.post(f"/api/ofertas/{oid}/tomar").status_code == 401
    ha, hb = _token(a), _token(b)
    res = client.post(f"/api/ofertas/{oid}/tomar", headers=ha)
    assert res.status_code == 200 and res.json()["estado"] == "tomada" and res.json()["repartidor_id"] == a
    assert client.post(f"/api/ofertas/{oid}/tomar", headers=hb).status_code == 409
    assert client.post(f"/api/ofertas/{oid}/completar", headers=hb).status_code == 409
    res = client.post(f"/api/ofertas/{oid}/completar", headers=ha)
    assert res.status_code == 200 and res.json()["estado"] == "completada"
    assert repartidores.obtener(a)["rutas_completadas"] == 1
    assert [o["estado"] for o in ofertas.ofertas_para(a)] == ["completada"]  # CO-020: Mis rutas
    assert client.post("/api/ofertas/O-NADA/tomar", headers=ha).status_code == 404


def test_demo_siembra_ofertas(live, monkeypatch) -> None:
    monkeypatch.setattr(ofertas.settings, "demo_mode", True)
    rid = _rep(21, True, ts=T0)
    vistas = ofertas.ofertas_para(rid)
    assert vistas and all(o["demo_data"] for o in vistas)


def test_mis_rutas_tomada_y_completada_solo_del_dueno(live) -> None:
    a = _rep(21, True, ts=T0)
    b = _rep(22, True, ts=T0 + 1)
    oid = ofertas.crear({"colonia": "San Lucas"}, ahora=T0)["id"]
    ha, hb = _token(a), _token(b)
    assert client.post(f"/api/ofertas/{oid}/tomar", headers=ha).status_code == 200
    lista = client.get(f"/api/ofertas?repartidor_id={a}", headers=ha).json()
    assert [(o["id"], o["estado"]) for o in lista] == [(oid, "tomada")]
    assert client.post(f"/api/ofertas/{oid}/completar", headers=ha).status_code == 200
    lista = client.get(f"/api/ofertas?repartidor_id={a}", headers=ha).json()
    assert [(o["id"], o["estado"]) for o in lista] == [(oid, "completada")]
    assert all(k not in lista[0] for k in ("prioridad", "edad", "foto_id"))
    assert client.get(f"/api/ofertas?repartidor_id={b}", headers=hb).json() == []
