import { useEffect, useState, type ComponentType } from "react";
import { AppShell } from "./lib/ui";

// Each view is web/src/features/<name>/index.tsx exporting `default`, `route`, `label` and `order`.
// Adding a view = creating its folder; App.tsx never becomes a conflict point.
// Hash routes, no login: #/inicio (also #/), #/mapa (#/sedeco redirige), #/usuario, #/negocio/:id, #/repartidor.
// The component receives the segments after its route. Every view renders inside AppShell (web/DESIGN.md §5).
export type FeatureProps = { params: string[] };

type FeatureModule = {
  default: ComponentType<FeatureProps>;
  route?: string;
  label?: string;
  order?: number;
};

const features = Object.entries(
  import.meta.glob<FeatureModule>("./features/*/index.tsx", { eager: true }),
)
  .map(([path, module]) => ({
    path,
    Component: module.default,
    route: module.route ?? path.split("/")[2],
    label: module.label ?? module.route ?? path.split("/")[2],
    order: module.order ?? 100,
  }))
  .sort((a, b) => a.order - b.order);

const items = features.map((f) => ({ route: f.route, label: f.label }));

function readHash(): string[] {
  return window.location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
}

export default function App() {
  const [segments, setSegments] = useState(readHash);

  useEffect(() => {
    const onHash = () => setSegments(readHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  // Rutas retiradas: #/sedeco pasó a #/mapa y #/crecimiento ya no es vista (sus datos son capas del mapa).
  useEffect(() => {
    if (segments[0] === "sedeco" || segments[0] === "crecimiento") window.location.replace("#/mapa");
  }, [segments]);

  // No hash (or an unknown one) opens the landing: the first thing a visitor sees is Inicio.
  const current =
    features.find((f) => f.route === segments[0]) ??
    (segments[0] === "sedeco" || segments[0] === "crecimiento" ? features.find((f) => f.route === "mapa") : undefined) ??
    features.find((f) => f.route === "inicio") ??
    features[0];

  return (
    <AppShell items={items} actual={current?.route}>
      {current ? (
        <current.Component params={current.route === segments[0] ? segments.slice(1) : []} />
      ) : (
        <p className="p-8 text-lg text-(--pb-texto-2)">Cargando vistas…</p>
      )}
    </AppShell>
  );
}
