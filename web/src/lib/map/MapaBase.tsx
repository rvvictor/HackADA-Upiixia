import mapboxgl from "mapbox-gl";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { CAMARA_INICIAL } from "./camara";

type MapaBaseProps = {
  /** Called once the style has loaded: add sources and layers here. */
  onReady?: (map: mapboxgl.Map) => void;
  className?: string;
  /** Overlays drawn on top of the map (legend, card for the selected hexagon). */
  children?: ReactNode;
  /** "claro" (default) for the app views, "oscuro" for hero and presentation moments. */
  estilo?: "claro" | "oscuro";
};

const ESTILOS = {
  claro: "mapbox://styles/mapbox/light-v11",
  oscuro: "mapbox://styles/mapbox/dark-v11",
};

type Estado = "cargando" | "listo" | "sin-token" | "error";

export function MapaBase({ onReady, className = "", children, estilo = "claro" }: MapaBaseProps) {
  const contenedor = useRef<HTMLDivElement>(null);
  const onReadyRef = useRef(onReady);
  useEffect(() => {
    onReadyRef.current = onReady;
  }, [onReady]);
  const token = import.meta.env.VITE_MAPBOX_TOKEN;
  const [estado, setEstado] = useState<Estado>(token ? "cargando" : "sin-token");

  useEffect(() => {
    if (!token || !contenedor.current) return;
    let map: mapboxgl.Map;
    try {
      map = new mapboxgl.Map({
        container: contenedor.current,
        accessToken: token,
        style: ESTILOS[estilo],
        ...CAMARA_INICIAL,
        antialias: true,
        attributionControl: true,
      });
    } catch {
      // No WebGL (old projector laptop): deferred so the effect does not set state synchronously.
      queueMicrotask(() => setEstado("error"));
      return;
    }
    map.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), "top-right");
    map.on("load", () => {
      setEstado("listo");
      onReadyRef.current?.(map);
    });
    // A bad token or no network fails the style request; show the notice instead of a blank box.
    map.on("error", (e) => {
      if (!map.isStyleLoaded()) setEstado("error");
      console.warn("Mapbox:", e.error?.message ?? e);
    });
    return () => map.remove();
  }, [token, estilo]);

  return (
    <div className={`relative h-full min-h-80 w-full overflow-hidden bg-(--pb-superficie-2) ${className}`}>
      <div ref={contenedor} className="absolute inset-0" aria-label="Mapa de Coyoacán e Iztapalapa" role="region" />
      {estado === "cargando" && (
        <div className="absolute inset-0 animate-pulse bg-(--pb-superficie-2)" aria-hidden="true" />
      )}
      {(estado === "sin-token" || estado === "error") && <AvisoMapa estado={estado} />}
      {estado === "listo" && children}
    </div>
  );
}

function AvisoMapa({ estado }: { estado: "sin-token" | "error" }) {
  return (
    <div role="status" className="absolute inset-0 flex items-center justify-center p-6">
      <div className="max-w-md rounded-(--pb-radio-tarjeta) border border-(--pb-borde) bg-(--pb-superficie) p-6 shadow-(--pb-sombra)">
        <p className="text-[1.222rem] font-semibold leading-tight">
          {estado === "sin-token" ? "El mapa necesita una llave de Mapbox" : "No se pudo cargar el mapa"}
        </p>
        <p className="mt-2 leading-relaxed text-(--pb-texto-2)">
          {estado === "sin-token"
            ? "Agrega VITE_MAPBOX_TOKEN en el archivo .env y vuelve a iniciar la página. El resto de la vista sigue funcionando."
            : "Revisa la conexión a internet o la llave de Mapbox. El resto de la vista sigue funcionando."}
        </p>
      </div>
    </div>
  );
}
