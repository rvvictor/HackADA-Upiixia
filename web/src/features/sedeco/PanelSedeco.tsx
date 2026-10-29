import { DIAS, ETIQUETA_TIPO, NOMBRE_ALCALDIA, type Alcaldia, type PropsHex, type TipoDato } from "./datos";

// Etiqueta del tipo de dato (real / estimado / simulado): color y forma distintos, no solo color.
const ESTILO: Record<TipoDato, string> = {
  real: "bg-emerald-100 text-emerald-900 border-emerald-700",
  estimado: "bg-blue-100 text-blue-950 border-blue-800",
  simulado: "bg-stone-200 text-stone-900 border-dashed border-stone-700",
};
const PUNTO: Record<TipoDato, string> = {
  real: "bg-emerald-800",
  estimado: "border-2 border-blue-800",
  simulado: "border-2 border-dashed border-stone-700",
};

export function Etiqueta({ tipo, fuente }: { tipo: TipoDato; fuente?: string }) {
  return (
    <span
      title={fuente ? `${ETIQUETA_TIPO[tipo]} · ${fuente}` : ETIQUETA_TIPO[tipo]}
      className={`inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-0.5 text-base font-semibold ${ESTILO[tipo]}`}
    >
      <span aria-hidden="true" className={`size-2.5 rounded-full ${PUNTO[tipo]}`} />
      {ETIQUETA_TIPO[tipo]}
    </span>
  );
}

const cifra = (n: number | null | undefined, decimales = 0) =>
  n == null ? "Sin dato" : n.toLocaleString("es-MX", { maximumFractionDigits: decimales, minimumFractionDigits: decimales });

type PanelProps = {
  dia: number;
  onDia: (d: number) => void;
  hora: number;
  onHora: (h: number) => void;
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

/** Panel derecho (30 %): altas, dato real, día y hora, cobertura. Sin scroll a 1280×720. */
export function Panel(p: PanelProps) {
  return (
    <div className="flex h-full flex-col gap-3 overflow-hidden p-4">
      <section aria-live="polite" className="flex items-center justify-between rounded-2xl border border-stone-400 bg-white px-4 py-3">
        <div>
          <p className="text-base font-medium text-stone-800">Altas hoy</p>
          <p className="text-4xl font-bold tabular-nums text-stone-900">{p.altasHoy}</p>
        </div>
        <span className="relative flex size-4" aria-hidden="true">
          {p.altaReciente && <span className="absolute inset-0 animate-ping rounded-full bg-[#c2410c] opacity-70 motion-reduce:animate-none" />}
          <span className="relative size-4 rounded-full bg-[#c2410c]" />
        </span>
      </section>

      <div className="flex items-center justify-between gap-3 rounded-2xl border border-stone-400 bg-white px-4 py-3">
        <span className="text-lg font-semibold text-stone-900">Ver dato real</span>
        <button
          type="button"
          role="switch"
          aria-checked={p.datoReal}
          onClick={() => p.onDatoReal(!p.datoReal)}
          className={`relative h-8 w-14 rounded-full transition-colors ${p.datoReal ? "bg-stone-900" : "bg-stone-400"}`}
        >
          <span className={`absolute top-1 size-6 rounded-full bg-white transition-all ${p.datoReal ? "left-7" : "left-1"}`} />
          <span className="sr-only">{p.datoReal ? "Activado" : "Desactivado"}</span>
        </button>
      </div>

      {p.datoReal ? (
        <section aria-label="Dato CNBV por alcaldía" className="flex flex-col gap-2">
          <p className="text-base leading-snug text-stone-800">
            Transacciones con tarjeta por adulto, trimestre {p.alcaldias[0]?.trimestre ?? "2023-T2"}.
          </p>
          {p.alcaldias.map((a) => (
            <div key={a.cvegeo} className="rounded-2xl border border-stone-400 bg-white px-4 py-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-lg font-semibold text-stone-900">{a.municipio}</span>
                <Etiqueta tipo={a.tipo_dato} fuente={`CNBV ${a.trimestre}`} />
              </div>
              <p className="mt-1 text-3xl font-bold tabular-nums text-stone-900">{cifra(a.tpv_por_adulto, 2)}</p>
              <p className="text-base text-stone-800">transacciones por adulto</p>
            </div>
          ))}
          {p.origenAlcaldias === "ejemplo" && <p className="text-base font-medium text-stone-800">Datos de ejemplo.</p>}
        </section>
      ) : (
        <section aria-label="Leyenda" className="rounded-2xl border border-stone-400 bg-white px-4 py-3 text-base text-stone-900">
          <p className="font-semibold">Color = índice de impulso</p>
          <div className="mt-2 h-3 rounded-full bg-gradient-to-r from-[#ffeedd] via-[#f5914a] to-[#9a3412]" />
          <div className="mt-1 flex justify-between text-sm text-stone-800">
            <span>bajo</span>
            <span>alto</span>
          </div>
          <p className="mt-2 flex items-center gap-2">
            <span className="inline-block size-4 rounded bg-[#c3c9d0]" aria-hidden="true" />
            Gris: menos de 3 negocios
          </p>
        </section>
      )}

      <section aria-label="Día y hora" className="flex flex-col gap-2 rounded-2xl border border-stone-400 bg-white px-4 py-3">
        <p className="text-lg font-semibold text-stone-900">¿Qué día y a qué hora?</p>
        <div role="group" aria-label="Día de la semana" className="grid grid-cols-7 gap-1">
          {DIAS.map((nombre, i) => (
            <button
              key={nombre}
              type="button"
              aria-pressed={p.dia === i}
              onClick={() => p.onDia(i)}
              className={`h-11 rounded-lg text-base font-semibold capitalize ${
                p.dia === i ? "bg-stone-900 text-white" : "bg-stone-100 text-stone-900 hover:bg-stone-200"
              }`}
            >
              {nombre}
            </button>
          ))}
        </div>
        <label className="flex flex-col gap-1 text-base font-medium text-stone-900">
          <span className="tabular-nums">Hora: {String(p.hora).padStart(2, "0")}:00</span>
          <input
            type="range"
            min={0}
            max={23}
            step={1}
            value={p.hora}
            onChange={(e) => p.onHora(Number(e.target.value))}
            className="h-6 w-full accent-stone-900"
          />
        </label>
        <p className="text-base text-stone-900">
          Tianguis abiertos: <span className="font-bold tabular-nums">{p.abiertos}</span>
        </p>
        {p.cobertura ? (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-base text-stone-900">
              Población con tianguis a 800 m:{" "}
              <span className="text-2xl font-bold tabular-nums">{cifra(p.cobertura.pct, 1)} %</span>
            </span>
            <Etiqueta tipo={p.cobertura.tipo} fuente={p.cobertura.fuente} />
          </div>
        ) : (
          <p className="text-base text-stone-800">Cargando cobertura…</p>
        )}
      </section>

      <p className="mt-auto text-sm leading-snug text-stone-700">
        {p.origenHex === "ejemplo" ? "Hexágonos: datos de ejemplo. " : ""}
        Toca un hexágono para ver sus cifras y su fuente.
      </p>
    </div>
  );
}

/** Tarjeta del hexágono tocado (sobre el mapa). Oculto: sin cifras por privacidad. */
export function TarjetaHex({ p, onCerrar }: { p: PropsHex; onCerrar: () => void }) {
  const tc = p.tipo_campos;
  const fuentePoblacion = "hexágonos del pipeline (data/processed/hex.geojson)";
  const alcaldia = NOMBRE_ALCALDIA[p.alcaldia_cvegeo] ?? "CDMX";
  return (
    <section
      aria-label="Detalle del hexágono"
      className="w-full max-w-md rounded-2xl border border-stone-400 bg-white p-4 shadow-lg"
    >
      <header className="mb-2 flex items-start justify-between gap-3">
        <h2 className="text-xl font-bold text-stone-900">Hexágono en {alcaldia}</h2>
        <button
          type="button"
          onClick={onCerrar}
          className="shrink-0 rounded-lg bg-stone-100 px-3 py-1 text-base font-semibold text-stone-900 hover:bg-stone-200"
        >
          Cerrar
        </button>
      </header>

      {p.oculto ? (
        <p className="text-lg leading-relaxed text-stone-900">Menos de 3 negocios: sin cifras por privacidad</p>
      ) : (
        <dl className="grid gap-2 text-base text-stone-900">
          <Fila etiqueta="Población" valor={cifra(p.poblacion)} tipo={tc.poblacion ?? "simulado"} fuente={fuentePoblacion} />
          <Fila
            etiqueta="Negocios de barrio"
            valor={`${cifra(p.negocios_barriales)} de ${cifra(p.negocios_total)}`}
            tipo={tc.negocios_barriales ?? "simulado"}
            fuente="DENUE y Tianguis Abierto (pipeline)"
          />
          <Fila
            etiqueta="Actividad con tarjeta (estimada)"
            valor={cifra(p.actividad_tpv_est, 2)}
            tipo={tc.actividad_tpv_est ?? "estimado"}
            fuente="CNBV por alcaldía, repartido por negocios"
          />
          <Fila
            etiqueta="Impulso"
            valor={p.impulso == null ? "Sin dato" : `${Math.round(p.impulso * 100)} de 100`}
            tipo={tc.impulso ?? "estimado"}
            fuente="Índice propio del pipeline"
          />
          <Fila etiqueta="Periodo" valor={p.periodo_cnbv ?? "Sin periodo"} tipo="real" fuente="CNBV" />
        </dl>
      )}
    </section>
  );
}

function Fila({ etiqueta, valor, tipo, fuente }: { etiqueta: string; valor: string; tipo: TipoDato; fuente: string }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-stone-200 pb-2 last:border-0">
      <dt className="font-medium">{etiqueta}</dt>
      <dd className="flex items-center gap-2">
        <span className="text-lg font-bold tabular-nums">{valor}</span>
        <Etiqueta tipo={tipo} fuente={fuente} />
      </dd>
      <p className="w-full text-sm text-stone-700">Fuente: {fuente}</p>
    </div>
  );
}
