"""Contrato v2 (IDEA-v2.md §4, §5, §7, §8): repartidores, ofertas de ruta, incentivos, alcaldías y puntos del mapa.

Privacidad (IDEA-v2.md §4.5):
- `Repartidor` es el registro completo y no sale del backend. No hay campo de foto de identificación: la foto vive
  fuera de git y solo queda `id_verificada` + `tipo_id`.
- Lo que va al frontend o al bot es `RepartidorPublico`, que ignora campos extra: sin `prioridad`, `rango_edad`,
  `estudiante`, `chat_id_hash` ni `tipo_id`. Constrúyelo con `RepartidorPublico.model_validate(r.model_dump())`.

Fixtures (app/fixtures/): `repartidores.json`, `ofertas.json` y `alcaldias.json` son objetos con una entrada por
endpoint ("GET /api/…"); `incentivos.json` y `puntos.json` son la respuesta de su único endpoint.
"""

from typing import Literal

from pydantic import ConfigDict, Field

from app.schemas.entidades import HORA, Modelo, TipoDato, TipoPunto

RangoEdad = Literal["18-30", "31+"]
Transporte = Literal["bici", "bici_electrica", "a_pie", "scooter_electrico", "moto", "auto"]
EstadoRepartidor = Literal["pendiente_verificacion", "activo", "rechazado"]
EstadoOferta = Literal["abierta", "tomada", "completada", "cancelada"]
EstadoIncentivo = Literal["existe", "propuesta"]
TipoId = Literal["ine", "pasaporte", "credencial_escolar"]

TRANSPORTE_ECOLOGICO = ("bici", "bici_electrica", "a_pie", "scooter_electrico")
REPARTIDOR_ID = r"^R-\d{5}$"
CVEGEO_ALCALDIA = r"^09\d{3}$"


class Disponibilidad(Modelo):
    dias: list[int] = Field(description="0 = lunes … 6 = domingo")
    desde: str = Field(pattern=HORA)
    hasta: str = Field(pattern=HORA)


class Repartidor(Modelo):
    """Una línea de `data/live/repartidores.jsonl`. Solo backend: tiene los datos de prioridad."""

    id: str = Field(pattern=REPARTIDOR_ID)
    ts_alta: float
    chat_id_hash: str
    nombre_mostrar: str
    rango_edad: RangoEdad
    estudiante: bool
    alcaldia_cvegeo: str = Field(pattern=CVEGEO_ALCALDIA)
    colonias: list[str] = Field(max_length=3)
    transporte: Transporte
    disponibilidad: Disponibilidad
    id_verificada: bool = False
    tipo_id: TipoId | None = None
    estado: EstadoRepartidor = "pendiente_verificacion"
    negocio_id: str | None = None
    prioridad: int = Field(ge=0, le=2, description="§4.3; nunca se muestra a nadie")
    rutas_completadas: int = 0
    demo_data: bool = False


class RepartidorPublico(Modelo):
    """Lo que ve el propio repartidor en el portal y el bot. Ignora (no copia) los campos privados."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(pattern=REPARTIDOR_ID)
    ts_alta: float
    nombre_mostrar: str
    alcaldia_cvegeo: str
    colonias: list[str]
    transporte: Transporte
    disponibilidad: Disponibilidad
    id_verificada: bool
    estado: EstadoRepartidor
    negocio_id: str | None = None
    rutas_completadas: int
    demo_data: bool = False


class ParadaOferta(Modelo):
    lat: float
    lng: float
    h3: str
    colonia: str | None = None


class Oferta(Modelo):
    """Una línea de `data/live/ofertas.jsonl`: una ruta de entrega publicada por un negocio."""

    id: str
    ts: float
    negocio_id: str
    negocio_nombre: str | None = None
    tipo_negocio: TipoPunto = Field(description="Define el ícono del mapa (§1.3)")
    paradas: list[ParadaOferta] = Field(min_length=1)
    distancia_m: int
    minutos_est: int
    pago_est: float
    tipo_dato_pago: TipoDato
    colonia: str
    estado: EstadoOferta = "abierta"
    repartidor_id: str | None = None
    demo_data: bool = False


class Incentivo(Modelo):
    """Una entrada de `data/processed/incentivos.json`. El destacado (la bici) va primero."""

    id: str
    nombre: str
    descripcion: str
    rutas_requeridas: int = Field(gt=0)
    destacado: bool = False
    imagen: str | None = None
    patrocinador: str | None = None
    estado: EstadoIncentivo
    tipo_dato: TipoDato


class Colonia(Modelo):
    id: str
    nombre: str
    lat: float
    lng: float


class Alcaldia(Modelo):
    """Una entrada de `data/processed/colonias.json`. `prioridad` = Coyoacán e Iztapalapa (§5)."""

    alcaldia_cvegeo: str = Field(pattern=CVEGEO_ALCALDIA)
    alcaldia_nombre: str
    prioridad: bool
    colonias: list[Colonia] = Field(default_factory=list)
    fuente: str | None = None
    demo_data: bool = False


class PuntoMapa(Modelo):
    """Un punto de la capa de íconos: tianguis, mercado o negocio local (los negocios no tienen horario en DENUE)."""

    id: str
    tipo: TipoPunto
    nombre: str
    alcaldia_cvegeo: str
    colonia: str | None = None
    lat: float
    lng: float
    h3: str
    fuente: str | None = None
    tipo_dato: TipoDato


# GET /api/puntos?tipo=tianguis,mercado,negocio_local&bbox=
class PuntosResponse(Modelo):
    total: int
    puntos: list[PuntoMapa]


# GET /api/alcaldias/{cvegeo}/colonias
class ColoniasResponse(Modelo):
    alcaldia_cvegeo: str = Field(pattern=CVEGEO_ALCALDIA)
    alcaldia_nombre: str
    colonias: list[Colonia]


# POST /api/repartidores (desde el bot, al confirmar "Así queda")
class RepartidorAltaRequest(Modelo):
    chat_id: int | str = Field(description="El backend lo guarda solo como hash")
    acepta_privacidad: Literal[True]
    nombre_mostrar: str = Field(min_length=1)
    edad: int = Field(ge=18, le=99, description="Se guarda solo el rango (18-30 | 31+)")
    estudiante: bool
    alcaldia_cvegeo: str = Field(pattern=CVEGEO_ALCALDIA)
    colonias: list[str] = Field(min_length=1, max_length=3)
    transporte: Transporte
    disponibilidad: Disponibilidad
    tipo_id: TipoId | None = Field(default=None, description="None si lo dio de alta su negocio, sin identificación")
    negocio_id: str | None = None
    invitacion: str | None = Field(default=None, description="Token de `inv_<token>` si llegó por link")
    demo_data: bool = False


class RepartidorAltaResponse(Modelo):
    id: str = Field(pattern=REPARTIDOR_ID)
    estado: EstadoRepartidor
    portal_url: str
    aviso_transporte: str | None = Field(default=None, description="Sugerencia de bici si eligió moto o auto")


# POST /api/repartidores/invitacion
class InvitacionRequest(Modelo):
    negocio_id: str


class InvitacionResponse(Modelo):
    token: str
    link: str = Field(description="t.me/<bot>?start=inv_<token>")
    negocio_id: str
    expira_ts: float


# POST /api/repartidores/codigo
class CodigoRequest(Modelo):
    id: str = Field(pattern=REPARTIDOR_ID)


class CodigoResponse(Modelo):
    enviado: bool
    canal: Literal["telegram"] = "telegram"
    codigo_demo: str | None = Field(default=None, description="Solo con DEMO_MODE, para el plan B sin bot")


# POST /api/repartidores/sesion
class SesionRequest(Modelo):
    id: str = Field(pattern=REPARTIDOR_ID)
    codigo: str = Field(pattern=r"^\d{6}$")


class SesionResponse(Modelo):
    token: str
    repartidor_id: str = Field(pattern=REPARTIDOR_ID)
    expira_ts: float


# GET /api/repartidores/{id}
class AvanceIncentivo(Modelo):
    incentivo_id: str
    rutas_requeridas: int
    rutas_completadas: int
    pct: float = Field(ge=0, le=100)
    alcanzado: bool


class RepartidorPerfil(Modelo):
    repartidor: RepartidorPublico
    rutas: list[Oferta] = Field(default_factory=list, description="Tomadas y completadas por este repartidor")
    avance_incentivos: list[AvanceIncentivo]
    aviso_transporte: str | None = None


# GET /api/ofertas?repartidor_id=&desde=ts
class OfertasResponse(Modelo):
    repartidor_id: str = Field(pattern=REPARTIDOR_ID)
    ts: float = Field(description="Hora del servidor; la siguiente consulta la manda como `desde`")
    ofertas: list[Oferta] = Field(description="Abiertas en sus colonias, orden §4.3")


# POST /api/ofertas/{id}/tomar · /completar → devuelve la `Oferta` actualizada
# GET /api/incentivos → list[Incentivo], destacado primero
# GET /api/alcaldias → list[Alcaldia] (sin colonias; prioridad primero)
