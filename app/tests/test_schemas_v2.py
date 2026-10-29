"""CO-001: contrato v2 (IDEA-v2.md §7, §8). Cada fixture valida contra su modelo y los datos privados no salen.

`repartidores.json`, `ofertas.json` y `alcaldias.json` tienen una entrada por endpoint; las demás son la respuesta.
"""

import json

import h3
import pytest
from pydantic import TypeAdapter, ValidationError

from app import schemas as S
from app.config import FIXTURES_DIR, PROCESSED_DIR, settings

POR_ENDPOINT = {
    "repartidores.json": {
        "POST /api/repartidores (request)": S.RepartidorAltaRequest,
        "POST /api/repartidores": S.RepartidorAltaResponse,
        "POST /api/repartidores/invitacion (request)": S.InvitacionRequest,
        "POST /api/repartidores/invitacion": S.InvitacionResponse,
        "POST /api/repartidores/codigo (request)": S.CodigoRequest,
        "POST /api/repartidores/codigo": S.CodigoResponse,
        "POST /api/repartidores/sesion (request)": S.SesionRequest,
        "POST /api/repartidores/sesion": S.SesionResponse,
        "GET /api/repartidores/{id}": S.RepartidorPerfil,
    },
    "ofertas.json": {
        "GET /api/ofertas": S.OfertasResponse,
        "POST /api/ofertas/{id}/tomar": S.Oferta,
        "POST /api/ofertas/{id}/completar": S.Oferta,
    },
    "alcaldias.json": {
        "GET /api/alcaldias": list[S.Alcaldia],
        "GET /api/alcaldias/{cvegeo}/colonias": S.ColoniasResponse,
    },
}
RESPUESTA = {"incentivos.json": list[S.Incentivo], "puntos.json": S.PuntosResponse}
PRIVADOS = {"prioridad", "rango_edad", "estudiante", "chat_id_hash", "tipo_id", "edad", "chat_id"}


def leer(name, carpeta=FIXTURES_DIR):
    return json.loads((carpeta / name).read_text(encoding="utf-8"))


def claves(obj):
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in claves(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in claves(v)}
    return set()


CASOS = [(f, e) for f, eps in POR_ENDPOINT.items() for e in eps]


@pytest.mark.parametrize(("name", "endpoint"), CASOS)
def test_fixture_por_endpoint_valida(name, endpoint):
    datos = leer(name)
    assert endpoint in datos, f"{name} sin {endpoint}"
    TypeAdapter(POR_ENDPOINT[name][endpoint]).validate_python(datos[endpoint])


@pytest.mark.parametrize("name", sorted(RESPUESTA))
def test_fixture_respuesta_valida(name):
    TypeAdapter(RESPUESTA[name]).validate_python(leer(name))


def test_punto_barrial_acepta_negocio_local_y_nada_mas():
    base = leer("tianguis_abierto.json")[0]
    assert S.PuntoBarrial.model_validate({**base, "tipo": "negocio_local"}).tipo == "negocio_local"
    with pytest.raises(ValidationError):
        S.PuntoBarrial.model_validate({**base, "tipo": "tiendita"})
    tipos = {p.tipo for p in S.PuntosResponse.model_validate(leer("puntos.json")).puntos}
    assert tipos == {"tianguis", "mercado", "negocio_local"}


def repartidor_completo():
    publico = leer("repartidores.json")["GET /api/repartidores/{id}"]["repartidor"]
    return S.Repartidor.model_validate({**publico, "chat_id_hash": "a1b2", "rango_edad": "18-30", "estudiante": True,
                                        "tipo_id": "credencial_escolar", "prioridad": 2, "foto_id": "x.jpg"})


def test_repartidor_publico_no_expone_prioridad_ni_identificacion():
    r = repartidor_completo()
    publico = S.RepartidorPublico.model_validate(r.model_dump()).model_dump()
    assert not PRIVADOS & set(publico), PRIVADOS & set(publico)
    assert not {k for k in publico if "foto" in k}
    assert "foto_id" not in S.Repartidor.model_fields and "prioridad" not in S.RepartidorPublico.model_fields


def test_fixtures_publicas_sin_datos_privados():
    perfil = leer("repartidores.json")["GET /api/repartidores/{id}"]
    assert not PRIVADOS & claves(perfil)
    assert not {k for k in claves(perfil) if "foto" in k}


def test_repartidor_reglas_de_alta():
    alta = leer("repartidores.json")["POST /api/repartidores (request)"]
    for malo in ({"edad": 17}, {"acepta_privacidad": False}, {"colonias": ["a", "b", "c", "d"]}, {"transporte": "avion"}):
        with pytest.raises(ValidationError):
            S.RepartidorAltaRequest.model_validate({**alta, **malo})
    with pytest.raises(ValidationError):
        S.Repartidor.model_validate({**repartidor_completo().model_dump(), "prioridad": 3})
    with pytest.raises(ValidationError):
        S.SesionRequest.model_validate({"id": "R-00042", "codigo": "12a456"})


def test_incentivos_bici_destacada_y_simulados():
    for incentivos in (leer("incentivos.json"), leer("incentivos.json", PROCESSED_DIR)):
        lista = TypeAdapter(list[S.Incentivo]).validate_python(incentivos)
        assert lista[0].id == "bici" and lista[0].destacado
        assert [i.id for i in lista if i.destacado] == ["bici"]
        assert all(i.tipo_dato == "simulado" and i.patrocinador is None for i in lista)


def test_alcaldias_16_con_prioridad_primero():
    alcaldias = TypeAdapter(list[S.Alcaldia]).validate_python(leer("alcaldias.json")["GET /api/alcaldias"])
    claves_alc = [a.alcaldia_cvegeo for a in alcaldias]
    assert sorted(claves_alc) == [f"090{n:02d}" for n in range(2, 18)]
    assert claves_alc[:2] == settings.alcaldias_prioridad_list == ["09003", "09007"]
    assert [a.alcaldia_cvegeo for a in alcaldias if a.prioridad] == ["09003", "09007"]


def test_ofertas_demo_con_h3_real_y_pago_etiquetado():
    ofertas = S.OfertasResponse.model_validate(leer("ofertas.json")["GET /api/ofertas"]).ofertas
    assert ofertas and all(o.estado == "abierta" and o.demo_data for o in ofertas)
    for o in ofertas:
        assert o.tipo_dato_pago in ("real", "estimado", "simulado")
        for p in o.paradas:
            assert p.h3 == h3.latlng_to_cell(p.lat, p.lng, 9)


def test_config_v2():
    assert settings.prioridad_peso_edad + settings.prioridad_peso_estudiante == 2
    assert (settings.prioridad_edad_min, settings.prioridad_edad_max, settings.repartidor_edad_minima) == (18, 30, 18)
    assert settings.negocio_local_estratos.split(",") == ["0 a 5 personas", "6 a 10 personas"]
    assert hasattr(settings, "denue_token")
