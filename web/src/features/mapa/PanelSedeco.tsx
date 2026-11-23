import { useState, type ReactNode } from "react";
import { DIAS, NOMBRE_ALCALDIA, type Alcaldia, type PropsHex, type TipoDato } from "./datos";

// Panel SEDECO · Maqueta viva (web/DESIGN.md §6, recipe map + panel). Hero: the day and hour in words and the big
// figure of open tianguis. Only tokens; rosa is the single accent. No real/estimado/simulado chips on screen
// (uak decision CO-028): each figure keeps its source line, and tipo_dato stays in the data.

const DIA_LARGO = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"];

const cifra = (n: number | null | undefined, decimales = 0) =>
  n == null ? "Sin dato" : n.toLocaleString("es-MX", { maximumFractionDigits: decimales, minimumFractionDigits: decimales });

const CAJA = "rounded-(--pb-radio-tarjeta) bg-(--pb-superficie) p-4 shadow-(--pb-sombra)";

type PanelProps = {
  /** Selector y tarjeta de alcaldía (se muestra arriba del panel, no sobre el mapa). */
  alcaldiaNodo?: ReactNode;
  dia: number;
  onDia: (d: number) => void;
  hora: number;
  onHora: (h: number) => void;
  /** Muestra la comparación CNBV por alcaldía en lugar de la leyenda de impulso. */
  datoReal: boolean;
  onDatoReal: (v: boolean) => void;
  alcaldias: Alcaldia[];
  origenAlcaldias: "api" | "ejemplo";
  cobertura: { pct: number; tipo: TipoDato; fuente: string; periodo: string } | null;
  abiertos: number;
  altasHoy: number;
  altaReciente: boolean;
  origenHex: "api" | "ejemplo";
};

/** Panel derecho en escritorio. En teléfono es una hoja inferior fija sobre la barra de vistas: cerrada muestra el
 *  día, la hora y la cifra; el asa la abre para usar los controles. */
export function Panel(p: PanelProps) {
  const rampa = [1, 2, 3, 4, 5].map((n) => `var(--pb-impulso-${n})`).join(", ");
  const [abierta, setAbierta] = useState(false);
  return (
    <div
      className={`fixed inset-x-0 bottom-[calc(4rem+env(safe-area-inset-bottom))] z-20 flex flex-col gap-4 rounded-t-(--pb-radio-grande) bg-(--pb-fondo) p-4 pt-2 shadow-[0_-12px_30px_-14px_rgb(20_23_28/0.4)] motion-safe:transition-[max-height] motion-safe:duration-300 lg:static lg:h-full lg:max-h-none lg:overflow-y-auto lg:rounded-none lg:pt-4 lg:shadow-none ${
        abierta ? "max-h-[72dvh] overflow-y-auto" : "max-h-[11.5rem] overflow-hidden"
      }`}
    >
      <button
        type="button"
        aria-expanded={abierta}
        onClick={() => setAbierta((v) => !v)}
        className="-mx-4 -mt-2 flex min-h-(--pb-alto-control) shrink-0 flex-col items-center justify-center gap-1 lg:hidden"
      >
        <span aria-hidden="true" className="h-1.5 w-12 rounded-full bg-(--pb-borde-fuerte)" />
        <span className="text-sm font-medium text-(--pb-texto-2)">{abierta ? "Ver el mapa" : "Elegir día y hora"}</span>
      </button>

      <section aria-labelledby="titulo-panel" aria-live="polite" className="flex flex-col gap-1">
        <h2 id="titulo-panel" className="pb-display text-[1.75rem] font-extrabold leading-tight">
          El <span className="text-(--pb-acento)">{DIA_LARGO[p.dia]}</span> a las {String(p.hora).padStart(2, "0")}:00
        </h2>
        <p className="flex items-baseline gap-3">
          <span className="pb-display pb-cifra text-[3.6rem] font-extrabold leading-none">{p.abiertos.toLocaleString("es-MX")}</span>
          <span className="text-lg text-(--pb-texto-2)">{p.abiertos === 1 ? "tianguis abierto" : "tianguis abiertos"}</span>
        </p>
        {p.cobertura ? (
          <p className="text-lg">
            <span className="pb-cifra font-semibold">{cifra(p.cobertura.pct, 1)} %</span> de la gente vive a 800 m de uno
            <span className="block text-base text-(--pb-texto-2)">Fuente: {p.cobertura.fuente}</span>
          </p>
        ) : (
          <div role="status" aria-label="Calculando cobertura" className="h-12 rounded-(--pb-radio-control) bg-(--pb-superficie-2) motion-safe:animate-pulse" />
        )}
      </section>

      <section aria-label="Día y hora" className={`${CAJA} flex flex-col gap-3`}>
        <div role="group" aria-label="Día de la semana" className="grid grid-cols-7 gap-1">
          {DIAS.map((nombre, i) => (
            <button
              key={nombre}
              type="button"
              aria-pressed={p.dia === i}
              aria-label={DIA_LARGO[i]}
              onClick={() => p.onDia(i)}
              className={`min-h-(--pb-alto-control) rounded-full text-base font-semibold capitalize motion-safe:transition-colors ${
                p.dia === i ? "bg-(--pb-acento) text-(--pb-sobre-acento)" : "text-(--pb-texto) hover:bg-(--pb-superficie-2)"
              }`}
            >
              {nombre}
            </button>
          ))}
        </div>
        <label className="flex flex-col gap-1 text-base font-medium">
          <span className="flex justify-between">
            <span>Hora</span>
            <span className="pb-cifra">{String(p.hora).padStart(2, "0")}:00</span>
          </span>
          <input
            type="range"
            min={0}
            max={23}
            step={1}
            value={p.hora}
            onChange={(e) => p.onHora(Number(e.target.value))}
            className="h-(--pb-alto-control) w-full accent-(--pb-acento)"
          />
        </label>
      </section>

      <section aria-live="polite" className={`${CAJA} flex items-center justify-between`}>
        <div>
          <p className="text-base text-(--pb-texto-2)">Negocios dados de alta hoy</p>
          <p className="pb-display pb-cifra text-[2.4rem] font-extrabold leading-none">{p.altasHoy}</p>
        </div>
        <span className="relative flex size-4" aria-hidden="true">
          {p.altaReciente && <span className="absolute inset-0 rounded-full bg-(--pb-acento) opacity-70 motion-safe:animate-ping" />}
          <span className="relative size-4 rounded-full bg-(--pb-acento)" />
        </span>
      </section>

      {p.alcaldiaNodo}

      <div className={`${CAJA} flex items-center justify-between gap-3`}>
        <span id="etq-cnbv" className="text-lg font-semibold">
          Pagos con tarjeta por alcaldía
        </span>
        <button
          type="button"
          role="switch"
          aria-checked={p.datoReal}
          aria-labelledby="etq-cnbv"
          onClick={() => p.onDatoReal(!p.datoReal)}
          className={`relative h-8 w-14 shrink-0 rounded-full motion-safe:transition-colors ${p.datoReal ? "bg-(--pb-acento)" : "bg-(--pb-borde-fuerte)"}`}
        >
          <span
            className={`absolute top-1 size-6 rounded-full bg-(--pb-superficie) motion-safe:transition-all ${p.datoReal ? "left-7" : "left-1"}`}
          />
        </button>
      </div>

      {p.datoReal ? (
        <section aria-label="Pagos con tarjeta por alcaldía" className="flex flex-col gap-2">
          <p className="text-base text-(--pb-texto-2)">
            Transacciones con tarjeta por adulto, trimestre {p.alcaldias[0]?.trimestre ?? "2023-T2"}. Fuente: CNBV.
          </p>
          {p.alcaldias.map((a) => (
            <div key={a.cvegeo} className={CAJA}>
              <p className="text-lg font-semibold">{a.municipio}</p>
              <p className="pb-display pb-cifra text-[2rem] font-extrabold leading-tight">{cifra(a.tpv_por_adulto, 2)}</p>
              <p className="text-base text-(--pb-texto-2)">transacciones por adulto</p>
            </div>
          ))}
          {p.origenAlcaldias === "ejemplo" && <p className="text-base text-(--pb-texto-2)">Sin conexión: cifras de ejemplo.</p>}
        </section>
      ) : (
        <section aria-label="Qué significa el color" className={`${CAJA} text-base`}>
          <p className="font-semibold">Color: dónde falta comercio de barrio</p>
          <div aria-hidden="true" className="mt-2 h-3 rounded-full" style={{ background: `linear-gradient(to right, ${rampa})` }} />
          <div className="mt-1 flex justify-between text-(--pb-texto-2)">
            <span>poco</span>
            <span>mucho</span>
          </div>
          <p className="mt-2 flex items-center gap-2">
            <span className="inline-block size-4 rounded bg-(--pb-oculto)" aria-hidden="true" />
            Gris: menos de 3 negocios (sin cifras por privacidad)
          </p>
        </section>
      )}

      <p className="mt-auto text-base text-(--pb-texto-2)">
        {p.origenHex === "ejemplo" ? "Sin conexión: hexágonos de ejemplo. " : ""}
        Toca un hexágono para ver sus cifras y su fuente.
      </p>
    </div>
  );
}

/** Tarjeta del hexágono tocado (sobre el mapa). Oculto: sin cifras por privacidad. */
export function TarjetaHex({ p, onCerrar }: { p: PropsHex; onCerrar: () => void }) {
  const alcaldia = NOMBRE_ALCALDIA[p.alcaldia_cvegeo] ?? "CDMX";
  return (
    <section aria-label="Detalle del hexágono" className="w-full max-w-md rounded-(--pb-radio-tarjeta) bg-(--pb-superficie) p-5 shadow-(--pb-sombra-alta)">
      <header className="mb-3 flex items-start justify-between gap-3">
        <h2 className="text-xl font-semibold">Hexágono en {alcaldia}</h2>
        <button
          type="button"
          onClick={onCerrar}
          className="min-h-(--pb-alto-control) shrink-0 rounded-full px-4 text-base font-semibold hover:bg-(--pb-superficie-2)"
        >
          Cerrar
        </button>
      </header>

      {p.oculto ? (
        <p className="text-lg leading-relaxed">Menos de 3 negocios: sin cifras por privacidad.</p>
      ) : (
        <dl className="grid gap-3">
          <Fila etiqueta="Población" valor={cifra(p.poblacion)} fuente="Hexágonos del pipeline (data/processed/hex.geojson)" />
          <Fila
            etiqueta="Negocios de barrio"
            valor={`${cifra(p.negocios_barriales)} de ${cifra(p.negocios_total)}`}
            fuente="DENUE y Tianguis Abierto (pipeline)"
          />
          <Fila etiqueta="Actividad con tarjeta" valor={cifra(p.actividad_tpv_est, 2)} fuente="CNBV por alcaldía, repartido por negocios" />
          <Fila
            etiqueta="Falta de comercio"
            valor={p.impulso == null ? "Sin dato" : `${Math.round(p.impulso * 100)} de 100`}
            fuente="Índice de impulso del pipeline"
          />
          <Fila etiqueta="Periodo" valor={p.periodo_cnbv ?? "Sin periodo"} fuente="CNBV" />
        </dl>
      )}
    </section>
  );
}

function Fila({ etiqueta, valor, fuente }: { etiqueta: string; valor: string; fuente: string }) {
  return (
    <div className="border-b border-(--pb-borde) pb-3 last:border-0 last:pb-0">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3">
        <dt className="font-medium">{etiqueta}</dt>
        <dd className="pb-cifra text-lg font-semibold">{valor}</dd>
      </div>
      <p className="text-base text-(--pb-texto-2)">Fuente: {fuente}</p>
    </div>
  );
}
