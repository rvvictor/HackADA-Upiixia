"""Entidades de datos (IDEA.md §6), tal como las escriben los pipelines y el bot. Espejo en web/src/lib/types.ts.

Convenciones del contrato:
- `dias`: 0 = lunes … 6 = domingo, igual que `date.weekday()` en Python y que `pipeline.geo` (data/fuentes/geo.md).
  En JavaScript: `(new Date().getDay() + 6) % 7`.
- Horas `abre` / `cierra` / `hora`: texto "HH:MM" de 24 h, hora de la CDMX.
- Toda cifra visible viaja con `tipo_dato` (o `tipo_campos` en el hexágono) y la UI la muestra.
- Los modelos aceptan campos extra (`extra="allow"`): validan lo que la UI usa sin romperse si un productor agrega algo.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TipoDato = Literal["real", "estimado", "simulado"]
TipoEvento = Literal["busqueda", "aparicion_ruta", "compre_aqui", "vista_pagina", "alta"]
OrigenAlta = Literal["telegram", "campo", "demo"]
EstadoPrograma = Literal["existe", "por_verificar", "propuesta"]

HORA = r"^([01]\d|2[0-3]):[0-5]\d$"
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


def dia_desde_js(get_day: int) -> int:
    """`Date.getDay()` de JavaScript (0 = domingo) → contrato (0 = lunes, como `date.weekday()`)."""
    return (get_day + 6) % 7


class Modelo(BaseModel):
    model_config = ConfigDict(extra="allow")


class Cifra(Modelo):
    """Un número que se muestra en pantalla, con su etiqueta y su fuente."""

    valor: float | int | None
    tipo_dato: TipoDato
    fuente: str | None = None
    periodo: str | None = None


class LatLng(Modelo):
    lat: float
    lng: float


class PuntoBarrial(Modelo):
    """Tianguis Abierto v0.1 (`data/processed/tianguis_abierto.json`): tianguis o mercado."""

    id: str
    tipo: str = Field(description="tianguis · mercado")
    nombre: str
    alcaldia_cvegeo: str
    colonia: str | None = None
    lat: float
    lng: float
    h3: str
    dias: list[int] = Field(description="0 = lunes … 6 = domingo")
    abre: str = Field(pattern=HORA)
    cierra: str = Field(pattern=HORA)
    giros: list[str] = Field(default_factory=list)
    productos: list[str] = Field(default_factory=list)
    formas_pago: list[str] = Field(default_factory=list)
    acepta_mercomuna: bool | None = None
    fuente: str | None = None
    fecha_verificacion: str | None = None
    verificado_por: str | None = None
    tipo_dato: TipoDato

    def abierto_en(self, dia: int, hora: str) -> bool:
        """A.4: abierto si `dia ∈ dias` y `abre ≤ hora < cierra`."""
        return dia in self.dias and self.abre <= hora < self.cierra


class Negocio(Modelo):
    """Negocio con forma del DENUE (`data/processed/negocios.json`), con el resultado de la regla anti-cadenas."""

    id: str
    clee: str
    nombre: str
    razon_social: str = ""
    clase_scian: str
    clase_nombre: str
    estrato: str
    tipo_establecimiento: str
    lat: float
    lng: float
    h3: str
    alcaldia_cvegeo: str
    colonia: str | None = None
    fecha_alta_denue: str | None = None
    formas_pago: list[str] = Field(default_factory=list)
    acepta_mercomuna: bool | None = None
    es_barrial: bool
    motivo_exclusion: str | None
    tipo_dato: TipoDato


class HexagonoProps(Modelo):
    h3: str
    alcaldia_cvegeo: str
    poblacion: int
    negocios_barriales: int
    negocios_total: int
    actividad_tpv_est: float | None
    monto_est: float | None = None
    impulso: float = Field(ge=0, le=1)
    cluster_id: int | str | None = None
    oculto: bool
    tipo_campos: dict[str, TipoDato]
    periodo_cnbv: str


class PoligonoGeo(Modelo):
    type: Literal["Polygon"]
    coordinates: list[list[list[float]]] = Field(description="[[[lng, lat], …]] anillo cerrado")


class Hexagono(Modelo):
    type: Literal["Feature"]
    geometry: PoligonoGeo
    properties: HexagonoProps


class HexagonoColeccion(Modelo):
    type: Literal["FeatureCollection"]
    features: list[Hexagono]


class DineroAlcaldia(Modelo):
    """CNBV por alcaldía. `tpv_por_adulto` son transacciones en TPV por adulto (no pesos)."""

    cvegeo: str
    municipio: str
    trimestre: str
    transacciones_tpv: float
    monto_tpv: float | None = None
    adultos: int
    tpv_por_adulto: float
    fuente_url: str | None = None
    fecha_descarga: str | None = None
    tipo_dato: TipoDato


class Articulo(Modelo):
    articulo: str
    sinonimos: list[str] = Field(default_factory=list)
    clases_scian: list[str]
    categoria_ui: str


class Programa(Modelo):
    id: str
    nombre: str
    que_es: str
    como_entrar: str
    url_oficial: str | None = None
    estado: EstadoPrograma
    fecha_verificacion: str | None = None


class Producto(Modelo):
    nombre: str
    precio: float | None = None
    unidad: str | None = None


class FichaAlta(Modelo):
    """La ficha que el bot extrae de la nota de voz y el comerciante confirma (app/services/altas.Ficha)."""

    nombre: str
    giro: str | None = None
    clase_scian: str | None = None
    productos: list[Producto] = Field(default_factory=list)
    dias: list[int] = Field(default=[], description="0 = lunes … 6 = domingo; vacío = todos")
    abre: str | None = Field(default=None, pattern=HORA)
    cierra: str | None = Field(default=None, pattern=HORA)
    formas_pago: list[str] = Field(default_factory=list)
    acepta_mercomuna: bool | None = None
    telefono: str | None = Field(default=None, description="Solo si el comerciante lo dio para su ficha")


class Alta(Modelo):
    """Una línea de `data/live/altas.jsonl`."""

    id: str
    slug: str
    ts: float
    ficha: FichaAlta
    lat: float
    lng: float
    h3: str | None = None
    origen: OrigenAlta
    confirmado: bool
    consentimiento_publicar: bool = True
    verificado_por: str | None = None
    tianguis_id: str | None = None
    tianguis_nombre: str | None = None
    demo_data: bool = False


class Evento(Modelo):
    """Una línea de `data/live/eventos.jsonl` (o de `data/demo/plataforma_simulada.json`, con demo_data true)."""

    ts: float
    tipo: TipoEvento
    negocio_id: str | None = None
    h3: str | None = None
    demo_data: bool = False
