// Icons by point type, clustering and counts on a Mapbox map (CO-007). Wired into the map in CO-012.
import type { GeoJSONSource, Map as MapaMapbox } from "mapbox-gl";
import type { TipoPunto } from "../types";

export type TipoIcono = { id: TipoPunto; etiqueta: string; icono: string; color: string; forma: string };

/** Distinct shape per type (circle, square, triangle), so it does not rely on color alone. */
export const TIPOS_ICONO: TipoIcono[] = [
  { id: "tianguis", etiqueta: "Tianguis", icono: "/iconos/tianguis.svg", color: "#c2410c", forma: "círculo" },
  { id: "mercado", etiqueta: "Mercado", icono: "/iconos/mercado.svg", color: "#0e5c58", forma: "cuadro" },
  { id: "negocio_local", etiqueta: "Negocio local", icono: "/iconos/negocio.svg", color: "#4338ca", forma: "triángulo" },
];

export type PuntoIcono = { id: string; tipo: TipoPunto; nombre: string | null; lat: number; lng: number };

export const FUENTE_PUNTOS = "puntos-tipo";
export const CAPA_CLUSTER = "puntos-cluster";
export const CAPA_CONTEO = "puntos-conteo";
export const CAPA_ICONOS = "puntos-iconos";

const nombreImagen = (t: TipoPunto) => `icono-${t}`;

function cargarImagen(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image(32, 32);
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`no se pudo cargar ${src}`));
    img.src = src;
  });
}

function aGeoJSON(puntos: PuntoIcono[]): GeoJSON.FeatureCollection<GeoJSON.Point> {
  return {
    type: "FeatureCollection",
    features: puntos.map((p) => ({
      type: "Feature",
      id: p.id,
      geometry: { type: "Point", coordinates: [p.lng, p.lat] },
      properties: { id: p.id, tipo: p.tipo, nombre: p.nombre ?? "", icono: nombreImagen(p.tipo) },
    })),
  };
}

/** Registers the 3 icons and adds a clustered source with count and per-type icon layers. Idempotent. */
export async function agregarIconos(map: MapaMapbox, puntos: PuntoIcono[]): Promise<void> {
  await Promise.all(
    TIPOS_ICONO.map(async (t) => {
      const nombre = nombreImagen(t.id);
      if (!map.hasImage(nombre)) {
        const img = await cargarImagen(t.icono);
        if (!map.hasImage(nombre)) map.addImage(nombre, img, { pixelRatio: 2 });
      }
    }),
  );

  const existente = map.getSource(FUENTE_PUNTOS) as GeoJSONSource | undefined;
  if (existente) {
    existente.setData(aGeoJSON(puntos));
    return;
  }
  map.addSource(FUENTE_PUNTOS, { type: "geojson", data: aGeoJSON(puntos), cluster: true, clusterRadius: 40, clusterMaxZoom: 14 });
  map.addLayer({
    id: CAPA_CLUSTER,
    type: "circle",
    source: FUENTE_PUNTOS,
    filter: ["has", "point_count"],
    paint: {
      "circle-color": "#1c1917",
      "circle-opacity": 0.85,
      "circle-stroke-color": "#fff",
      "circle-stroke-width": 2,
      "circle-radius": ["step", ["get", "point_count"], 14, 20, 18, 100, 24],
    },
  });
  map.addLayer({
    id: CAPA_CONTEO,
    type: "symbol",
    source: FUENTE_PUNTOS,
    filter: ["has", "point_count"],
    layout: { "text-field": ["get", "point_count_abbreviated"], "text-size": 13, "text-font": ["DIN Pro Bold", "Arial Unicode MS Bold"] },
    paint: { "text-color": "#fff" },
  });
  map.addLayer({
    id: CAPA_ICONOS,
    type: "symbol",
    source: FUENTE_PUNTOS,
    filter: ["!", ["has", "point_count"]],
    layout: { "icon-image": ["get", "icono"], "icon-size": ["interpolate", ["linear"], ["zoom"], 8, 0.7, 11, 1, 14, 1.5, 17, 2], "icon-allow-overlap": true },
  });
}

/** Shows only the active types; clusters are rebuilt from the filtered data. */
export function filtrarTipos(map: MapaMapbox, puntos: PuntoIcono[], activos: TipoPunto[]): void {
  const fuente = map.getSource(FUENTE_PUNTOS) as GeoJSONSource | undefined;
  fuente?.setData(aGeoJSON(puntos.filter((p) => activos.includes(p.tipo))));
}
