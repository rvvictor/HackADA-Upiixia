// Local types for GET /api/sedeco/crecimiento (mirror of app/services/crecimiento.py).
// Replace with web/src/lib/types.ts once PB-002 lands.
export type TipoDato = "real" | "estimado" | "simulado";

export type Punto = { periodo: string; valor: number };

export type SerieAlcaldia = {
  alcaldia_cvegeo: string;
  alcaldia: string;
  indicador: string;
  puntos: Punto[];
  tipo_dato: TipoDato;
  fuente: string;
};

export type AltasHoy = {
  fecha: string;
  hoy: number;
  total: number;
  tipo_dato: TipoDato;
  fuente: string;
  archivo_disponible: boolean;
};

export type RutasPorHexagono = {
  hexagonos: { h3: string; rutas: number }[];
  total: number;
  tipo_dato: TipoDato;
  fuente: string;
  archivo_disponible: boolean;
};

export type Escala = {
  alcaldias_activas: string[];
  alcaldias_totales: number;
  parametro: string;
  costo: string;
  piezas: string[];
  tipo_dato: TipoDato;
  fuente: string;
};

export type Crecimiento = {
  generado: string;
  alcaldias: string[];
  serie_trimestral: SerieAlcaldia[];
  altas_negocios_por_anio: SerieAlcaldia[];
  altas_plataforma: AltasHoy;
  rutas_por_hexagono: RutasPorHexagono;
  escala: Escala;
  demo_data: boolean;
};
