// Toggle chips per point type (CO-007): icon + label + tooltip, never color alone.
import type { TipoPunto } from "../types";
import { TIPOS_ICONO } from "./iconos";

type ChipsTipoProps = {
  activos: TipoPunto[];
  onAlternar: (t: TipoPunto) => void;
  /** Optional count per type, shown in the tooltip. */
  conteos?: Partial<Record<TipoPunto, number>>;
};

export function ChipsTipo({ activos, onAlternar, conteos }: ChipsTipoProps) {
  return (
    <div role="group" aria-label="Tipos de punto" className="pointer-events-auto flex flex-wrap gap-1 rounded-2xl bg-white p-1.5 shadow-md">
      {TIPOS_ICONO.map((t) => {
        const on = activos.includes(t.id);
        const n = conteos?.[t.id];
        const tooltip = `${t.etiqueta} (${t.forma})${n != null ? ` · ${n} puntos` : ""} · ${on ? "visible, clic para ocultar" : "oculto, clic para mostrar"}`;
        return (
          <button
            key={t.id}
            type="button"
            aria-pressed={on}
            title={tooltip}
            aria-label={tooltip}
            onClick={() => onAlternar(t.id)}
            className={`flex items-center gap-1.5 rounded-xl px-3 py-2 text-base font-semibold transition-colors ${on ? "bg-stone-900 text-white" : "text-stone-500 hover:bg-stone-100"}`}
          >
            <img src={t.icono} alt="" aria-hidden width={18} height={18} className={on ? "" : "opacity-40 grayscale"} />
            {t.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
