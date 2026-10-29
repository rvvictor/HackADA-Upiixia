import mapboxgl, { type FilterSpecification } from "mapbox-gl";
import { useEffect, useRef, useState } from "react";
import { pintarCapa } from "../../lib/map/hex";
import { agregarIconos, CAPA_CLUSTER, CAPA_ICONOS, FUENTE_PUNTOS } from "../../lib/map/iconos";
import type { PuntoMapa } from "./puntos";
import type { Alta, CapaHex, ColeccionHex, Tianguis } from "./datos";

// Cámara inicial: 50° sobre Coyoacán con Iztapalapa a la vista (IDEA.md §4 paso 1).
const CAMARA = { center: [-99.118, 19.352] as [number, number], zoom: 11.7, pitch: 50, bearing: -12 };
const GRIS = "#c3c9d0";
const COLOR_ALCALDIA: Record<string, string> = { "09003": "#c2410c", "09007": "#0e5c58" };

type Props = {
  hex: ColeccionHex;
  capa: CapaHex;
  datoReal: boolean;
  tianguis: Tianguis[];
  puntos?: PuntoMapa[];
  altas: Alta[];
  seleccionado: string | null;
  onSeleccion: (h3: string | null) => void;
};

function pintarHex(map: mapboxgl.Map, capa: CapaHex, datoReal: boolean) {
  pintarCapa(map, capa);
  if (!datoReal) return;
  // "Ver dato real": sin altura estimada, solo el color por alcaldía.
  map.setPaintProperty("hex-3d", "fill-extrusion-height", 0);
  map.setPaintProperty("hex-3d", "fill-extrusion-color", [
    "case",
    ["==", ["get", "oculto"], true],
    GRIS,
    ["match", ["get", "alcaldia_cvegeo"], "09003", COLOR_ALCALDIA["09003"], "09007", COLOR_ALCALDIA["09007"], GRIS],
  ]);
}

export function MapaHex({ hex, capa, datoReal, tianguis, puntos = [], altas, seleccionado, onSeleccion }: Props) {
  const contenedor = useRef<HTMLDivElement>(null);
  const mapaRef = useRef<mapboxgl.Map | null>(null);
  const marcasRef = useRef(new Map<string, mapboxgl.Marker>());
  const seleccionRef = useRef(onSeleccion);
  const [listo, setListo] = useState(false);
  const [estado, setEstado] = useState<"cargando" | "sin-token" | "error" | "listo">("cargando");
  const token = import.meta.env.VITE_MAPBOX_TOKEN;

  useEffect(() => {
    seleccionRef.current = onSeleccion;
  }, [onSeleccion]);

  // Mapa: se crea una vez por llave. Sin llave no hay mapa, pero el panel sigue funcionando.
  useEffect(() => {
    if (!token) {
      queueMicrotask(() => setEstado("sin-token"));
      return;
    }
    if (!contenedor.current) return;
    let mapa: mapboxgl.Map;
    try {
      mapboxgl.accessToken = token;
      mapa = new mapboxgl.Map({ container: contenedor.current, style: "mapbox://styles/mapbox/light-v11", ...CAMARA, antialias: true });
    } catch {
      queueMicrotask(() => setEstado("error"));
      return;
    }
    mapaRef.current = mapa;
    mapa.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), "top-right");
    mapa.on("error", (e) => {
      if (!mapa.isStyleLoaded()) setEstado("error");
      console.warn("Mapbox:", e.error?.message ?? e);
    });
    mapa.on("load", () => {
      mapa.addSource("hex", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      mapa.addLayer({
        id: "hex-3d",
        type: "fill-extrusion",
        source: "hex",
        paint: { "fill-extrusion-opacity": 0.88, "fill-extrusion-vertical-gradient": true },
      });
      mapa.on("click", CAPA_ICONOS, (e) => {
        const pr = e.features?.[0]?.properties ?? {};
        new mapboxgl.Popup({ offset: 12 })
          .setLngLat(e.lngLat)
          .setText(`${pr.nombre || pr.tipo} (${pr.tipo}). ${pr.tipo_dato} · Fuente: ${pr.fuente}`)
          .addTo(mapa);
      });
      mapa.on("click", CAPA_CLUSTER, (e) => {
        const f = e.features?.[0];
        if (!f) return;
        mapa.easeTo({ center: (f.geometry as GeoJSON.Point).coordinates as [number, number], zoom: mapa.getZoom() + 2 });
      });
      mapa.addSource("tianguis", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      mapa.addLayer({
        id: "tianguis",
        type: "circle",
        source: "tianguis",
        paint: { "circle-radius": 11, "circle-color": "#c2410c", "circle-opacity": 0.15, "circle-stroke-color": "#c2410c", "circle-stroke-width": 2 },
      });
      mapa.on("click", "hex-3d", (e) => {
        const h3 = e.features?.[0]?.properties?.h3;
        if (typeof h3 === "string") seleccionRef.current(h3);
      });
      mapa.on("click", "tianguis", (e) => {
        const f = e.features?.[0];
        if (!f) return;
        const nombre = String(f.properties?.nombre ?? "");
        const horario = `${f.properties?.abre ?? ""} a ${f.properties?.cierra ?? ""}`;
        new mapboxgl.Popup({ offset: 12 }).setLngLat(e.lngLat).setText(`${nombre}. Abre de ${horario}.`).addTo(mapa);
      });
      mapa.on("mouseenter", "hex-3d", () => (mapa.getCanvas().style.cursor = "pointer"));
      mapa.on("mouseleave", "hex-3d", () => (mapa.getCanvas().style.cursor = ""));
      setEstado("listo");
      setListo(true);
    });
    const marcas = marcasRef.current;
    return () => {
      marcas.forEach((m) => m.remove());
      marcas.clear();
      mapa.remove();
      mapaRef.current = null;
      setListo(false);
    };
  }, [token]);

  // Hexágonos: datos y pintura.
  useEffect(() => {
    const mapa = mapaRef.current;
    if (!listo || !mapa) return;
    (mapa.getSource("hex") as mapboxgl.GeoJSONSource).setData(hex as unknown as Parameters<mapboxgl.GeoJSONSource["setData"]>[0]);
  }, [listo, hex]);

  useEffect(() => {
    const mapa = mapaRef.current;
    if (!listo || !mapa) return;
    pintarHex(mapa, capa, datoReal);
  }, [listo, capa, datoReal, hex]);

  // Tianguis abiertos.
  useEffect(() => {
    const mapa = mapaRef.current;
    if (!listo || !mapa) return;
    (mapa.getSource("tianguis") as mapboxgl.GeoJSONSource).setData({
      type: "FeatureCollection",
      features: tianguis.map((t) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [t.lng, t.lat] },
        properties: { nombre: t.nombre, abre: t.abre, cierra: t.cierra },
      })),
    });
  }, [listo, tianguis]);

  useEffect(() => {
    const mapa = mapaRef.current;
    if (!mapa || !listo) return;
    void agregarIconos(mapa, puntos.map((p) => ({ id: p.id, tipo: p.tipo, nombre: p.nombre, lat: p.lat, lng: p.lng }))).then(() => {
      const fuente = mapa.getSource(FUENTE_PUNTOS) as mapboxgl.GeoJSONSource | undefined;
      fuente?.setData({
        type: "FeatureCollection",
        features: puntos.map((p) => ({
          type: "Feature" as const,
          id: p.id,
          geometry: { type: "Point" as const, coordinates: [p.lng, p.lat] },
          properties: { id: p.id, tipo: p.tipo, nombre: p.nombre ?? "", icono: `icono-${p.tipo}`, tipo_dato: p.tipo_dato, fuente: p.fuente },
        })),
      });
    });
  }, [listo, puntos]);

  // Altas nuevas: punto que pulsa.
  useEffect(() => {
    const mapa = mapaRef.current;
    if (!listo || !mapa) return;
    const marcas = marcasRef.current;
    for (const a of altas) {
      const lat = a.lat ?? a.ficha?.lat;
      const lng = a.lng ?? a.ficha?.lng;
      if (lat == null || lng == null || marcas.has(a.id)) continue;
      const el = document.createElement("div");
      el.className = "relative size-5";
      el.title = a.ficha?.nombre ?? "Nueva alta";
      el.innerHTML =
        '<span class="absolute inset-0 rounded-full bg-[#c2410c] opacity-60 animate-ping motion-reduce:animate-none"></span>' +
        '<span class="absolute inset-1 rounded-full border-2 border-white bg-[#c2410c]"></span>';
      marcas.set(a.id, new mapboxgl.Marker({ element: el }).setLngLat([lng, lat]).addTo(mapa));
    }
  }, [listo, altas]);

  // Resalta el hexágono elegido con un borde.
  useEffect(() => {
    const mapa = mapaRef.current;
    if (!listo || !mapa) return;
    const filtro: FilterSpecification = ["==", ["get", "h3"], seleccionado ?? ""];
    if (!mapa.getLayer("hex-sel")) {
      mapa.addLayer({ id: "hex-sel", type: "line", source: "hex", paint: { "line-color": "#15191e", "line-width": 3 }, filter: filtro });
    } else {
      mapa.setFilter("hex-sel", filtro);
    }
  }, [listo, seleccionado]);

  const aviso =
    estado === "sin-token"
      ? { titulo: "El mapa necesita una llave de Mapbox", texto: "Agrega VITE_MAPBOX_TOKEN en el archivo .env y vuelve a abrir la página. El panel de la derecha sigue funcionando." }
      : estado === "error"
        ? { titulo: "No se pudo cargar el mapa", texto: "Revisa la conexión a internet o la llave de Mapbox. El panel de la derecha sigue funcionando." }
        : null;

  return (
    <div className="relative h-full w-full overflow-hidden bg-stone-200">
      <div ref={contenedor} className="h-full w-full" role="region" aria-label="Mapa de Coyoacán e Iztapalapa" />
      {estado === "cargando" && token && (
        <div className="absolute inset-0 flex items-center justify-center text-lg text-stone-700" role="status">
          Cargando mapa…
        </div>
      )}
      {aviso && (
        <div role="status" className="absolute inset-0 flex items-center justify-center p-6 lg:pl-[22rem]">
          <div className="max-w-md rounded-2xl border border-stone-400 bg-white p-6 shadow-md">
            <p className="text-xl font-semibold text-stone-900">{aviso.titulo}</p>
            <p className="mt-2 text-lg leading-relaxed text-stone-800">{aviso.texto}</p>
          </div>
        </div>
      )}
    </div>
  );
}
