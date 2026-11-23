import type { GeoJSONSource, Map as MapboxMap } from "mapbox-gl";
import { useCallback, useEffect, useRef } from "react";

import { leerToken } from "../../lib/map/hex";
import { MapaBase } from "../../lib/map/MapaBase";
import type { Oferta } from "./tipos";

type FC = GeoJSON.FeatureCollection;
const VACIO: FC = { type: "FeatureCollection", features: [] };

// Mapbox no lee variables CSS: se leen los tokens al pintar (web/DESIGN.md, Maqueta viva). La ruta elegida va en
// rosa; las demás quedan en concreto para que la primera ruta resalte; el origen es tinta.
function colores() {
  return {
    origen: leerToken("--pb-texto") || "#14171c",
    parada: leerToken("--pb-borde-fuerte") || "#7c8390",
    elegida: leerToken("--pb-acento") || "#c8006a",
    borde: leerToken("--pb-superficie") || "#ffffff",
  };
}

function puntos(ofertas: Oferta[], elegida: string | null): FC {
  const features: GeoJSON.Feature[] = [];
  for (const o of ofertas) {
    const sel = o.id === elegida ? 1 : 0;
    if (o.origen) {
      features.push({
        type: "Feature",
        geometry: { type: "Point", coordinates: [o.origen.lng, o.origen.lat] },
        properties: { id: o.id, origen: 1, sel, etiqueta: "" },
      });
    }
    o.paradas.forEach((p, i) =>
      features.push({
        type: "Feature",
        geometry: { type: "Point", coordinates: [p.lng, p.lat] },
        properties: { id: o.id, origen: 0, sel, etiqueta: String(i + 1) },
      }),
    );
  }
  return { type: "FeatureCollection", features };
}

export function MapaOfertas({
  ofertas,
  elegida,
  onElegir,
}: {
  ofertas: Oferta[];
  elegida: string | null;
  onElegir: (id: string) => void;
}) {
  const mapa = useRef<MapboxMap | null>(null);
  const onElegirRef = useRef(onElegir);
  useEffect(() => {
    onElegirRef.current = onElegir;
  }, [onElegir]);

  const pintar = useCallback(() => {
    const map = mapa.current;
    if (!map) return;
    (map.getSource("ofertas") as GeoJSONSource | undefined)?.setData(puntos(ofertas, elegida));
  }, [ofertas, elegida]);
  const pintarRef = useRef(pintar);
  useEffect(() => {
    pintarRef.current = pintar;
    pintar();
  }, [pintar]);

  // The map frames the chosen offer; with none chosen, all of them. It runs when the map is ready, when offers first
  // arrive and on every new choice (CO-051: before, the first fit ran before the map existed and it stayed on the city).
  const encuadrado = useRef(false);
  const encuadrar = useCallback(
    (animar: boolean) => {
      const map = mapa.current;
      if (!map || ofertas.length === 0) return;
      const o = ofertas.find((x) => x.id === elegida);
      const lista = o ? [o] : ofertas;
      const pts = lista.flatMap((x) => [...(x.origen ? [x.origen] : []), ...x.paradas]);
      if (pts.length === 0) return;
      encuadrado.current = true;
      const opciones = { padding: 80, pitch: 0, bearing: 0, maxZoom: 15.5, duration: animar ? 700 : 0 };
      if (pts.length === 1) {
        map.easeTo({ center: [pts[0].lng, pts[0].lat], zoom: 15, pitch: 0, bearing: 0, duration: opciones.duration });
        return;
      }
      map.fitBounds(
        [
          [Math.min(...pts.map((p) => p.lng)), Math.min(...pts.map((p) => p.lat))],
          [Math.max(...pts.map((p) => p.lng)), Math.max(...pts.map((p) => p.lat))],
        ],
        opciones,
      );
    },
    [ofertas, elegida],
  );
  const encuadrarRef = useRef(encuadrar);
  useEffect(() => {
    encuadrarRef.current = encuadrar;
    // First offers after the map is ready: frame them once; later polls do not move the camera.
    if (!encuadrado.current) encuadrar(false);
  }, [encuadrar]);
  useEffect(() => {
    if (encuadrado.current) encuadrarRef.current(true);
  }, [elegida]);

  const alListo = useCallback((map: MapboxMap) => {
    mapa.current = map;
    const COLOR = colores();
    map.addSource("ofertas", { type: "geojson", data: VACIO });
    map.addLayer({
      id: "ofertas-puntos",
      type: "circle",
      source: "ofertas",
      paint: {
        "circle-radius": ["case", ["==", ["get", "sel"], 1], 17, ["==", ["get", "origen"], 1], 11, 12],
        "circle-color": [
          "case",
          ["==", ["get", "sel"], 1],
          COLOR.elegida,
          ["==", ["get", "origen"], 1],
          COLOR.origen,
          COLOR.parada,
        ],
        "circle-stroke-color": COLOR.borde,
        "circle-stroke-width": 3,
      },
    });
    map.addLayer({
      id: "ofertas-numeros",
      type: "symbol",
      source: "ofertas",
      filter: ["==", ["get", "origen"], 0],
      layout: { "text-field": ["get", "etiqueta"], "text-size": 15, "text-allow-overlap": true },
      paint: { "text-color": COLOR.borde },
    });
    map.on("click", "ofertas-puntos", (e) => {
      const id = e.features?.[0]?.properties?.id;
      if (typeof id === "string") onElegirRef.current(id);
    });
    map.on("mouseenter", "ofertas-puntos", () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", "ofertas-puntos", () => (map.getCanvas().style.cursor = ""));
    pintarRef.current();
    encuadrarRef.current(false);
  }, []);

  return <MapaBase onReady={alListo} />;
}
