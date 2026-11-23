// Same values as `tipo_dato` in the PB-002 contract (web/src/lib/types.ts).
export type TipoDato = "real" | "estimado" | "simulado";

const estilos: Record<TipoDato, { texto: string; clase: string; punto: string }> = {
  real: {
    texto: "Dato real",
    clase: "bg-(--pb-real-fondo) text-(--pb-real-texto) border-transparent",
    punto: "bg-current",
  },
  estimado: {
    texto: "Estimado",
    clase: "bg-(--pb-estimado-fondo) text-(--pb-estimado-texto) border-transparent",
    punto: "border-2 border-current",
  },
  simulado: {
    texto: "Simulado",
    clase:
      "bg-(--pb-simulado-fondo) text-(--pb-simulado-texto) border-dashed border-(--pb-simulado-texto) " +
      "bg-[repeating-linear-gradient(135deg,transparent_0_6px,rgb(61_70_81/0.08)_6px_8px)]",
    punto: "border-2 border-dashed border-current",
  },
};

type EtiquetaProps = {
  tipo: TipoDato;
  /** Where the figure comes from, e.g. "CNBV 2023-T2". Shown as tooltip and read by screen readers. */
  fuente?: string;
  className?: string;
};

/** Hidden on screen by decision of cris (uak decision CO-028, 2026-11-23): the UI shows no real/simulado chips.
 *  `tipo_dato` and `fuente` stay in the API and the data; set this to true to bring every chip back at once. */
export const MOSTRAR_TIPO_DATO = false;

/** Data-type chip for a figure. Shape differs per type, not only color. Renders nothing while MOSTRAR_TIPO_DATO is false. */
export function Etiqueta({ tipo, fuente, className = "" }: EtiquetaProps) {
  if (!MOSTRAR_TIPO_DATO) return null;
  const e = estilos[tipo];
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
