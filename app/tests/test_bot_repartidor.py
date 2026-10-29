import json

import pytest

from app import config
from app.services import altas
from app.services import repartidor_dialogo as rd
from app.services.repartidor_dialogo import Entrada, avanzar, iniciar


@pytest.fixture()
def live(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(config, "PROCESSED_DIR", tmp_path / "processed")  # sin colonias.json: lista local
    monkeypatch.setattr(altas, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(rd.settings, "demo_mode", True)
    monkeypatch.delenv("REPARTIDORES_API_URL", raising=False)
    return tmp_path / "live"


def voz(texto):
    """Nota de voz simulada: el transcriptor inyectado devuelve este texto."""
    return Entrada(audio=b"ogg"), (lambda audio: (texto, True))


def paso(ses, ent, trans=None):
    return avanzar(ses, ent, trans, base_url="https://colonia.test")


def alta_hasta_resumen(live):
    ses, r = iniciar(777)
    assert "privacidad" in r.texto.lower() and r.botones[0][0][1] == "acepto"
    paso(ses, Entrada(boton="acepto"))
    ent, tr = voz("Hola, me llamo Ana López")  # nombre por voz
    paso(ses, ent, tr)
    assert ses.nombre == "Ana López"
    paso(ses, Entrada(texto="tengo 24 años"))
    paso(ses, Entrada(boton="est:si"))
    paso(ses, Entrada(boton="id:ine"))
    r = paso(ses, Entrada(foto=b"\xff\xd8fake"))
    assert ses.id_foto and (live / "ids").exists()
    assert "Coyoac" in r.botones[0][0][0] and "Iztapalapa" in r.botones[0][1][0]  # prioritarias primero
    assert sum(len(f) for f in r.botones) == 16
    paso(ses, Entrada(boton="alc:09003"))
    r = paso(ses, Entrada(texto="Santa Catarina y Del Carmen"))
    assert ses.colonias_nombres == ["Santa Catarina", "Del Carmen"]
    paso(ses, Entrada(boton="col_ok"))
    assert ses.paso == "transporte"
    return ses


def test_flujo_completo_texto_y_voz(live):
    ses = alta_hasta_resumen(live)
    r = paso(ses, Entrada(boton="tr:bici"))
    assert "Excelente" in r.texto and ses.paso == "dias"
    ent, tr = voz("puedo los fines de semana por la tarde")  # un solo audio llena días y franja
    r = paso(ses, ent, tr)
    assert ses.paso == "resumen" and "Así queda" in r.texto or r.botones[0][0][1] == "ok"
    assert "Fin de semana" in r.texto and "prioridad" not in r.texto.lower()
    r = paso(ses, Entrada(boton="ok"))
    assert r.terminado
    assert "https://colonia.test/#/repartidor" in r.texto
    rid = ses.repartidor_id
    assert rid.startswith("R-") and len(rid) == 7 and rid in r.texto
    fila = json.loads((live / "repartidores.jsonl").read_text().splitlines()[0])
    assert fila["demo_data"] is True and fila["id_verificada"] and fila["tipo_id"] == "ine"
    assert fila["prioridad"] == 2 and fila["rango_edad"] == "18-30" and fila["estado"] == "activo"
    assert fila["disponibilidad"] == {"dias": [5, 6], "desde": "12:00", "hasta": "18:00"}
    assert "edad" not in fila and "chat_id" not in fila and fila["chat_id_hash"] != "777"
    assert list((live / "ids").glob("*")) == []  # la foto se borró tras verificar
    assert "prioridad" not in r.texto.lower()


def test_moto_sugiere_bici_sin_bloquear(live):
    ses = alta_hasta_resumen(live)
    r = paso(ses, Entrada(texto="voy en moto"))
    assert ses.transporte == "moto" and ses.paso == "dias"
    assert "bici" in r.texto.lower() and "premios" in r.texto
    assert not any(ch.isdigit() for ch in r.texto.split("\n\n")[0])  # el mensaje no trae cifras


def test_sin_aceptar_no_sigue_y_menor_se_rechaza(live):
    ses, _ = iniciar(1)
    r = paso(ses, Entrada(texto="mi nombre es Pepe"))
    assert ses.paso == "privacidad" and r.botones
    r = paso(ses, Entrada(boton="no_acepto"))
    assert r.terminado and not (live / "repartidores.jsonl").exists()

    ses, _ = iniciar(2)
    paso(ses, Entrada(boton="acepto"))
    paso(ses, Entrada(texto="Luis"))
    r = paso(ses, Entrada(texto="17"))
    assert r.terminado and "mayores de 18" in r.texto and ses.rango_edad is None
    assert not (live / "repartidores.jsonl").exists()


def test_entradas_raras_repreguntan(live):
    ses, _ = iniciar(3)
    paso(ses, Entrada(boton="acepto"))
    assert paso(ses, Entrada(texto="???")).texto.startswith("No alcancé")
    paso(ses, Entrada(texto="Mario"))
    assert paso(ses, Entrada(texto="uhm")).texto.startswith("¿Cuántos años")
    paso(ses, Entrada(texto="1990"))  # año de nacimiento
    assert ses.rango_edad == "31+"
    paso(ses, Entrada(texto="no"))
    assert ses.estudiante is False
    r = paso(ses, Entrada(texto="hola"))  # id_tipo
    assert ses.paso == "id_tipo"
    paso(ses, Entrada(texto="mi pasaporte"))
    r = paso(ses, Entrada(texto="aquí va"))
    assert r.pide_foto and ses.paso == "id_foto"


def test_corregir_vuelve_al_resumen_y_cambia_campo(live):
    ses = alta_hasta_resumen(live)
    paso(ses, Entrada(boton="tr:bici"))
    paso(ses, Entrada(boton="dias:todos"))
    r = paso(ses, Entrada(boton="fr:noche"))
    assert ses.paso == "resumen" and "Todos los días" in r.texto
    r = paso(ses, Entrada(boton="corregir"))
    assert len(r.botones) == 5
    paso(ses, Entrada(boton="fix:transporte"))
    r = paso(ses, Entrada(boton="tr:a_pie"))
    assert ses.paso == "resumen" and "A pie" in r.texto
    paso(ses, Entrada(boton="fix:alcaldia"))
    paso(ses, Entrada(boton="alc:09007"))
    assert ses.colonias == []  # cambiar de alcaldía limpia las colonias
    paso(ses, Entrada(texto="Escuadrón 201"))
    r = paso(ses, Entrada(boton="col_ok"))
    assert ses.paso == "resumen" and "Iztapalapa: Escuadrón 201" in r.texto


def test_maximo_tres_colonias(live):
    ses = alta_hasta_resumen(live)
    paso(ses, Entrada(boton="fix:alcaldia")) if False else None
    ses.paso, ses.colonias, ses.colonias_nombres = "colonias", [], []
    for c in ("Del Carmen", "Los Reyes", "Ajusco", "Santo Domingo"):
        paso(ses, Entrada(texto=c))
    assert len(ses.colonias) == 3 and ses.paso == "transporte"


def test_colonias_json_tiene_prioridad_sobre_la_lista_local(live, tmp_path):
    (tmp_path / "processed").mkdir()
    (tmp_path / "processed" / "colonias.json").write_text(json.dumps([
        {"alcaldia_cvegeo": "09099", "alcaldia_nombre": "Prueba", "prioridad": False, "colonias": [{"id": "x1", "nombre": "Uno"}]},
        {"alcaldia_cvegeo": "09003", "alcaldia_nombre": "Coyoacán", "prioridad": True, "colonias": [{"id": "c1", "nombre": "Centro"}]},
    ]))
    assert [a["nombre"] for a in rd.alcaldias()] == ["Coyoacán", "Prueba"]
    assert len(rd.alcaldias()) == 2
    assert rd.alcaldias()[0]["colonias"][0]["id"] == "c1"


def test_lista_local_tiene_16_alcaldias_y_las_dos_primeras(live):
    a = rd.alcaldias()
    assert len(a) == 16 and [x["nombre"] for x in a[:2]] == ["Coyoacán", "Iztapalapa"]


def test_prioridad_solo_backend():
    assert rd.prioridad("18-30", True) == 2
    assert rd.prioridad("31+", True) == 1 and rd.prioridad("18-30", False) == 1
    assert rd.prioridad("31+", False) == 0


def test_adaptador_intercambiable(live):
    class Falso:
        def registrar(self, datos):
            return {"id": "R-00042"}

    ses = alta_hasta_resumen(live)
    paso(ses, Entrada(boton="tr:bici"))
    paso(ses, Entrada(boton="dias:todos"))
    paso(ses, Entrada(boton="fr:manana"))
    r = avanzar(ses, Entrada(boton="ok"), base_url="https://x", adaptador=Falso())
    assert "R-00042" in r.texto and not (live / "repartidores.jsonl").exists()


def test_bot_importa_y_menu_ofrece_repartidor():
    from app.bot import __main__ as bot

    textos = [b.text for fila in bot.MENU.keyboard for b in fila]
    assert "Quiero ser repartidor" in textos


# ---------- CO-023: el bot da de alta en la plataforma desplegada ----------

def _repartidor_in():
    return rd.RepartidorIn(chat_id=777, nombre_mostrar="Ana", rango_edad="18-30", estudiante=True,
                           alcaldia_cvegeo="09003", colonias=["Santa Catarina"], transporte="bici",
                           dias=[5, 6], desde="12:00", hasta="18:00", tipo_id="ine", demo_data=True)


def test_payload_valida_contra_la_api_de_repartidores():
    from app.services import repartidores

    entrada = repartidores.RepartidorIn.model_validate(rd.payload_api(_repartidor_in()))
    assert repartidores.calcular_prioridad(entrada.edad, entrada.estudiante) == 2
    assert entrada.disponibilidad.dias == ["sábado", "domingo"] and entrada.chat_id == "777"
    mayor = rd.payload_api(_repartidor_in().model_copy(update={"rango_edad": "31+", "estudiante": False}))
    assert repartidores.calcular_prioridad(mayor["edad"], False) == 0


def test_colonia_api_url_manda_repartidor_a_render(monkeypatch):
    monkeypatch.setattr(rd.settings, "demo_mode", False)
    monkeypatch.delenv("REPARTIDORES_API_URL", raising=False)
    monkeypatch.setenv("COLONIA_API_URL", "https://colonia.test/")
    ad = rd.adaptador_por_defecto()
    assert isinstance(ad, rd.AdaptadorApi) and ad.url == "https://colonia.test/api/repartidores"
    monkeypatch.delenv("COLONIA_API_URL")
    assert isinstance(rd.adaptador_por_defecto(), rd.AdaptadorLocal)


def test_alta_de_negocio_va_a_la_api_desplegada(live, monkeypatch):
    import httpx

    from app.bot import __main__ as bot

    enviado = {}

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {**enviado["json"], "id": "A-1", "slug": "dona-lupe", "ts": 1.0, "h3": "89498e2c2d3ffff", "pagina": "/n/dona-lupe"}

    def post(url, json, timeout):
        enviado.update(url=url, json=json)
        return Resp()

    monkeypatch.setenv("COLONIA_API_URL", "https://colonia.test")
    monkeypatch.setattr(httpx, "post", post)
    entrada = altas.AltaIn(ficha=altas.ficha_grabada(), lat=19.35, lng=-99.15, confirmado=True, demo_data=True)
    alta = bot.registrar_alta(entrada)
    assert enviado["url"] == "https://colonia.test/api/altas" and enviado["json"]["confirmado"] is True
    assert alta.slug == "dona-lupe" and not (live / "altas.jsonl").exists()  # nada se guardó en local
    monkeypatch.delenv("COLONIA_API_URL")
    assert bot.registrar_alta(entrada).id and (live / "altas.jsonl").exists()
