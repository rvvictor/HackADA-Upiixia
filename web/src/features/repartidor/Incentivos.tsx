import { useEffect, useState } from "react";
import { Backpack, Bicycle, CheckCircle, Gift, HardHat, Lightbulb, Lock, Wrench, type Icon } from "@phosphor-icons/react";

import { api } from "../../lib/api";
import type { TipoDato } from "../../lib/ui";
import "./incentivos.css";

export type Incentivo = {
  id: string;
  nombre: string;
  descripcion: string;
  rutas_requeridas: number;
  destacado: boolean;
  imagen?: string | null;
  patrocinador?: string | null;
  estado: "existe" | "propuesta";
  tipo_dato: TipoDato;
};

// Recipe "list" (web/DESIGN.md §6): the bike as one big card on top, the rest as quiet rows.
// No real/simulado chips on screen (uak decision CO-028); the API still sends tipo_dato.

// Ejemplo de demostración (IDEA-v2.md §4.4), solo si la API de incentivos no responde.
const MOCK: Incentivo[] = [
  { id: "bici", nombre: "Una bicicleta para ti", descripcion: "Tuya al completar las rutas de la meta, para repartir sin gastar en gasolina.", rutas_requeridas: 5, destacado: true, patrocinador: null, estado: "propuesta", tipo_dato: "simulado" },
  { id: "casco", nombre: "Casco", descripcion: "Para rodar más seguro.", rutas_requeridas: 1, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "luces", nombre: "Luces para bici", descripcion: "Delantera y trasera.", rutas_requeridas: 2, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "candado", nombre: "Candado", descripcion: "Para dejar tu bici tranquila.", rutas_requeridas: 3, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "mochila", nombre: "Mochila térmica", descripcion: "Mantiene la comida caliente.", rutas_requeridas: 4, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "mantenimiento", nombre: "Mantenimiento de bici", descripcion: "Una revisión completa en un taller del barrio.", rutas_requeridas: 6, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
];

const ICONOS: Record<string, Icon> = {
  bici: Bicycle,
  casco: HardHat,
  luces: Lightbulb,
  candado: Lock,
  mochila: Backpack,
  mantenimiento: Wrench,
};

function sinApi(e: unknown): boolean {
  if (e instanceof TypeError || e instanceof SyntaxError) return true;
  return e instanceof Error && /^(404|405|500|502|503|504)\b/.test(e.message);
}

async function cargarIncentivos(): Promise<{ lista: Incentivo[]; mock: boolean }> {
  try {
    const r = await api<Incentivo[] | { incentivos: Incentivo[] }>("/incentivos");
    const lista = Array.isArray(r) ? r : r.incentivos;
    if (!Array.isArray(lista) || lista.length === 0) throw new SyntaxError("vacío");
    return { lista, mock: false };
  } catch (e) {
    if (!sinApi(e)) throw e;
    return { lista: MOCK, mock: true };
  }
}

const rutas = (n: number) => `${n.toLocaleString("es-MX")} ${n === 1 ? "ruta" : "rutas"}`;

/** Progress bar that fills from 0 when it appears (CSS transition); instant under prefers-reduced-motion. */
function Barra({ hechas, meta, chica }: { hechas: number; meta: number; chica?: boolean }) {
  const pct = Math.min(100, Math.round((hechas / Math.max(1, meta)) * 100));
  const [lleno, setLleno] = useState(0);
  useEffect(() => {
    const id = requestAnimationFrame(() => setLleno(pct));
    return () => cancelAnimationFrame(id);
  }, [pct]);
  return (
    <div
      className={`inc-barra${chica ? " chica" : ""}`}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={meta}
      aria-valuenow={Math.min(hechas, meta)}
      aria-label={`Avance: ${Math.min(hechas, meta)} de ${meta} rutas`}
    >
      <span style={{ width: `${lleno}%` }} />
    </div>
  );
}

/** Pestaña Incentivos: `completadas` viene del mismo estado que "Mis rutas". */
export function Incentivos({ completadas }: { completadas: number }) {
  const [lista, setLista] = useState<Incentivo[]>([]);
  const [mock, setMock] = useState(false);
  const [error, setError] = useState("");
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vivo = true;
    cargarIncentivos()
      .then((r) => {
        if (!vivo) return;
        setLista(r.lista);
        setMock(r.mock);
        setError("");
      })
      .catch(() => vivo && setError("No pudimos cargar los premios."));
    return () => {
      vivo = false;
    };
  }, [intento]);

  if (error)
    return (
      <div role="alert" className="flex flex-col items-start gap-3 rounded-(--pb-radio-tarjeta) bg-(--pb-superficie) p-5">
        <p className="text-lg font-semibold">{error}</p>
        <button
          type="button"
          onClick={() => setIntento((n) => n + 1)}
          className="min-h-(--pb-alto-control) rounded-full border-2 border-(--pb-borde-fuerte) px-5 text-lg font-semibold"
        >
          Intentar otra vez
        </button>
      </div>
    );
  if (lista.length === 0)
    return (
      <div role="status" aria-label="Cargando premios" className="flex flex-col gap-3">
        <div className="h-56 rounded-(--pb-radio-tarjeta) bg-(--pb-superficie-2) motion-safe:animate-pulse" />
        <div className="h-20 rounded-(--pb-radio-tarjeta) bg-(--pb-superficie-2) motion-safe:animate-pulse" />
      </div>
    );

  const bici = lista.find((i) => i.destacado) ?? lista[0];
  const otros = lista.filter((i) => i !== bici).sort((a, b) => a.rutas_requeridas - b.rutas_requeridas);
  const faltan = Math.max(0, bici.rutas_requeridas - completadas);
  const IconoBici = ICONOS[bici.id] ?? Gift;

  return (
    <div className="flex flex-col gap-5">
      <article className="inc-destacado" aria-label={`Premio destacado: ${bici.nombre}`}>
        <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
          <span className="inc-icono" aria-hidden="true">
            <IconoBici size={56} weight="duotone" />
          </span>
          <div className="min-w-0">
            <h3 className="text-[1.45rem] font-semibold leading-tight">{bici.nombre}</h3>
            <p className="mt-1 text-lg text-(--pb-texto-2)">{bici.descripcion}</p>
          </div>
        </div>

        <p className="mt-6" aria-live="polite">
          {faltan === 0 ? (
            <span className="pb-display text-[2.2rem] font-extrabold leading-none">¡Lo lograste!</span>
          ) : (
            <>
              <span className="block text-lg">Te {faltan === 1 ? "falta" : "faltan"}</span>
              <span className="pb-display pb-cifra text-[3.4rem] font-extrabold leading-none text-(--pb-acento-fuerte)">
                {faltan.toLocaleString("es-MX")}
              </span>{" "}
              <span className="text-xl font-semibold">{faltan === 1 ? "ruta" : "rutas"} para tu bici</span>
            </>
          )}
        </p>
        <div className="mt-4">
          <Barra hechas={completadas} meta={bici.rutas_requeridas} />
        </div>
        <p className="mt-2 text-lg text-(--pb-texto-2)">
          <span className="pb-cifra font-semibold text-(--pb-texto)">{Math.min(completadas, bici.rutas_requeridas)}</span> de{" "}
          {rutas(bici.rutas_requeridas)} completadas
        </p>
        {(bici.estado === "propuesta" || !bici.patrocinador) && (
          <p className="mt-3 text-base text-(--pb-texto-2)">
            Patrocinador: {bici.patrocinador ?? "por confirmar"}. La meta puede cambiar.
          </p>
        )}
      </article>

      <section aria-labelledby="otros-premios">
        <h3 id="otros-premios" className="mb-2 text-xl font-semibold">
          En el camino
        </h3>
        <ul className="inc-lista">
          {otros.map((i) => {
            const logrado = completadas >= i.rutas_requeridas;
            const Icono = logrado ? CheckCircle : (ICONOS[i.id] ?? Gift);
            return (
              <li key={i.id} className={`inc-premio${logrado ? " inc-logrado" : ""}`}>
                <span className="inc-premio-icono" aria-hidden="true">
                  <Icono size={26} weight={logrado ? "fill" : "regular"} />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <p className="text-lg font-semibold">{i.nombre}</p>
                    <span className="text-base font-semibold text-(--pb-texto-2)">
                      {logrado ? "Conseguido" : rutas(i.rutas_requeridas)}
                    </span>
                  </div>
                  <p className="text-base text-(--pb-texto-2)">{i.descripcion}</p>
                  {!logrado && (
                    <div className="mt-2">
                      <Barra hechas={completadas} meta={i.rutas_requeridas} chica />
                    </div>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      </section>
      {mock && (
        <p role="status" className="text-base text-(--pb-texto-2)">
          Sin conexión con el servidor: te mostramos premios de ejemplo.
        </p>
      )}
    </div>
  );
}
