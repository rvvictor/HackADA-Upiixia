// Mirror of app/schemas/ (PB-002): what the API really serves, same field names, snake_case.
// Mocks: app/fixtures/<endpoint>.json, generated from the live API in DEMO_MODE (app/tests/test_schemas.py checks both).
// `dias`: 0 = lunes … 6 = domingo (Python weekday). From JS: diaDesdeJs(new Date().getDay()).

export type TipoDato = "real" | "estimado" | "simulado";
export type TipoEvento = "busqueda" | "aparicion_ruta" | "compre_aqui" | "vista_pagina" | "alta";
export type OrigenAlta = "telegram" | "campo" | "demo";
export type EstadoPrograma = "existe" | "por_verificar" | "propuesta";

export const DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"] as const;

/** JS `Date.getDay()` (0 = domingo) → contract day (0 = lunes). */
export function diaDesdeJs(getDay: number): number {
  return (getDay + 6) % 7;
}

export interface Cifra {
  valor: number | null;
  tipo_dato: TipoDato;
  fuente?: string | null;
  periodo?: string | null;
}

export interface LatLng {
  lat: number;
  lng: number;
}

// ---------- Entities (data/processed, data/live) ----------

export interface PuntoBarrial {
  id: string;
  tipo: string; // tianguis · mercado
  nombre: string;
  alcaldia_cvegeo: string;
  colonia: string | null;
  lat: number;
  lng: number;
  h3: string;
  dias: number[]; // 0 = lunes … 6 = domingo
  abre: string; // "HH:MM"
  cierra: string;
  giros: string[];
  productos: string[];
  formas_pago: string[];
  acepta_mercomuna: boolean | null;
  fuente: string | null;
  fecha_verificacion: string | null;
  verificado_por: string | null;
  tipo_dato: TipoDato;
}

export interface Negocio {
  id: string;
  clee: string;
  nombre: string;
  razon_social: string;
  clase_scian: string;
  clase_nombre: string;
  estrato: string;
  tipo_establecimiento: string;
  lat: number;
  lng: number;
  h3: string;
  alcaldia_cvegeo: string;
  colonia: string | null;
  fecha_alta_denue: string | null;
  formas_pago: string[];
  acepta_mercomuna: boolean | null;
  es_barrial: boolean;
  motivo_exclusion: string | null;
  tipo_dato: TipoDato;
}

export interface HexagonoProps {
  h3: string;
  alcaldia_cvegeo: string;
  poblacion: number;
  negocios_barriales: number;
  negocios_total: number;
  actividad_tpv_est: number | null; // null when oculto
  monto_est: number | null;
  impulso: number; // 0–1
  cluster_id: number | string | null;
  oculto: boolean; // < 3 negocios: no figures, grey
  tipo_campos: Record<string, TipoDato>;
  periodo_cnbv: string;
}

export interface Hexagono {
  type: "Feature";
  geometry: { type: "Polygon"; coordinates: [number, number][][] };
  properties: HexagonoProps;
}

export interface HexagonoColeccion {
  type: "FeatureCollection";
  features: Hexagono[];
  meta?: Record<string, unknown>;
}

/** CNBV per alcaldía. `tpv_por_adulto` = POS transactions per adult (not pesos). */
export interface DineroAlcaldia {
  cvegeo: string;
  municipio: string;
  trimestre: string;
  transacciones_tpv: number;
  monto_tpv: number | null;
  adultos: number;
  tpv_por_adulto: number;
  fuente_url: string | null;
  fecha_descarga: string | null;
  tipo_dato: TipoDato;
}

export interface Programa {
  id: string;
  nombre: string;
  que_es: string;
  como_entrar: string;
  url_oficial: string | null;
  estado: EstadoPrograma;
  fecha_verificacion: string | null;
}

export interface Producto {
  nombre: string;
  precio: number | null;
  unidad: string | null;
}

/** The ficha the bot extracts from a voice note and the merchant confirms. */
export interface FichaAlta {
  nombre: string;
  giro: string | null;
  clase_scian: string | null;
  productos: Producto[];
  dias: number[]; // empty = every day
  abre: string | null;
  cierra: string | null;
  formas_pago: string[];
  acepta_mercomuna: boolean | null;
  telefono: string | null;
}

export interface Alta {
  id: string;
  slug: string;
  ts: number;
  ficha: FichaAlta;
  lat: number;
  lng: number;
  h3: string | null;
  origen: OrigenAlta;
  confirmado: boolean;
  consentimiento_publicar: boolean;
  verificado_por: string | null;
  tianguis_id: string | null;
  tianguis_nombre: string | null;
  demo_data: boolean;
}

// ---------- API responses ----------

/** GET /api/tianguis?dia=0-6&hora=HH:MM */
export interface TianguisResponse {
  dia: number;
  dia_nombre: string;
  hora: string;
  total: number;
  abiertos: number;
  puntos: (PuntoBarrial & { abierto: boolean })[];
  cobertura: {
    poblacion_total: number;
    poblacion_cubierta: number;
    poblacion_cubierta_pct: number;
    desiertos: string[];
    radio_m: number;
    tipo_dato: TipoDato;
    metodo: string;
  };
  origen: "processed" | "fixture" | "vacio";
}

/** GET /api/sedeco/resumen */
export interface SedecoResumen {
  altas_hoy: number;
  rutas_por_hexagono: Record<string, number>;
  dia: number;
  hora: string;
  abiertos: number;
  poblacion_cubierta_pct: number;
  desiertos: number;
  tipo_campos: Record<string, TipoDato>;
}

/** POST /api/articulos/interpretar */
export interface ArticulosResponse {
  items: {
    texto: string;
    articulo: string;
    cantidad: number | null;
    unidad: string | null;
    clases: string[];
    fuente: "diccionario" | "sinonimo" | "difuso" | "llm";
  }[];
  sin_resultado: string[];
}

/** POST /api/ruta */
export interface RutaRequest {
  origen?: LatLng;
  texto_lista: string;
  dia?: number | null;
  hora?: string | null;
  radio_m?: number;
  alpha?: number;
  regresar?: boolean;
}

export interface LugarRuta {
  id: string;
  nombre: string;
  tipo: "negocio" | "tianguis" | "mercado" | "alta";
  giro: string;
  lat: number;
  lng: number;
  h3: string | null;
  formas_pago: string[];
  acepta_mercomuna: boolean | null;
  tipo_dato: TipoDato;
  horario_verificado: boolean;
  impulso: number;
}

export interface Parada {
  orden: number;
  negocio: LugarRuta;
  articulos: string[];
  por_que: string[];
}

export interface RutaResponse {
  paradas: Parada[];
  geometria: { type: "LineString"; coordinates: [number, number][] } | null;
  distancia_m: number;
  minutos: number;
  resumen: { barrial_pct: number; cadenas: number; paradas_impulso: number };
  sin_resultado: string[];
  aviso: string | null;
  demo_data: boolean;
}

/** POST /api/eventos */
export interface EventoRequest {
  tipo: "busqueda" | "compre_aqui";
  negocio_id?: string | null;
  h3?: string | null;
}

/** GET /api/altas/live?desde=ts — send `ultimo_ts` as the next `desde`. */
export interface AltasLive {
  altas: Alta[];
  desde: number;
  ultimo_ts: number;
}

/** GET /api/negocio/{id} */
export interface NegocioDetalle {
  id: string;
  origen: string;
  ficha: {
    nombre: string;
    giro: string | null;
    colonia: string | null;
    telefono: string | null;
    horario: string | null;
    formas_pago: string[];
    productos: Producto[];
    acepta_mercomuna: boolean | null;
    ubicacion: string | null;
    aparecer_en_rutas: boolean;
  };
  descripcion: string | null;
  avance: { tipo_dato: TipoDato; dias: number; conteos: Record<string, number> };
  escalera: { orden: number; nombre: string; estado: string; beneficio: string; siguiente_accion: string | null }[];
  programas: Programa[];
  pagina: { url: string; cartel: string } | null;
}

/** POST /api/negocio/{id}/pagina */
export interface Pagina {
  slug: string;
  url: string;
  url_completa: string | null;
  cartel: string;
  qr: string; // data:image/png;base64,…
}

/** GET /api/sedeco/crecimiento */
export interface SerieIndicador {
  alcaldia_cvegeo: string;
  alcaldia: string;
  indicador: string;
  puntos: Record<string, unknown>[];
  tipo_dato: TipoDato;
  fuente: string;
}

export interface SedecoCrecimiento {
  alcaldias: string[];
  serie_trimestral: SerieIndicador[];
  altas_negocios_por_anio: SerieIndicador[];
  altas_plataforma: Record<string, unknown>;
  rutas_por_hexagono: Record<string, unknown>;
  escala: Record<string, unknown>;
  demo_data: boolean;
}
