import type { FeatureCollection, Feature } from "geojson";
import type { GeoJSONSource, Map as MapboxMap } from "mapbox-gl";
import { useCallback, useEffect, useRef } from "react";

import { MapaBase } from "../../lib/map";
import { leerToken } from "../../lib/map/hex";
import type { Punto, Ruta } from "./tipos";

const VACIO: FeatureCollection = { type: "FeatureCollection", features: [] };

// Mapbox no lee variables CSS: colores de los tokens al montar (web/DESIGN.md, Maqueta viva). La ruta va en rosa,
// las paradas en tinta, el negocio recién dado de alta en rosa y el punto de salida en concreto.
const tk = (nombre: string, respaldo: string) => leerToken(nombre) || respaldo;

function paradasGeoJSON(ruta: Ruta | null, origen: Punto): FeatureCollection {
  const origenF: Feature = {
    type: "Feature",
    geometry: { type: "Point", coordinates: [origen.lng, origen.lat] },
    properties: { etiqueta: "Tú", origen: 1 },
  };
  if (!ruta) return { type: "FeatureCollection", features: [origenF] };
  return {
    type: "FeatureCollection",
    features: [
      origenF,
      ...ruta.paradas.map((p) => ({
        type: "Feature" as const,
        geometry: { type: "Point" as const, coordinates: [p.negocio.lng, p.negocio.lat] },
        properties: { etiqueta: String(p.orden), origen: 0, alta: p.negocio.tipo === "alta" ? 1 : 0 },
      })),
    ],
  };
}

export function MapaRuta({ ruta, origen }: { ruta: Ruta | null; origen: Punto }) {
  const mapa = useRef<MapboxMap | null>(null);

  const pintar = useCallback(() => {
    const map = mapa.current;
    if (!map) return;
    const linea: FeatureCollection = ruta?.geometria
      ? { type: "FeatureCollection", features: [{ type: "Feature", geometry: ruta.geometria, properties: {} }] }
      : VACIO;
    (map.getSource("ruta-linea") as GeoJSONSource | undefined)?.setData(linea);
    (map.getSource("ruta-paradas") as GeoJSONSource | undefined)?.setData(paradasGeoJSON(ruta, origen));
    const puntos = ruta ? [origen, ...ruta.paradas.map((p) => ({ lat: p.negocio.lat, lng: p.negocio.lng }))] : [origen];
    if (puntos.length > 1) {
      const lngs = puntos.map((p) => p.lng);
      const lats = puntos.map((p) => p.lat);
      map.fitBounds(
        [[Math.min(...lngs), Math.min(...lats)], [Math.max(...lngs), Math.max(...lats)]],
        { padding: 70, pitch: 0, bearing: 0, duration: 900 },
      );
    } else {
      map.easeTo({ center: [origen.lng, origen.lat], zoom: 15, pitch: 0, bearing: 0, duration: 600 });
    }
  }, [ruta, origen]);

  const alListo = useCallback(
    (map: MapboxMap) => {
      mapa.current = map;
      map.addSource("ruta-linea", { type: "geojson", data: VACIO });
      map.addSource("ruta-paradas", { type: "geojson", data: VACIO });
      map.addLayer({
        id: "ruta-linea",
        type: "line",
        source: "ruta-linea",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": tk("--pb-acento", "#c8006a"), "line-width": 5, "line-opacity": 0.85 },
      });
      map.addLayer({
        id: "ruta-paradas",
        type: "circle",
        source: "ruta-paradas",
        paint: {
          "circle-radius": ["case", ["==", ["get", "origen"], 1], 11, 15],
          "circle-color": [
            "case",
            ["==", ["get", "origen"], 1],
            tk("--pb-borde-fuerte", "#7c8390"),
            ["==", ["get", "alta"], 1],
            tk("--pb-acento", "#c8006a"),
            tk("--pb-texto", "#14171c"),
          ],
          "circle-stroke-color": tk("--pb-superficie", "#ffffff"),
          "circle-stroke-width": 3,
        },
      });
      map.addLayer({
        id: "ruta-numeros",
        type: "symbol",
        source: "ruta-paradas",
        filter: ["==", ["get", "origen"], 0],
        layout: { "text-field": ["get", "etiqueta"], "text-size": 15, "text-allow-overlap": true },
        paint: { "text-color": tk("--pb-superficie", "#ffffff") },
      });
      pintarRef.current();
    },
    // The layers are created once; later changes go through pintar() in the effect below.
    [],
  );

  // MapaBase calls onReady once; the ref lets it paint the latest route even if it changed while loading.
  const pintarRef = useRef(pintar);
  useEffect(() => {
    pintarRef.current = pintar;
    pintar();
  }, [pintar]);

  return <MapaBase onReady={alListo} className="rounded-(--pb-radio-tarjeta)" />;
}
