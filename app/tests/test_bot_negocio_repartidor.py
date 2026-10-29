"""CO-011: tras "Así queda" del negocio, el bot pregunta por su repartidor (IDEA-v2.md §6)."""

import json

import pytest

from app import config
from app.bot import negocio_repartidor as nr
from app.services import altas
from app.services import repartidor_dialogo as rd
from app.services.repartidor_dialogo import Entrada

NEGOCIO = "alta-dona-lupe"


@pytest.fixture()
def live(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(config, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(altas, "LIVE_DIR", tmp_path / "live")
    monkeypatch.setattr(rd.settings, "demo_mode", True)
    monkeypatch.delenv("REPARTIDORES_API_URL", raising=False)
    return tmp_path / "live"


def paso(ses, ent):
    return nr.avanzar(ses, ent, bot_username="colonia_test_bot", base_url="https://colonia.test")


def test_pregunta_si_no(live):
    ses, r = nr.preguntar(NEGOCIO, 555)
    assert r.texto == "¿Tienes a alguien que haga entregas para tu negocio?"
    assert [c for _, c in r.botones[0]] == ["nr:si", "nr:no"]
    r = paso(ses, Entrada(boton="nr:si"))
    assert [f[0][1] for f in r.botones] == ["nr:yo", "nr:link"]


def test_no_ofrece_red_del_barrio(live):
    ses, _ = nr.preguntar(NEGOCIO)
    r = paso(ses, Entrada(texto="No, la verdad no"))
    assert r.terminado and "repartidores de tu colonia" in r.texto
    assert not (live / "repartidores.jsonl").exists()


def test_link_de_invitacion_ligado_al_negocio(live):
    ses, _ = nr.preguntar(NEGOCIO)
    paso(ses, Entrada(boton="nr:si"))
    r = paso(ses, Entrada(boton="nr:link"))
    assert r.terminado
    link = next(p for p in r.texto.split() if p.startswith("https://t.me/"))
    assert link.startswith("https://t.me/colonia_test_bot?start=inv_")
    payload = link.split("start=")[1]
    assert nr.resolver_invitacion(payload) == NEGOCIO
    assert nr.resolver_invitacion("inv_noexiste") is None
    fila = json.loads((live / "invitaciones.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert nr.resolver_invitacion(payload, ahora=fila["expira_ts"] + 1) is None  # vencida


def test_lo_doy_de_alta_yo_sin_foto_y_ligado(live):
    ses, _ = nr.preguntar(NEGOCIO, 555)
    paso(ses, Entrada(boton="nr:si"))
    r = paso(ses, Entrada(boton="nr:yo"))
    assert "llamemos" in r.texto and "privacidad" not in r.texto.lower()
    paso(ses, Entrada(texto="Beto Ramírez"))
    paso(ses, Entrada(texto="22"))
    r = paso(ses, Entrada(boton="est:no"))
    assert ses.rep.paso == "alcaldia" and not r.pide_foto and "identificaci" not in r.texto.lower()
    paso(ses, Entrada(boton="alc:09003"))
    paso(ses, Entrada(texto="Santa Catarina"))
    paso(ses, Entrada(boton="col_ok"))
    paso(ses, Entrada(boton="tr:bici"))
    paso(ses, Entrada(boton="dias:entre_semana"))
    r = paso(ses, Entrada(boton="fr:tarde"))
    if ses.rep.paso != "resumen":  # la franja puede venir en un paso aparte según el catálogo
        r = paso(ses, Entrada(texto="por la tarde"))
    assert ses.rep.paso == "resumen", r.texto
    r = paso(ses, Entrada(boton="ok"))
    assert r.terminado and "ligado a tu negocio" in r.texto
    fila = json.loads((live / "repartidores.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert fila["negocio_id"] == NEGOCIO
    assert fila["estado"] == "pendiente_verificacion" and not fila["id_verificada"] and fila["tipo_id"] is None
    assert not (live / "ids").exists() or list((live / "ids").glob("*")) == []


def test_rutas_de_su_negocio_primero():
    ofertas = [{"id": "O-1", "negocio_id": "otro"}, {"id": "O-2", "negocio_id": NEGOCIO},
               {"id": "O-3", "negocio_id": "otro2"}, {"id": "O-4", "negocio_id": NEGOCIO}]
    assert [o["id"] for o in nr.primero_su_negocio(ofertas, NEGOCIO)] == ["O-2", "O-4", "O-1", "O-3"]
    assert [o["id"] for o in nr.primero_su_negocio(ofertas, None)] == ["O-1", "O-2", "O-3", "O-4"]
