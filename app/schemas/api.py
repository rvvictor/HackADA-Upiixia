"""Peticiones y respuestas de la API tal como las sirven los routers (IDEA.md Apéndice C).

Un fixture por respuesta en app/fixtures/, generado desde la API real en DEMO_MODE; test_schemas.py comprueba que
cada endpoint en vivo sigue validando contra estos modelos.
"""

from typing import Literal

from pydantic import Field

from app.schemas.entidades import (
    HORA,
    Alta,
    Modelo,
    Producto,
    Programa,
    PuntoBarrial,
    TipoDato,
    TipoEvento,
)


class Health(Modelo):
    status: str


# GET /api/tianguis?dia=0-6&hora=HH:MM
class PuntoConEstado(PuntoBarrial):
    abierto: bool


class Cobertura(Modelo):
    poblacion_total: int
    poblacion_cubierta: int
    poblacion_cubierta_pct: float
    desiertos: list[str]
    radio_m: int
    tipo_dato: TipoDato
    metodo: str


class TianguisResponse(Modelo):
    dia: int = Field(ge=0, le=6, description="0 = lunes … 6 = domingo")
    dia_nombre: str
    hora: str = Field(pattern=HORA)
    total: int
    abiertos: int = Field(description="Cuántos de `puntos` están abiertos")
    puntos: list[PuntoConEstado] = Field(description="Todos los puntos; la UI apaga los de abierto=false")
    cobertura: Cobertura
    origen: Literal["processed", "fixture", "vacio"]


# GET /api/sedeco/resumen
class SedecoResumen(Modelo):
    altas_hoy: int
    rutas_por_hexagono: dict[str, int]
    dia: int = Field(ge=0, le=6)
    hora: str = Field(pattern=HORA)
    abiertos: int
    poblacion_cubierta_pct: float
    desiertos: int
    tipo_campos: dict[str, TipoDato]


# POST /api/articulos/interpretar
class ArticulosRequest(Modelo):
    texto: str


class ItemInterpretado(Modelo):
    texto: str
    articulo: str
    cantidad: float | None = None
    unidad: str | None = None
    clases: list[str]
    fuente: Literal["diccionario", "sinonimo", "difuso", "llm"]


class ArticulosResponse(Modelo):
    items: list[ItemInterpretado]
    sin_resultado: list[str]


# POST /api/ruta
class RutaRequest(Modelo):
    origen: dict[str, float] | None = Field(default=None, description="{lat, lng}; por defecto la sede del evento")
    texto_lista: str
    dia: int | None = Field(default=None, ge=0, le=6, description="0 = lunes … 6 = domingo; null = hoy")
    hora: str | None = Field(default=None, pattern=HORA, description="null = ahora")
    radio_m: int = 1500
    alpha: float = 0.6
    regresar: bool = True


class LugarRuta(Modelo):
    """Negocio, tianguis, mercado o alta del bot: lo mínimo para dibujar y explicar una parada."""

    id: str
    nombre: str
    tipo: Literal["negocio", "tianguis", "mercado", "alta"]
    giro: str
    lat: float
    lng: float
    h3: str | None
    formas_pago: list[str] = Field(default_factory=list)
    acepta_mercomuna: bool | None = None
    tipo_dato: TipoDato
    horario_verificado: bool
    impulso: float


class Parada(Modelo):
    orden: int
    negocio: LugarRuta
    articulos: list[str]
    por_que: list[str] = Field(description="Plantillas con datos calculados, nunca LLM")


class LineaGeo(Modelo):
    type: Literal["LineString"]
    coordinates: list[list[float]] = Field(description="[[lng, lat], …]")


class ResumenRuta(Modelo):
    barrial_pct: float
    cadenas: int
    paradas_impulso: int = Field(description="Paradas en hexágonos de impulso ≥ p70")


class RutaResponse(Modelo):
    paradas: list[Parada]
    geometria: LineaGeo | None
    distancia_m: float
    minutos: float
    resumen: ResumenRuta
    sin_resultado: list[str]
    aviso: str | None = Field(default=None, description="p. ej. 'Ruta aproximada en línea recta'")
    demo_data: bool


# POST /api/eventos
class EventoRequest(Modelo):
    tipo: Literal["busqueda", "compre_aqui"]
    negocio_id: str | None = None
    h3: str | None = None


class EventoResponse(Modelo):
    ts: float
    tipo: TipoEvento
    negocio_id: str | None = None
    h3: str | None = None
    demo_data: bool


# GET /api/altas/live?desde=ts
class AltasLive(Modelo):
    altas: list[Alta]
    desde: float
    ultimo_ts: float = Field(description="La UI lo manda como `desde` en la siguiente pregunta")


# GET /api/negocio/{id}
class FichaNegocio(Modelo):
    nombre: str
    giro: str | None = None
    colonia: str | None = None
    telefono: str | None = None
    horario: str | None = None
    formas_pago: list[str] = Field(default_factory=list)
    productos: list[Producto] = Field(default_factory=list)
    acepta_mercomuna: bool | None = None
    ubicacion: str | None = Field(default=None, description="exacta · aproximada")
    aparecer_en_rutas: bool = True


class Avance(Modelo):
    """Mi avance (privado): nunca ventas ni ingresos."""

    tipo_dato: TipoDato
    dias: int
    conteos: dict[str, int] = Field(description="busquedas · rutas · compre_aqui · visitas_pagina")


class Escalon(Modelo):
    orden: int = Field(ge=1, le=4)
    nombre: str = Field(description="Visible · Cobro digital · Historial · Crédito")
    estado: str
    beneficio: str
    siguiente_accion: str | None = None


class NegocioDetalle(Modelo):
    id: str
    origen: str
    ficha: FichaNegocio
    descripcion: str | None = None
    avance: Avance
    escalera: list[Escalon] = Field(min_length=4, max_length=4)
    programas: list[Programa]
    pagina: dict[str, str] | None = Field(default=None, description="{url, cartel}")


# POST /api/negocio/{id}/pagina
class Pagina(Modelo):
    slug: str
    url: str = Field(description="/n/{slug}")
    url_completa: str | None = None
    cartel: str = Field(description="/n/{slug}/cartel")
    qr: str = Field(description="data:image/png;base64,…")


# GET /api/sedeco/crecimiento
class SerieIndicador(Modelo):
    alcaldia_cvegeo: str
    alcaldia: str
    indicador: str
    puntos: list[dict]
    tipo_dato: TipoDato
    fuente: str


class SedecoCrecimiento(Modelo):
    alcaldias: list[str]
    serie_trimestral: list[SerieIndicador]
    altas_negocios_por_anio: list[SerieIndicador]
    altas_plataforma: dict
    rutas_por_hexagono: dict
    escala: dict
    demo_data: bool
