import { cellToBoundary } from "h3-js";
import type { ExpressionSpecification, FillExtrusionLayerSpecification, Map as MapboxMap } from "mapbox-gl";

// H3 cells (resolution 9, IDEA.md A.1) → GeoJSON polygons for `fill-extrusion` layers.

export type PoligonoHex<P> = {
  type: "Feature";
  id?: number;
  geometry: { type: "Polygon"; coordinates: [number, number][][] };
  properties: P & { h3: string };
};

export type ColeccionHex<P> = { type: "FeatureCollection"; features: PoligonoHex<P>[] };

/** One polygon per cell; every other field of the row goes into `properties`. */
export function celdasAGeoJSON<P extends { h3: string }>(celdas: P[]): ColeccionHex<P> {
  return {
    type: "FeatureCollection",
    features: celdas.map((celda, i) => {
      const anillo = cellToBoundary(celda.h3, true) as [number, number][]; // [lng, lat], ring already closed
      return {
        type: "Feature",
        id: i,
        geometry: { type: "Polygon", coordinates: [anillo] },
        properties: celda,
      };
    }),
  };
}

export type Rampa = "actividad" | "impulso";

/** Reads a CSS token at runtime so map colors come from tokens.css like the rest of the UI. */
export function leerToken(nombre: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
}

export function coloresRampa(rampa: Rampa): string[] {
  return [1, 2, 3, 4, 5].map((n) => leerToken(`--pb-${rampa}-${n}`));
}

/** `interpolate` over a 0–1 property (percentile or normalized index) using the 5 steps of the ramp. */
export function colorPorRampa(propiedad: string, rampa: Rampa, pasos?: string[]): ExpressionSpecification {
  const colores = pasos ?? coloresRampa(rampa);
  return [
    "interpolate",
    ["linear"],
    ["coalesce", ["get", propiedad], 0],
    ...colores.flatMap((c, i) => [i / (colores.length - 1), c]),
  ] as ExpressionSpecification;
}

// ---------- Capas: una capa = una métrica (IDEA-v2 §1.2) ----------

export type TipoDatoCapa = "real" | "estimado" | "simulado";
export type Capa = "actividad" | "oferta" | "poblacion" | "impulso" | "crecimiento" | "rutas";

export type MetaCapa = {
  id: Capa;
  texto: string;
  /** Nombre de la métrica en la leyenda. */
  metrica: string;
  /** Propiedad 0–1 del hexágono de la que salen altura Y color. */
  propiedad: string;
  rampa: Rampa;
  tipo_dato: TipoDatoCapa;
  fuente: string;
};

export const CAPAS: MetaCapa[] = [
  {
    id: "actividad", texto: "Actividad", metrica: "Actividad con tarjeta (actividad_tpv_est)",
    propiedad: "n_actividad", rampa: "actividad", tipo_dato: "estimado", fuente: "CNBV por alcaldía, repartido por negocios",
  },
  {
    id: "oferta", texto: "Oferta barrial", metrica: "Negocios de barrio (negocios_barriales)",
    propiedad: "n_negocios", rampa: "actividad", tipo_dato: "real", fuente: "DENUE y Tianguis Abierto (pipeline)",
  },
  {
    id: "poblacion", texto: "Población", metrica: "Población (poblacion)",
    propiedad: "n_poblacion", rampa: "actividad", tipo_dato: "real", fuente: "hexágonos del pipeline (data/processed/hex.geojson)",
  },
  {
    id: "impulso", texto: "Impulso", metrica: "Índice de impulso (impulso)",
    propiedad: "impulso", rampa: "impulso", tipo_dato: "estimado", fuente: "Índice propio del pipeline",
  },
  {
    id: "crecimiento", texto: "Crecimiento", metrica: "Altas de negocios (altas)",
    propiedad: "n_altas", rampa: "impulso", tipo_dato: "real", fuente: "Altas registradas en la plataforma",
  },
  {
    id: "rutas", texto: "Rutas", metrica: "Rutas por hexágono (rutas)",
    propiedad: "n_rutas", rampa: "impulso", tipo_dato: "simulado", fuente: "GET /api/sedeco/crecimiento (rutas_por_hexagono)",
  },
];

export function metaCapa(capa: Capa): MetaCapa {
  return CAPAS.find((c) => c.id === capa) ?? CAPAS[0];
}

/** Propiedad única (0–1) que alimenta altura y color de la capa. */
export function propiedadCapa(capa: Capa): string {
  return metaCapa(capa).propiedad;
}

const alturaMaxima = 1200;

const esOculto: ExpressionSpecification = ["==", ["get", "oculto"], true];

/** Altura en metros: la métrica de la capa × alturaMax; hexágonos ocultos (< 3 negocios) planos. */
export function expresionAltura(capa: Capa): ExpressionSpecification {
  return ["case", esOculto, 0, ["*", ["coalesce", ["get", propiedadCapa(capa)], 0], alturaMaxima]];
}

/** Color: la MISMA propiedad que la altura pasada por la rampa de la capa; ocultos en gris. */
export function expresionColor(capa: Capa, colores?: string[]): ExpressionSpecification {
  const meta = metaCapa(capa);
  return ["case", esOculto, leerToken("--pb-oculto"), colorPorRampa(meta.propiedad, meta.rampa, colores)];
}

/** Fija altura y color de la capa "hex-3d" con la misma métrica. */
export function pintarCapa(map: MapboxMap, capa: Capa, capaId = "hex-3d"): void {
  map.setPaintProperty(capaId, "fill-extrusion-height", expresionAltura(capa));
  map.setPaintProperty(capaId, "fill-extrusion-color", expresionColor(capa));
}

/** Layer spec listo para `map.addLayer`, ya pintado con la capa. */
export function capaHexExtrusion(id: string, source: string, capa: Capa): FillExtrusionLayerSpecification {
  return {
    id,
    type: "fill-extrusion",
    source,
    paint: {
      "fill-extrusion-color": expresionColor(capa),
      "fill-extrusion-height": expresionAltura(capa),
      "fill-extrusion-opacity": 0.85,
      "fill-extrusion-vertical-gradient": true,
    },
  };
}
