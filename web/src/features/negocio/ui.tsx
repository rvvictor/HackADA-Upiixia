import type { ButtonHTMLAttributes, ReactNode } from "react";
import type { TipoDato } from "./tipos";

// Local stand-ins for web/src/lib/ui (PB-003, not on main yet). Same props as PB-003's Etiqueta,
// so switching is an import change. Colors read --pb-* tokens with fallbacks.

const FOCO = "focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-[var(--pb-foco,#1d4ed8)]";

const ETIQUETAS: Record<TipoDato, { texto: string; clase: string; punto: string }> = {
  real: {
    texto: "Dato real",
    clase: "bg-[var(--pb-real-fondo,#dcfce7)] text-[var(--pb-real-texto,#14532d)] border-transparent",
    punto: "bg-current",
  },
  estimado: {
    texto: "Estimado",
    clase: "bg-[var(--pb-estimado-fondo,#dbeafe)] text-[var(--pb-estimado-texto,#1e3a8a)] border-transparent",
    punto: "border-2 border-current",
  },
  simulado: {
    texto: "Simulado",
    clase:
      "bg-[var(--pb-simulado-fondo,#eceff3)] text-[var(--pb-simulado-texto,#3d4651)] border-dashed border-[var(--pb-simulado-texto,#3d4651)]",
    punto: "border-2 border-dashed border-current",
  },
};

export function Etiqueta({ tipo, fuente, className = "" }: { tipo: TipoDato; fuente?: string | null; className?: string }) {
  const e = ETIQUETAS[tipo];
  return (
    <span
      title={fuente ? `${e.texto} · Fuente: ${fuente}` : e.texto}
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-0.5 text-[0.889rem] font-medium leading-6 ${e.clase} ${className}`}
    >
      <span aria-hidden="true" className={`size-2 rounded-full ${e.punto}`} />
      {e.texto}
      {fuente && <span className="sr-only">. Fuente: {fuente}</span>}
    </span>
  );
}

type BotonProps = ButtonHTMLAttributes<HTMLButtonElement> & { variante?: "primario" | "secundario" };

export function Boton({ variante = "primario", className = "", ...props }: BotonProps) {
  const estilo =
    variante === "primario"
      ? "bg-[var(--pb-acento,#c2410c)] text-white hover:bg-[var(--pb-acento-fuerte,#9a3412)] disabled:opacity-60"
      : "border-2 border-[var(--pb-borde-fuerte,#7d8793)] bg-[var(--pb-superficie,#fff)] text-[var(--pb-texto,#15191e)] hover:bg-[var(--pb-superficie-2,#eef1f4)]";
  return (
    <button
      type="button"
      className={`inline-flex min-h-12 items-center justify-center gap-2 rounded-[var(--pb-radio-control,12px)] px-5 text-lg font-semibold ${estilo} ${FOCO} ${className}`}
      {...props}
    />
  );
}

export function Tarjeta({ titulo, extra, children, className = "" }: { titulo: string; extra?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section
      aria-label={titulo}
      className={`rounded-[var(--pb-radio-tarjeta,16px)] border border-[var(--pb-borde,#d3d9e0)] bg-[var(--pb-superficie,#fff)] p-4 shadow-sm ${className}`}
    >
      <header className="mb-3 flex flex-wrap items-center gap-2">
        <h2 className="text-[1.222rem] font-semibold text-[var(--pb-texto,#15191e)]">{titulo}</h2>
        {extra}
      </header>
      {children}
    </section>
  );
}
