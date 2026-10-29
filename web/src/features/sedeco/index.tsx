import { useEffect, useMemo, useState } from "react";
import type { FeatureProps } from "../../App";
import {
  cargarAltas,
  cargarAlcaldias,
  cargarHex,
  cargarResumen,
  cargarTianguis,
  calcularCobertura,
  DIAS,
  diaHoy,
  estaAbierto,
  type Alcaldia,
  type Alta,
  type CapaHex,
  type ColeccionHex,
  type Origen,
  type Resumen,
  type Tianguis,
} from "./datos";
import { MapaSedeco } from "./MapaSedeco";
import { Panel, TarjetaHex } from "./PanelSedeco";

const CAPAS: { id: CapaHex; texto: string }[] = [
  { id: "actividad", texto: "Actividad" },
  { id: "oferta", texto: "Oferta barrial" },
  { id: "poblacion", texto: "Población" },
  { id: "impulso", texto: "Impulso" },
];
const MAX_ALTAS = 100;

export default function Sedeco(_props: FeatureProps) {
  const [dia, setDia] = useState(diaHoy);
  const [hora, setHora] = useState(() => Math.min(23, Math.max(0, new Date().getHours())));
  const [capa, setCapa] = useState<CapaHex>("actividad");
  const [datoReal, setDatoReal] = useState(false);
  const [seleccion, setSeleccion] = useState<string | null>(null);

  const [hex, setHex] = useState<{ data: ColeccionHex; origen: Origen } | null>(null);
  const [tianguis, setTianguis] = useState<{ lista: Tianguis[]; origen: Origen }>({ lista: [], origen: "api" });
  const [alcaldias, setAlcaldias] = useState<{ lista: Alcaldia[]; origen: Origen }>({ lista: [], origen: "api" });
  const [resumen, setResumen] = useState<Resumen | null>(null);

  const [altas, setAltas] = useState<Alta[]>([]);
  const [altaReciente, setAltaReciente] = useState(false);

  useEffect(() => {
    let vivo = true;
    cargarHex().then((r) => vivo && setHex(r));
    cargarAlcaldias().then((r) => vivo && setAlcaldias(r));
    return () => {
      vivo = false;
    };
  }, []);

  useEffect(() => {
    let vivo = true;
    cargarTianguis(dia, hora).then((r) => vivo && setTianguis(r));
    cargarResumen(dia, hora).then((r) => vivo && setResumen(r));
    return () => {
      vivo = false;
    };
  }, [dia, hora]);

  // Altas en vivo: cada 3 s pregunta por lo nuevo. Si falla (404 incluido), no hace ruido.
  useEffect(() => {
    let desde = Math.floor(Date.now() / 1000);
    const vistas = new Set<string>();
    let ocupado = false;
    const sondear = async () => {
      if (ocupado) return;
      ocupado = true;
      const r = await cargarAltas(desde);
      ocupado = false;
      if (!r) return;
      desde = r.ts ?? desde;
      const nuevas = r.altas.filter((a) => !vistas.has(a.id));
      if (!nuevas.length) return;
      nuevas.forEach((a) => vistas.add(a.id));
      setAltas((prev) => [...nuevas, ...prev].slice(0, MAX_ALTAS));
      setAltaReciente(true);
      window.setTimeout(() => setAltaReciente(false), 5000);
    };
    const id = window.setInterval(sondear, 3000);
    return () => window.clearInterval(id);
  }, []);

  const abiertos = useMemo(() => tianguis.lista.filter((t) => estaAbierto(t, dia, hora)), [tianguis, dia, hora]);

  const cobertura = useMemo(() => {
    if (!hex) return null;
    const periodo = `${DIAS[dia]} ${String(hora).padStart(2, "0")}:00`;
    if (resumen?.poblacion_cubierta_pct) {
      const d = resumen.poblacion_cubierta_pct;
      return { pct: d.valor, tipo: d.tipo_dato, fuente: d.fuente, periodo: d.periodo };
    }
    return {
      pct: calcularCobertura(hex.data, abiertos),
      tipo: "estimado" as const,
      fuente: "Buffer de 800 m sobre tianguis abiertos (cálculo en el navegador)",
      periodo,
    };
  }, [hex, abiertos, resumen, dia, hora]);

  const propsSeleccion = useMemo(
    () => (seleccion && hex ? hex.data.features.find((f) => f.properties.h3 === seleccion)?.properties ?? null : null),
    [seleccion, hex],
  );

  const altasHoy = (resumen?.altas_hoy?.valor ?? 0) + altas.length;
  const hayEjemplo = hex?.origen === "ejemplo" || alcaldias.origen === "ejemplo" || tianguis.origen === "ejemplo";

  return (
    <div className="flex h-full flex-col lg:grid lg:grid-cols-[70fr_30fr]">
      <div className="relative h-[60vh] min-w-0 lg:h-full">
        <MapaSedeco
          hex={hex?.data ?? { type: "FeatureCollection", features: [] }}
          capa={capa}
          datoReal={datoReal}
          tianguis={abiertos}
          altas={altas}
          seleccionado={seleccion}
          onSeleccion={setSeleccion}
        />

        <div className="pointer-events-none absolute inset-x-0 top-3 flex flex-wrap items-start justify-between gap-2 px-3">
          <div role="group" aria-label="Capa del mapa" className="pointer-events-auto flex flex-wrap gap-1 rounded-2xl bg-white p-1.5 shadow-md">
            {CAPAS.map((c) => (
              <button
                key={c.id}
                type="button"
                aria-pressed={capa === c.id}
                onClick={() => setCapa(c.id)}
                disabled={datoReal}
                className={`rounded-xl px-3.5 py-2 text-base font-semibold disabled:opacity-40 ${
                  capa === c.id ? "bg-stone-900 text-white" : "text-stone-900 hover:bg-stone-100"
                }`}
              >
                {c.texto}
              </button>
            ))}
          </div>
          {hayEjemplo && (
            <span role="status" className="pointer-events-auto rounded-xl bg-amber-100 px-3 py-2 text-base font-bold text-amber-950 shadow-md">
              Datos de ejemplo
            </span>
          )}
        </div>

        {propsSeleccion && (
          <div className="absolute inset-x-3 bottom-3 flex justify-start">
            <TarjetaHex p={propsSeleccion} onCerrar={() => setSeleccion(null)} />
          </div>
        )}
      </div>

      <aside aria-label="Panel SEDECO" className="min-h-0 min-w-0 border-l border-stone-300 bg-stone-50 lg:h-full">
        <Panel
          dia={dia}
          onDia={setDia}
          hora={hora}
          onHora={setHora}
          datoReal={datoReal}
          onDatoReal={setDatoReal}
          alcaldias={alcaldias.lista}
          origenAlcaldias={alcaldias.origen}
          cobertura={cobertura}
          abiertos={abiertos.length}
          altasHoy={altasHoy}
          altaReciente={altaReciente}
          origenHex={hex?.origen ?? "api"}
        />
      </aside>
    </div>
  );
}

export const route = "sedeco";
export const label = "SEDECO";
export const order = 1;
