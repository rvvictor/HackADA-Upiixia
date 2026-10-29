import { useEffect, useState, type ComponentType } from "react";

// Each view is web/src/features/<name>/index.tsx exporting `default`, `route`, `label` and `order`.
// Adding a view = creating its folder; App.tsx never becomes a conflict point.
// Hash routes, no login: #/sedeco, #/usuario, #/negocio/:id. The component receives the segments after its route.
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

  const current =
    features.find((f) => f.route === segments[0]) ??
    features.find((f) => f.route === "sedeco") ??
    features[0];

  return (
    <div className="flex h-[100dvh] flex-col font-sans">
      <header className="flex shrink-0 items-center gap-6 border-b border-stone-300 bg-white px-5 py-3">
        <a href="#/sedeco" className="text-xl font-semibold tracking-tight text-stone-900">
          Pulso Barrial
        </a>
        <nav aria-label="Elegir vista" className="flex gap-2">
          {features.map((f) => {
            const active = f === current;
            return (
              <a
                key={f.path}
                href={`#/${f.route}`}
                aria-current={active ? "page" : undefined}
                className={`rounded-lg px-4 py-2 text-base font-medium ${
                  active ? "bg-stone-900 text-white" : "text-stone-700 hover:bg-stone-100"
                }`}
              >
                {f.label}
              </a>
            );
          })}
        </nav>
        <span className="ml-auto text-sm text-stone-500">La red viva de la economía de barrio</span>
      </header>
      <main className="min-h-0 flex-1">
        {current ? (
          <current.Component params={current.route === segments[0] ? segments.slice(1) : []} />
        ) : (
          <p className="p-8 text-lg text-stone-600">Cargando vistas…</p>
        )}
      </main>
    </div>
  );
}
