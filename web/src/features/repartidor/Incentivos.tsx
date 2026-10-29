import { useEffect, useState } from "react";

import { api } from "../../lib/api";
import { Etiqueta, type TipoDato } from "../../lib/ui";
import "./incentivos.css";

export type Incentivo = {
  id: string;
  nombre: string;
  descripcion: string;
  rutas_requeridas: number;
  destacado: boolean;
  imagen?: string;
  patrocinador?: string;
  estado: "existe" | "propuesta";
  tipo_dato: TipoDato;
};

// Ejemplo de demostración (IDEA-v2.md §4.4). Las metas y el patrocinador reales están por validar.
const MOCK: Incentivo[] = [
  { id: "bici", nombre: "Una bicicleta para ti", descripcion: "Tuya al completar las rutas de la meta, para repartir sin gastar en gasolina.", rutas_requeridas: 5, destacado: true, patrocinador: "Por confirmar (programa de movilidad)", estado: "propuesta", tipo_dato: "simulado" },
  { id: "casco", nombre: "Casco", descripcion: "Para rodar más seguro.", rutas_requeridas: 1, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "luces", nombre: "Luces para bici", descripcion: "Delantera y trasera.", rutas_requeridas: 2, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "candado", nombre: "Candado", descripcion: "Para dejar tu bici tranquila.", rutas_requeridas: 3, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "mochila", nombre: "Mochila térmica", descripcion: "Mantiene la comida caliente.", rutas_requeridas: 4, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
  { id: "mantenimiento", nombre: "Mantenimiento de bici", descripcion: "Una revisión completa en un taller del barrio.", rutas_requeridas: 6, destacado: false, estado: "propuesta", tipo_dato: "simulado" },
];

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

const rutas = (n: number) => `${n} ${n === 1 ? "ruta" : "rutas"}`;

function Barra({ hechas, meta, chica }: { hechas: number; meta: number; chica?: boolean }) {
  const pct = Math.min(100, Math.round((hechas / Math.max(1, meta)) * 100));
  return (
    <div
      className={`inc-barra${chica ? " chica" : ""}`}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={meta}
      aria-valuenow={Math.min(hechas, meta)}
      aria-label={`Avance: ${Math.min(hechas, meta)} de ${meta} rutas`}
    >
      <span style={{ width: `${pct}%` }} />
    </div>
  );
}

/** Pestaña Incentivos: `completadas` viene del mismo estado que "Mis rutas". */
export function Incentivos({ completadas }: { completadas: number }) {
  const [lista, setLista] = useState<Incentivo[]>([]);
  const [mock, setMock] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let vivo = true;
    cargarIncentivos()
      .then((r) => {
        if (!vivo) return;
        setLista(r.lista);
        setMock(r.mock);
      })
      .catch(() => vivo && setError("No pudimos cargar los premios. Intenta de nuevo en un momento."));
    return () => {
      vivo = false;
    };
  }, []);

  if (error) return <p role="alert" className="text-lg font-medium">{error}</p>;
  if (lista.length === 0) return <p className="text-lg text-(--pb-texto-2)">Cargando premios…</p>;

  const bici = lista.find((i) => i.destacado) ?? lista[0];
  const otros = lista.filter((i) => i !== bici).sort((a, b) => a.rutas_requeridas - b.rutas_requeridas);
  const faltan = Math.max(0, bici.rutas_requeridas - completadas);

  return (
    <div className="flex flex-col gap-4">
      <article className="inc-destacado" aria-label={`Premio destacado: ${bici.nombre}`}>
        <div className="flex items-start gap-4">
          <span className="inc-icono" aria-hidden="true">🚲</span>
          <div className="min-w-0">
            <p className="text-(--pb-texto-2)">Premio destacado</p>
            <h3 className="text-2xl font-semibold leading-tight">{bici.nombre}</h3>
            <p className="mt-1 text-lg">{bici.descripcion}</p>
          </div>
        </div>
        <p className="mt-4 text-xl" aria-live="polite">
          {faltan === 0 ? (
            <strong>¡Lo lograste! Completaste las {rutas(bici.rutas_requeridas)} de la meta.</strong>
          ) : (
            <>
              Te {faltan === 1 ? "falta" : "faltan"} <strong>{rutas(faltan)}</strong> para tu bici.
            </>
          )}
        </p>
        <div className="mt-2">
          <Barra hechas={completadas} meta={bici.rutas_requeridas} />
        </div>
        <p className="mt-2 text-lg text-(--pb-texto-2)">
          {Math.min(completadas, bici.rutas_requeridas)} de {bici.rutas_requeridas} rutas completadas
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Etiqueta tipo="simulado" fuente="Meta y premio de ejemplo para la demostración" />
          {bici.estado === "propuesta" && <span className="font-semibold">Propuesta</span>}
          <span className="text-(--pb-texto-2)">
            Patrocinador: {bici.patrocinador ?? "por confirmar"} · Meta de {rutas(bici.rutas_requeridas)} por validar
          </span>
        </div>
      </article>

      <h3 className="text-xl font-semibold">Otros premios</h3>
      <ul className="inc-lista">
        {otros.map((i) => {
          const logrado = completadas >= i.rutas_requeridas;
          return (
            <li key={i.id} className={`inc-premio${logrado ? " inc-logrado" : ""}`}>
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <p className="text-lg font-semibold">{i.nombre}</p>
                  <p className="text-(--pb-texto-2)">{i.descripcion}</p>
                </div>
                <span className="text-lg font-semibold">{logrado ? "Conseguido" : `${rutas(i.rutas_requeridas)}`}</span>
              </div>
              <div className="mt-2">
                <Barra hechas={completadas} meta={i.rutas_requeridas} chica />
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <Etiqueta tipo={i.tipo_dato} fuente="Premio de ejemplo" />
                {i.estado === "propuesta" && <span className="font-medium">Propuesta</span>}
              </div>
            </li>
          );
        })}
      </ul>
      {mock && (
        <p role="status" className="text-(--pb-texto-2)">
          Premios de demostración: la API de incentivos aún no responde, por eso ves ejemplos.
        </p>
      )}
    </div>
  );
}
