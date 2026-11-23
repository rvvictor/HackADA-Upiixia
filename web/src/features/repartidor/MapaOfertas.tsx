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

  // Al elegir una oferta, el mapa se encuadra en sus puntos.
  useEffect(() => {
    const map = mapa.current;
    const o = ofertas.find((x) => x.id === elegida);
    if (!map || !o) return;
    const pts = [...(o.origen ? [o.origen] : []), ...o.paradas];
    if (pts.length < 2) return;
    map.fitBounds(
      [
        [Math.min(...pts.map((p) => p.lng)), Math.min(...pts.map((p) => p.lat))],
        [Math.max(...pts.map((p) => p.lng)), Math.max(...pts.map((p) => p.lat))],
      ],
      { padding: 80, pitch: 0, bearing: 0, duration: 700 },
    );
    // Solo al cambiar la elección, no en cada sondeo.
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
  }, []);

  return <MapaBase onReady={alListo} />;
}
