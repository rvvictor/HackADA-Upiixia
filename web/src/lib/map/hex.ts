import { cellToBoundary } from "h3-js";
import type { ExpressionSpecification, FillExtrusionLayerSpecification } from "mapbox-gl";

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
export function colorPorRampa(propiedad: string, rampa: Rampa): ExpressionSpecification {
  const colores = coloresRampa(rampa);
  return [
    "interpolate",
    ["linear"],
    ["coalesce", ["get", propiedad], 0],
    ...colores.flatMap((c, i) => [i / (colores.length - 1), c]),
  ] as ExpressionSpecification;
}

type OpcionesCapa = {
  /** Property mapped to color (0–1). */
  color: string;
  rampa: Rampa;
  /** Property mapped to height (0–1); `alturaMax` meters at 1. */
  altura?: string;
  alturaMax?: number;
  /** Boolean property: hidden cells (< 3 businesses) are drawn flat and gray. */
  oculto?: string;
};

/** Ready-to-add layer spec: `map.addLayer(capaHexExtrusion("hex", "hex", {...}))`. */
export function capaHexExtrusion(
  id: string,
  source: string,
  { color, rampa, altura, alturaMax = 1200, oculto = "oculto" }: OpcionesCapa,
): FillExtrusionLayerSpecification {
  const esOculto: ExpressionSpecification = ["==", ["get", oculto], true];
  return {
    id,
    type: "fill-extrusion",
    source,
    paint: {
      "fill-extrusion-color": ["case", esOculto, leerToken("--pb-oculto"), colorPorRampa(color, rampa)],
      "fill-extrusion-height": altura
        ? ["case", esOculto, 0, ["*", ["coalesce", ["get", altura], 0], alturaMax]]
        : 0,
      "fill-extrusion-opacity": 0.85,
      "fill-extrusion-vertical-gradient": true,
    },
  };
}
