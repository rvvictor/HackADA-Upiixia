import { useCallback, useEffect, useState, type FormEvent } from "react";

import type { FeatureProps } from "../../App";
import { Boton, Etiqueta, Tarjeta } from "../../lib/ui";
import { CodigoInvalido, completarOferta, enModoMock, iniciarSesion, listarOfertas, tomarOferta } from "./cliente";
import { Incentivos } from "./Incentivos";
import { MapaOfertas } from "./MapaOfertas";
import { ECOLOGICOS, type Oferta, type Sesion } from "./tipos";

export const route = "repartidor";
export const label = "Repartidor";
export const order = 4;

const SONDEO_MS = 5000;
const dinero = (n: number) => `$${n.toFixed(0)} MXN`;
const km = (m: number) => (m >= 1000 ? `${(m / 1000).toFixed(1)} km` : `${m} m`);

export default function Repartidor(_props: FeatureProps) {
  const [sesion, setSesion] = useState<Sesion | null>(null);
  if (!sesion) return <Acceso onEntrar={setSesion} />;
  return <Portal sesion={sesion} onSalir={() => setSesion(null)} />;
}

function Acceso({ onEntrar }: { onEntrar: (s: Sesion) => void }) {
  const [id, setId] = useState("");
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

  const campo =
    "mt-2 block w-full min-h-14 rounded-(--pb-radio-tarjeta) border border-(--pb-borde-fuerte) bg-(--pb-superficie) px-4 text-xl text-(--pb-texto)";

  return (
    <main className="mx-auto w-full max-w-lg px-4 py-10">
      <Tarjeta antetitulo="Repartidores de barrio" titulo="Entra a tu portal">
        <form onSubmit={entrar} className="space-y-5">
          <label className="block text-lg font-medium">
            Número de repartidor
            <input
              className={campo}
              value={id}
              onChange={(e) => setId(e.target.value.toUpperCase().trim())}
              placeholder="R-12345"
              autoComplete="off"
              inputMode="text"
              aria-invalid={id !== "" && !idValido}
            />
          </label>
          {error && (
            <p role="alert" className="font-medium text-(--pb-error,var(--pb-texto))">
              {error}
            </p>
          )}
          <Boton type="submit" tamano="lg" anchoCompleto disabled={!idValido || cargando}>
            {cargando ? "Entrando…" : "Entrar"}
          </Boton>
        </form>
        <p className="mt-5 text-(--pb-texto-2)">Escribe tu número de repartidor (R-12345) para ver tus rutas.</p>
      </Tarjeta>
    </main>
  );
}

function Portal({ sesion, onSalir }: { sesion: Sesion; onSalir: () => void }) {
  const [ofertas, setOfertas] = useState<Oferta[]>([]);
  const [elegida, setElegida] = useState<string | null>(null);
  const [pestana, setPestana] = useState<"ofertas" | "mias" | "incentivos">("ofertas");
  const [error, setError] = useState("");
  const [ocupada, setOcupada] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      setOfertas(await listarOfertas(sesion));
      setError("");
    } catch {
      setError("No pudimos actualizar las ofertas. Lo intentamos de nuevo en 5 segundos.");
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
  const demo = enModoMock() || sesion.demo_data || ofertas.some((o) => o.demo_data);
  const visibles = pestana === "ofertas" ? abiertas : pestana === "mias" ? mias : [];

  return (
    <main className="mx-auto w-full max-w-[1400px] px-4 py-6">
      <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-[1.777rem] font-semibold leading-tight tracking-tight">Portal de repartidores</h1>
          <p className="text-(--pb-texto-2)">
            {sesion.nombre_mostrar ? `${sesion.nombre_mostrar} · ` : ""}
            {sesion.repartidor_id}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {demo && <Etiqueta tipo="simulado" fuente="demo_data: true" />}
          <Boton variante="secundario" onClick={onSalir}>
            Salir
          </Boton>
        </div>
      </header>

      {enModoMock() && (
        <p role="status" className="mb-3 text-(--pb-texto-2)">
          Datos de demostración (demo_data: true): la API de repartidores aún no responde, por eso ves ejemplos.
        </p>
      )}
      {noEcologico && (
        <p role="note" className="mb-3 rounded-(--pb-radio-tarjeta) border border-(--pb-borde) bg-(--pb-superficie-2) p-4 text-lg">
          Tip: con bici, bici eléctrica o a pie ganas rutas de barrio más cortas y te acercas al premio de la bici. Tu transporte
          actual no es ecológico; puedes cambiarlo cuando quieras.
        </p>
      )}
      {error && (
        <p role="alert" className="mb-3 font-medium">
          {error}
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-[60%_1fr]">
        <div className="h-[60vh] min-h-96 lg:h-[calc(100vh-14rem)]">
          <MapaOfertas
            ofertas={visibles}
            elegida={elegida}
            onElegir={(id) => setElegida(id)}
          />
        </div>

        <section aria-label="Ofertas y rutas" className="flex min-h-0 flex-col gap-3 lg:max-h-[calc(100vh-14rem)] lg:overflow-y-auto">
          <div role="tablist" className="flex gap-2">
            <Pestana activa={pestana === "ofertas"} onClick={() => setPestana("ofertas")}>
              Ofertas ({abiertas.length})
            </Pestana>
            <Pestana activa={pestana === "mias"} onClick={() => setPestana("mias")}>
              Mis rutas ({mias.length})
            </Pestana>
            <Pestana activa={pestana === "incentivos"} onClick={() => setPestana("incentivos")}>
              Incentivos
            </Pestana>
          </div>
          {pestana === "mias" && (
            <p className="text-lg" aria-live="polite">
              Llevas <strong>{completadas}</strong> {completadas === 1 ? "ruta completada" : "rutas completadas"} de {mias.length}.
            </p>
          )}
          {pestana === "incentivos" && <Incentivos completadas={completadas} />}
          {pestana !== "incentivos" && visibles.length === 0 && (
            <p className="rounded-(--pb-radio-tarjeta) border border-(--pb-borde) bg-(--pb-superficie) p-5 text-lg text-(--pb-texto-2)">
              {pestana === "ofertas"
                ? "No hay ofertas abiertas ahora. Esta pantalla se actualiza sola cada 5 segundos."
                : "Todavía no tomas ninguna ruta."}
            </p>
          )}
          {visibles.map((o) => (
            <TarjetaOferta
              key={o.id}
              o={o}
              elegida={o.id === elegida}
              ocupada={ocupada === o.id}
              onElegir={() => setElegida(o.id)}
              onAccion={(q) => accion(o, q)}
            />
          ))}
        </section>
      </div>
    </main>
  );
}

function Pestana({ activa, onClick, children }: { activa: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      role="tab"
      aria-selected={activa}
      onClick={onClick}
      className={`min-h-12 flex-1 rounded-(--pb-radio-tarjeta) border px-4 text-lg font-semibold ${
        activa
          ? "border-transparent bg-(--pb-acento) text-white"
          : "border-(--pb-borde) bg-(--pb-superficie) text-(--pb-texto) hover:border-(--pb-borde-fuerte)"
      }`}
    >
      {children}
    </button>
  );
}

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
  const estados = { abierta: "Abierta", tomada: "En curso", completada: "Completada", cancelada: "Cancelada" };
  return (
    <article
      onClick={onElegir}
      className={`cursor-pointer rounded-(--pb-radio-tarjeta) border bg-(--pb-superficie) p-5 shadow-(--pb-sombra) ${
        elegida ? "border-(--pb-acento) border-2" : "border-(--pb-borde)"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="text-xl font-semibold leading-tight">{o.negocio_nombre ?? "Negocio de barrio"}</h3>
          <p className="text-(--pb-texto-2)">Sale de {o.colonia}</p>
        </div>
        {o.estado !== "abierta" && <span className="font-semibold">{estados[o.estado]}</span>}
      </div>
      <p className="mt-2 text-lg">
        {o.paradas.length} {o.paradas.length === 1 ? "parada" : "paradas"} · {km(o.distancia_m)} · {o.minutos_est} min
      </p>
      <p className="mt-1 flex flex-wrap items-center gap-2 text-lg">
        Pago estimado: <strong>{dinero(o.pago_est)}</strong>
        <Etiqueta tipo={o.tipo_dato_pago} />
      </p>
      {o.estado === "abierta" && (
        <Boton
          className="mt-4"
          tamano="lg"
          anchoCompleto
          disabled={ocupada}
          onClick={(e) => {
            e.stopPropagation();
            onAccion("tomar");
          }}
        >
          {ocupada ? "Tomando…" : "Tomar ruta"}
        </Boton>
      )}
      {o.estado === "tomada" && (
        <Boton
          className="mt-4"
          variante="secundario"
          tamano="lg"
          anchoCompleto
          disabled={ocupada}
          onClick={(e) => {
            e.stopPropagation();
            onAccion("completar");
          }}
        >
          {ocupada ? "Guardando…" : "Marcar como completada"}
        </Boton>
      )}
    </article>
  );
}
