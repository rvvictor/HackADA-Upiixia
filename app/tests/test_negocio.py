import json
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app import config
from app.main import app
from app.services.negocio import horario_desde_ficha


@pytest.fixture
def tmp_datos(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    live = tmp_path / "live"
    processed.mkdir()
    live.mkdir()
    negocios = [
        {
            "id": "neg-0001",
            "nombre": "Carnicería Doña Toña",
            "clase_nombre": "Carnicería",
            "colonia": "Santa Úrsula Coapa",
            "formas_pago": ["efectivo"],
            "acepta_mercomuna": False,
            "h3": "89499585e97ffff",
            "lat": 19.3, "lng": -99.1,
        }
    ]
    programas = [
        {"id": "dimo", "nombre": "DiMo", "que_es": "x", "como_entrar": "y", "url_oficial": None,
         "estado": "existe", "fecha_verificacion": "2026-10-25"},
        {"id": "crece", "nombre": "Crece", "que_es": "x", "como_entrar": "y", "url_oficial": None,
         "estado": "por_verificar", "fecha_verificacion": "2026-10-25"},
    ]
    (processed / "negocios.json").write_text(json.dumps(negocios), encoding="utf-8")
    (processed / "programas.json").write_text(json.dumps(programas), encoding="utf-8")
    monkeypatch.setattr(config, "PROCESSED_DIR", processed)
    monkeypatch.setattr(config, "LIVE_DIR", live)
    return live


@pytest.fixture
def client(tmp_datos):
    return TestClient(app)


def _alta(live, id_, ficha):
    linea = {"id": id_, "ts": datetime.now(UTC).isoformat(), "ficha": ficha,
             "lat": 19.31, "lng": -99.12, "h3": "89499585e9bffff", "origen": "telegram",
             "demo_data": False}
    with (live / "altas.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")


def _alta_bot(live, id_, slug, ficha):
    """Fila como la escribe PB-008 (app/services/altas.py: Alta.model_dump())."""
    linea = {"id": id_, "slug": slug, "ts": datetime.now(UTC).timestamp(), "ficha": ficha,
             "lat": 19.31, "lng": -99.12, "h3": "89499585e9bffff", "origen": "telegram",
             "confirmado": True, "demo_data": False}
    with (live / "altas.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")


def _evento(live, tipo, negocio_id, ts, demo=False):
    linea = {"ts": ts.isoformat(), "tipo": tipo, "negocio_id": negocio_id,
             "h3": "89499585e97ffff", "demo_data": demo}
    with (live / "eventos.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")


def test_ficha_del_directorio_con_escalera_y_programas(client):
    r = client.get("/api/negocio/neg-0001")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["ficha"]["nombre"] == "Carnicería Doña Toña"
    assert cuerpo["ficha"]["giro"] == "Carnicería"
    assert [e["nombre"] for e in cuerpo["escalera"]] == ["Visible", "Cobro digital", "Historial", "Crédito"]
    assert cuerpo["escalera"][0]["estado"] == "logrado"
    assert cuerpo["escalera"][1]["estado"] == "siguiente"
    assert all({"estado", "beneficio", "siguiente_accion"} <= set(e) for e in cuerpo["escalera"])
    ids = [p["id"] for p in cuerpo["programas"]]
    assert ids == ["dimo"]  # por_verificar no se muestra
    assert cuerpo["pagina"] is None


def test_sin_eventos_reales_el_avance_es_simulado_y_estable(client):
    cuerpo = client.get("/api/negocio/neg-0001").json()
    assert cuerpo["avance"]["tipo_dato"] == "simulado"
    assert set(cuerpo["avance"]["conteos"]) == {"busquedas", "rutas", "compre_aqui", "visitas_pagina"}
    assert client.get("/api/negocio/neg-0001").json()["avance"]["conteos"] == cuerpo["avance"]["conteos"]


def test_eventos_reales_de_7_dias_cuentan_y_los_demo_no(tmp_datos, client):
    ahora = datetime.now(UTC)
    _evento(tmp_datos, "aparicion_ruta", "neg-0001", ahora - timedelta(days=1))
    _evento(tmp_datos, "aparicion_ruta", "neg-0001", ahora - timedelta(days=2))
    _evento(tmp_datos, "compre_aqui", "neg-0001", ahora - timedelta(days=30))  # fuera de ventana
    _evento(tmp_datos, "busqueda", "neg-0001", ahora, demo=True)  # simulado, no cuenta
    cuerpo = client.get("/api/negocio/neg-0001").json()
    assert cuerpo["avance"]["tipo_dato"] == "real"
    assert cuerpo["avance"]["conteos"]["rutas"] == 2
    assert cuerpo["avance"]["conteos"]["compre_aqui"] == 0
    assert cuerpo["avance"]["conteos"]["busquedas"] == 0


def test_alta_del_bot_se_encuentra_por_su_id(tmp_datos, client):
    _alta(tmp_datos, "alta-lupe", {"nombre": "Nopales Doña Lupe", "giro": "Verdura",
                                    "telefono": "5512345678", "formas_pago": ["transferencia"],
                                    "ventas_mes": 99999})
    cuerpo = client.get("/api/negocio/alta-lupe").json()
    assert cuerpo["ficha"]["nombre"] == "Nopales Doña Lupe"
    assert cuerpo["escalera"][1]["estado"] == "logrado"
    assert "ventas_mes" not in cuerpo["ficha"]
    assert "ventas_mes" not in json.dumps(cuerpo)


def test_negocio_inexistente_da_404(client):
    assert client.get("/api/negocio/no-existe").status_code == 404
    assert client.get("/api/negocio/..%2Fsecreto").status_code == 404
    assert client.put("/api/negocio/no-existe/ficha", json={"nombre": "x"}).status_code == 404


def test_funciona_sin_archivos_live(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PROCESSED_DIR", tmp_path / "vacio")
    monkeypatch.setattr(config, "LIVE_DIR", tmp_path / "no-existe")
    cliente = TestClient(app)
    assert cliente.get("/api/negocio/neg-0001").status_code == 404
    assert cliente.get("/n/nada").status_code == 404


def test_put_ficha_persiste_y_rechaza_campos_ajenos(client, tmp_datos):
    r = client.put("/api/negocio/neg-0001/ficha", json={
        "telefono": "55 1234 5678", "horario": "7 a 3", "formas_pago": ["efectivo", "transferencia"],
        "productos": [{"nombre": "Nopal", "precio": 20}],
    })
    assert r.status_code == 200
    assert r.json()["ficha"]["horario"] == "7 a 3"
    assert (tmp_datos / "fichas" / "neg-0001.json").is_file()
    assert client.get("/api/negocio/neg-0001").json()["ficha"]["productos"][0]["nombre"] == "Nopal"
    assert client.put("/api/negocio/neg-0001/ficha", json={"ventas": 500}).status_code == 422


def test_pagina_se_genera_se_sirve_y_registra_vista(client, tmp_datos):
    client.put("/api/negocio/neg-0001/ficha", json={
        "telefono": "5512345678", "horario": "7 a 3", "formas_pago": ["efectivo", "transferencia"],
        "productos": [{"nombre": "Nopal", "precio": 20}, {"nombre": "Jitomate", "precio": 25}],
        "acepta_mercomuna": True,
    })
    r = client.post("/api/negocio/neg-0001/pagina")
    assert r.status_code == 200
    datos = r.json()
    slug = datos["slug"]
    assert datos["url"] == f"/n/{slug}"
    assert datos["qr"].startswith("data:image/png;base64,")
    assert (tmp_datos / "paginas" / f"{slug}.html").is_file()

    pagina = client.get(f"/n/{slug}")
    assert pagina.status_code == 200
    html = pagina.text
    assert "Carnicería Doña Toña" in html
    assert "Nopal" in html and "$20" in html
    assert "Acepta Mercomuna" in html
    assert "https://wa.me/525512345678" in html
    assert "data:image/png;base64," in html
    assert "ventas" not in html.lower() and "ingreso" not in html.lower()

    eventos = [json.loads(l) for l in (tmp_datos / "eventos.jsonl").read_text().splitlines()]
    assert eventos[-1]["tipo"] == "vista_pagina"
    assert eventos[-1]["negocio_id"] == "neg-0001"
    assert eventos[-1]["demo_data"] is False

    ficha = client.get("/api/negocio/neg-0001").json()
    assert ficha["pagina"]["url"] == f"/n/{slug}"
    assert client.post("/api/negocio/neg-0001/pagina").json()["slug"] == slug  # slug estable


def test_sin_telefono_no_hay_boton_de_whatsapp(client):
    slug = client.post("/api/negocio/neg-0001/pagina").json()["slug"]
    html = client.get(f"/n/{slug}").text
    assert "wa.me" not in html
    assert "Escanea el código" in html


def test_pagina_inexistente_o_slug_invalido_da_404(client):
    assert client.get("/n/no-hay-pagina").status_code == 404
    assert client.get("/n/..%2Fconfig").status_code == 404
    assert client.get("/n/no-hay-pagina/cartel").status_code == 404


def test_cartel_imprimible_con_qr_grande_y_medios_de_pago(client):
    slug = client.post("/api/negocio/neg-0001/pagina").json()["slug"]
    r = client.get(f"/n/{slug}/cartel")
    assert r.status_code == 200
    assert "Aceptamos transferencia / DiMo" in r.text
    assert "Carnicería Doña Toña" in r.text
    assert "data:image/png;base64," in r.text
    assert "@page" in r.text


def test_descripcion_es_plantilla_fija_y_sin_datos_de_venta(client):
    cuerpo = client.put("/api/negocio/neg-0001/ficha", json={
        "productos": [{"nombre": "Nopal"}, {"nombre": "Chile"}], "horario": "7 a 3",
    }).json()
    assert cuerpo["descripcion"] == (
        "Carnicería Doña Toña es un negocio de carnicería en Santa Úrsula Coapa. "
        "Vende Nopal, Chile. Horario: 7 a 3. Acepta efectivo."
    )


def test_alta_del_bot_se_sirve_por_su_slug_con_horario_de_la_ficha(tmp_datos, client):
    _alta_bot(tmp_datos, "alta-tortas-x", "tortas-x", {
        "nombre": "Tortas Doña Chela", "giro": "Taquería", "clase_scian": "722514",
        "productos": [{"nombre": "Torta de milanesa", "precio": 45, "unidad": "pieza"}],
        "dias": [0, 1, 2, 3, 4], "abre": "07:00", "cierra": "15:00",
        "formas_pago": ["efectivo", "transferencia"], "telefono": "5512345678",
        "acepta_mercomuna": False,
    })
    r = client.get("/n/tortas-x")
    assert r.status_code == 200
    assert "Tortas Doña Chela" in r.text
    assert "lunes a viernes de 07:00 a 15:00" in r.text
    assert "Torta de milanesa" in r.text
    ficha = client.get("/api/negocio/alta-tortas-x").json()
    assert ficha["pagina"]["url"] == "/n/tortas-x"
    assert ficha["ficha"]["horario"] == "lunes a viernes de 07:00 a 15:00"
    assert ficha["avance"]["tipo_dato"] == "real"
    assert ficha["avance"]["conteos"]["visitas_pagina"] == 1
    assert (tmp_datos / "paginas" / "tortas-x.html").is_file()


def test_slug_de_negocio_del_directorio_se_genera_en_el_primer_acceso(tmp_datos, client):
    r = client.get("/n/carniceria-dona-tona-neg-0001")
    assert r.status_code == 200
    assert "Carnicería Doña Toña" in r.text
    assert (tmp_datos / "paginas" / "carniceria-dona-tona-neg-0001.html").is_file()
    assert client.get("/n/carniceria-dona-tona-neg-0001/cartel").status_code == 200


def test_horario_desde_dias_abre_cierra():
    assert horario_desde_ficha([0, 1, 2, 3, 4], "07:00", "15:00") == "lunes a viernes de 07:00 a 15:00"
    assert horario_desde_ficha([5, 6], "08:00", "14:00") == "sábado a domingo de 08:00 a 14:00"
    assert horario_desde_ficha([0, 2, 3, 4, 6], "07:00", "15:00") == (
        "lunes, miércoles a viernes y domingo de 07:00 a 15:00"
    )
    assert horario_desde_ficha([], "07:00", "15:00") == "07:00 a 15:00"
    assert horario_desde_ficha([0], None, "15:00") is None
