import { useEffect, useMemo, useState } from "react";
import type { FeatureProps } from "../../App";
import {
  cargarAltas,
  cargarAlcaldias,
  cargarHex,
  cargarRutas,
  conCapasDinamicas,
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
import type { RutasPorHexagono } from "./tiposCrecimiento";
import { CAPAS } from "../../lib/map/hex";
import { ChipsTipoMinimo } from "./ChipsAdaptador";
import { TarjetaAlcaldia } from "./TarjetaAlcaldia";
import { cargarAlcaldiasInfo, cargarPuntosProgresivo, type AlcaldiaInfo, type PuntoMapa, type TipoPunto } from "./puntos";
import { Leyenda } from "./Leyenda";
import { MapaHex } from "./MapaHex";
import { Panel, TarjetaHex } from "./PanelSedeco";

const MAX_ALTAS = 100;

export default function Mapa(_props: FeatureProps) {
  const [dia, setDia] = useState(diaHoy);
  const [hora, setHora] = useState(() => Math.min(23, Math.max(0, new Date().getHours())));
  const [capa, setCapa] = useState<CapaHex>("actividad");
  const [datoReal, setDatoReal] = useState(false);
  const [seleccion, setSeleccion] = useState<string | null>(null);

  const [hex, setHex] = useState<{ data: ColeccionHex; origen: Origen } | null>(null);
  const [tianguis, setTianguis] = useState<{ lista: Tianguis[]; origen: Origen }>({ lista: [], origen: "api" });
  const [alcaldias, setAlcaldias] = useState<{ lista: Alcaldia[]; origen: Origen }>({ lista: [], origen: "api" });
  const [rutas, setRutas] = useState<RutasPorHexagono | null>(null);
  const [resumen, setResumen] = useState<Resumen | null>(null);

  const [tipos, setTipos] = useState<TipoPunto[]>(["tianguis", "mercado"]);
  const [infoAlcaldias, setInfoAlcaldias] = useState<AlcaldiaInfo[]>([]);
  const [alcaldiaSel, setAlcaldiaSel] = useState("09003");
  const [puntos, setPuntos] = useState<PuntoMapa[]>([]);

  useEffect(() => {
    let vivo = true;
    cargarAlcaldiasInfo().then((r) => vivo && setInfoAlcaldias(r));
    return () => {
      vivo = false;
    };
  }, []);

  // Primero 09003 y 09007; el resto de alcaldías llega en segundo plano.
  useEffect(() => {
    if (!infoAlcaldias.length) return;
    let vivo = true;
    setPuntos([]);
    cargarPuntosProgresivo(tipos, infoAlcaldias.map((a) => a.cvegeo), (n) => setPuntos((prev) => [...prev, ...n]), () => vivo);
    return () => {
      vivo = false;
    };
  }, [tipos, infoAlcaldias]);

  const alternarTipo = (t: TipoPunto) => setTipos((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]));

  const [altas, setAltas] = useState<Alta[]>([]);
  const [altaReciente, setAltaReciente] = useState(false);

  useEffect(() => {
    let vivo = true;
    cargarHex().then((r) => vivo && setHex(r));
    cargarAlcaldias().then((r) => vivo && setAlcaldias(r));
    cargarRutas().then((r) => vivo && setRutas(r));
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

  const hexCapas = useMemo(
    () => (hex ? conCapasDinamicas(hex.data, altas, rutas) : { type: "FeatureCollection" as const, features: [] }),
    [hex, altas, rutas],
  );

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
      <div className="flex min-w-0 flex-col lg:relative lg:h-full">
       <div className="relative h-[60vh] lg:absolute lg:inset-0 lg:h-full">
        <MapaHex
          hex={hexCapas}
          capa={capa}
          datoReal={datoReal}
          tianguis={abiertos}
          puntos={puntos}
          altas={altas}
          seleccionado={seleccion}
          onSeleccion={setSeleccion}
        />

        <div className="pointer-events-none absolute bottom-3 right-3 z-10 flex max-w-[calc(100%-1.5rem)]">
          <div className="pointer-events-auto">
            <Leyenda capa={capa} tipoDato={capa === "rutas" ? rutas?.tipo_dato : undefined} />
          </div>
        </div>

        {propsSeleccion && (
          <div className="absolute inset-x-3 bottom-3 flex justify-start">
            <TarjetaHex p={propsSeleccion} onCerrar={() => setSeleccion(null)} />
          </div>
        )}
       </div>
        <div className="pointer-events-none order-first relative z-10 flex flex-col items-start gap-2 px-3 py-3 lg:absolute lg:inset-x-0 lg:top-0 lg:py-0 lg:pt-3">
         <div className="flex flex-wrap items-start justify-between gap-2 self-stretch">
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
          <ChipsTipoMinimo activos={tipos} onAlternar={alternarTipo} />
          {hayEjemplo && (
            <span role="status" className="pointer-events-auto rounded-xl bg-amber-100 px-3 py-2 text-base font-bold text-amber-950 shadow-md">
              Datos de ejemplo
            </span>
          )}
         </div>
          {infoAlcaldias.length > 0 && (
            <TarjetaAlcaldia alcaldias={infoAlcaldias} seleccion={alcaldiaSel} onSeleccion={setAlcaldiaSel} />
          )}
        </div>

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

export const route = "mapa";
export const label = "Mapa";
export const order = 1;
