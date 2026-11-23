import { useCallback, useEffect, useState, type FormEvent, type ReactNode } from "react";
import { Bicycle, MapPin, SignOut } from "@phosphor-icons/react";

import type { FeatureProps } from "../../App";
import { Boton, Tarjeta } from "../../lib/ui";
import { CodigoInvalido, completarOferta, enModoMock, iniciarSesion, listarOfertas, tomarOferta } from "./cliente";
import { Incentivos } from "./Incentivos";
import { MapaOfertas } from "./MapaOfertas";
import { ECOLOGICOS, type Oferta, type Sesion } from "./tipos";

export const route = "repartidor";
export const label = "Repartidor";
export const order = 4;

// Recipe "map + panel" (web/DESIGN.md §6). Hero: the map of offers with the first route highlighted in rosa.
// On phones the map sits on top and every action is a full-width 48 px button within thumb reach.
// No real/simulado chips on screen (uak decision CO-028).

const SONDEO_MS = 5000;
// Número del repartidor demo (app/services/repartidores.py), prellenado para la demo.
const DEMO_ID = import.meta.env.VITE_REPARTIDOR_DEMO_ID ?? "R-00001";
const dinero = (n: number) => `$${n.toFixed(0)}`;
const km = (m: number) => (m >= 1000 ? `${(m / 1000).toFixed(1)} km` : `${m} m`);

export default function Repartidor(_props: FeatureProps) {
  const [sesion, setSesion] = useState<Sesion | null>(null);
  if (!sesion) return <Acceso onEntrar={setSesion} />;
  return <Portal sesion={sesion} onSalir={() => setSesion(null)} />;
}

function Acceso({ onEntrar }: { onEntrar: (s: Sesion) => void }) {
  const [id, setId] = useState(DEMO_ID);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const idValido = /^R-\d{5}$/.test(id);

  async function entrar(e: FormEvent) {
    e.preventDefault();
    if (!idValido) return;
    setCargando(true);
    setError("");
    try {
      onEntrar(await iniciarSesion(id));
    } catch (err) {
      setError(err instanceof CodigoInvalido ? err.message : "No pudimos entrar. Intenta de nuevo.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-lg flex-col gap-6 px-4 py-10 md:py-16">
      <div className="flex items-center gap-4">
        <span className="grid size-16 shrink-0 place-items-center rounded-full bg-(--pb-acento-suave) text-(--pb-acento-fuerte)">
          <Bicycle size={34} weight="duotone" aria-hidden="true" />
        </span>
        <div>
          <h1 className="pb-display text-[2.3rem] font-extrabold">Repartidores de barrio</h1>
          <p className="text-lg text-(--pb-texto-2)">Rutas cortas en tu colonia, con premios.</p>
        </div>
      </div>
      <Tarjeta className="shadow-(--pb-sombra-alta)">
        <form onSubmit={entrar} className="flex flex-col gap-5">
          <div className="flex flex-col gap-2">
            <label htmlFor="numero-repartidor" className="text-lg font-medium">
              Número de repartidor
            </label>
            <input
              id="numero-repartidor"
              className="min-h-14 w-full rounded-(--pb-radio-control) border-2 border-(--pb-borde-fuerte) bg-(--pb-superficie) px-4 text-xl tracking-wide"
              value={id}
              onChange={(e) => setId(e.target.value.toUpperCase().trim())}
              placeholder="R-12345"
              autoComplete="off"
              inputMode="text"
              aria-invalid={id !== "" && !idValido}
              aria-describedby="ayuda-numero"
            />
            <p id="ayuda-numero" className="text-base text-(--pb-texto-2)">
              Es el número que te dio el bot de Telegram, por ejemplo R-12345.
            </p>
          </div>
          {error && (
            <p role="alert" className="text-lg font-medium text-(--pb-error)">
              {error}
            </p>
          )}
          <Boton type="submit" tamano="lg" anchoCompleto disabled={!idValido || cargando}>
            {cargando ? "Entrando…" : "Entrar"}
          </Boton>
        </form>
      </Tarjeta>
    </div>
  );
}

type PestanaId = "ofertas" | "mias" | "incentivos";

function Portal({ sesion, onSalir }: { sesion: Sesion; onSalir: () => void }) {
  const [ofertas, setOfertas] = useState<Oferta[]>([]);
  const [cargado, setCargado] = useState(false);
  const [elegida, setElegida] = useState<string | null>(null);
  const [pestana, setPestana] = useState<PestanaId>("ofertas");
  const [error, setError] = useState("");
  const [ocupada, setOcupada] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      setOfertas(await listarOfertas(sesion));
      setError("");
    } catch {
      setError("No pudimos actualizar las ofertas. Lo intentamos de nuevo en 5 segundos.");
    } finally {
      setCargado(true);
    }
  }, [sesion]);

  useEffect(() => {
    const primera = setTimeout(cargar, 0);
    const t = setInterval(cargar, SONDEO_MS);
    return () => {
      clearTimeout(primera);
      clearInterval(t);
    };
  }, [cargar]);

  async function accion(o: Oferta, que: "tomar" | "completar") {
    setOcupada(o.id);
    try {
      await (que === "tomar" ? tomarOferta(sesion, o.id) : completarOferta(sesion, o.id));
      await cargar();
      if (que === "tomar") setPestana("mias");
    } catch {
      setError(que === "tomar" ? "No se pudo tomar la ruta; quizá ya la tomó alguien más." : "No se pudo marcar como completada.");
    } finally {
      setOcupada(null);
    }
  }

  const abiertas = ofertas.filter((o) => o.estado === "abierta");
  const mias = ofertas.filter((o) => o.repartidor_id === sesion.repartidor_id && o.estado !== "cancelada");
  const completadas = mias.filter((o) => o.estado === "completada").length;
  const noEcologico = sesion.transporte && !ECOLOGICOS.includes(sesion.transporte);
  const visibles = pestana === "ofertas" ? abiertas : pestana === "mias" ? mias : [];
  // Hero: with nothing chosen yet, the first route of the list is the highlighted one.
  const resaltada = visibles.some((o) => o.id === elegida) ? elegida : (visibles[0]?.id ?? null);

  return (
    <div className="grid min-h-full lg:h-full lg:grid-cols-[minmax(0,1fr)_440px]">
      <div className="relative h-[42vh] min-h-72 lg:h-full">
        <MapaOfertas ofertas={visibles} elegida={resaltada} onElegir={(id) => setElegida(id)} />
      </div>

      <section aria-label="Tus rutas" className="flex min-h-0 flex-col gap-4 bg-(--pb-fondo) p-4 md:p-6 lg:overflow-y-auto">
        <header className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h1 className="pb-display text-[1.9rem] font-extrabold leading-tight">
              Hola{sesion.nombre_mostrar ? `, ${sesion.nombre_mostrar}` : ""}
            </h1>
            <p className="text-lg text-(--pb-texto-2)">{sesion.repartidor_id}</p>
          </div>
          <Boton variante="fantasma" icono={<SignOut />} onClick={onSalir}>
            Salir
          </Boton>
        </header>

        {enModoMock() && (
          <p role="status" className="rounded-(--pb-radio-control) bg-(--pb-superficie-2) px-4 py-3 text-lg text-(--pb-texto-2)">
            Sin conexión con el servidor: te mostramos ofertas de ejemplo.
          </p>
        )}
        {noEcologico && (
          <p role="note" className="rounded-(--pb-radio-control) bg-(--pb-acento-suave) px-4 py-3 text-lg">
            Con bici, bici eléctrica o a pie te tocan rutas más cortas y te acercas al premio de la bici.
          </p>
        )}
        {error && (
          <p role="alert" className="text-lg font-medium text-(--pb-error)">
            {error}
          </p>
        )}

        <div role="tablist" aria-label="Qué quieres ver" className="grid grid-cols-3 gap-1 rounded-full bg-(--pb-superficie-2) p-1">
          <Pestana activa={pestana === "ofertas"} onClick={() => setPestana("ofertas")} cuenta={abiertas.length}>
            Ofertas
          </Pestana>
          <Pestana activa={pestana === "mias"} onClick={() => setPestana("mias")} cuenta={mias.length}>
            Mis rutas
          </Pestana>
          <Pestana activa={pestana === "incentivos"} onClick={() => setPestana("incentivos")}>
            Premios
          </Pestana>
        </div>

        {pestana === "mias" && (
          <p className="text-lg" aria-live="polite">
            Llevas <strong className="pb-cifra">{completadas}</strong> {completadas === 1 ? "ruta completada" : "rutas completadas"} de{" "}
            {mias.length}.
          </p>
        )}
        {pestana === "incentivos" && <Incentivos completadas={completadas} />}
        {pestana !== "incentivos" && !cargado && (
          <div role="status" aria-label="Cargando ofertas" className="flex flex-col gap-3">
            {[0, 1].map((i) => (
              <div key={i} className="h-40 rounded-(--pb-radio-tarjeta) bg-(--pb-superficie-2) motion-safe:animate-pulse" />
            ))}
          </div>
        )}
        {pestana !== "incentivos" && cargado && visibles.length === 0 && (
          <p className="rounded-(--pb-radio-tarjeta) bg-(--pb-superficie) p-5 text-lg text-(--pb-texto-2)">
            {pestana === "ofertas"
              ? "No hay ofertas abiertas ahora. Esta pantalla se actualiza sola cada 5 segundos."
              : "Todavía no tomas ninguna ruta."}
          </p>
        )}
        {pestana !== "incentivos" && (
          <ul className="flex flex-col gap-3">
            {visibles.map((o) => (
              <TarjetaOferta
                key={o.id}
                o={o}
                elegida={o.id === resaltada}
                ocupada={ocupada === o.id}
                onElegir={() => setElegida(o.id)}
                onAccion={(q) => accion(o, q)}
              />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function Pestana({ activa, onClick, cuenta, children }: { activa: boolean; onClick: () => void; cuenta?: number; children: ReactNode }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={activa}
      onClick={onClick}
      className={`flex min-h-(--pb-alto-control) items-center justify-center gap-1.5 whitespace-nowrap rounded-full px-2 text-base font-semibold motion-safe:transition-colors ${
        activa ? "bg-(--pb-superficie) text-(--pb-acento-fuerte) shadow-(--pb-sombra)" : "text-(--pb-texto-2) hover:text-(--pb-texto)"
      }`}
    >
      {children}
      {typeof cuenta === "number" && <span className="pb-cifra text-(--pb-texto-2)">{cuenta}</span>}
    </button>
  );
}

const ESTADOS = { abierta: "Abierta", tomada: "En curso", completada: "Completada", cancelada: "Cancelada" };

function TarjetaOferta({
  o,
  elegida,
  ocupada,
  onElegir,
  onAccion,
}: {
  o: Oferta;
  elegida: boolean;
  ocupada: boolean;
  onElegir: () => void;
  onAccion: (q: "tomar" | "completar") => void;
}) {
  return (
    <li
      className={`rounded-(--pb-radio-tarjeta) bg-(--pb-superficie) p-5 ${
        elegida ? "shadow-(--pb-sombra-alta) ring-2 ring-(--pb-acento)" : "shadow-(--pb-sombra)"
      }`}
    >
      <button type="button" onClick={onElegir} aria-pressed={elegida} className="block w-full rounded-(--pb-radio-control) text-left">
        <span className="flex items-start justify-between gap-3">
          <span className="min-w-0">
            <span className="block text-xl font-semibold leading-tight">{o.negocio_nombre ?? "Negocio de barrio"}</span>
            <span className="mt-1 flex items-center gap-1 text-lg text-(--pb-texto-2)">
              <MapPin size={18} aria-hidden="true" />
              Sale de {o.colonia}
            </span>
          </span>
          <span className="shrink-0 text-right">
            <span className="pb-display pb-cifra block text-[1.9rem] font-extrabold leading-none">{dinero(o.pago_est)}</span>
            <span className="text-base text-(--pb-texto-2)">pago aprox.</span>
          </span>
        </span>
        <span className="mt-3 block text-lg">
          {o.paradas.length} {o.paradas.length === 1 ? "parada" : "paradas"} · {km(o.distancia_m)} · {o.minutos_est} min
          {o.estado !== "abierta" && <span className="ml-2 font-semibold text-(--pb-acento-fuerte)">{ESTADOS[o.estado]}</span>}
        </span>
      </button>
      {o.estado === "abierta" && (
        <Boton className="mt-4" tamano="lg" anchoCompleto disabled={ocupada} onClick={() => onAccion("tomar")}>
          {ocupada ? "Tomando…" : "Tomar ruta"}
        </Boton>
      )}
      {o.estado === "tomada" && (
        <Boton className="mt-4" variante="secundario" tamano="lg" anchoCompleto disabled={ocupada} onClick={() => onAccion("completar")}>
          {ocupada ? "Guardando…" : "Marcar como completada"}
        </Boton>
      )}
    </li>
  );
}
