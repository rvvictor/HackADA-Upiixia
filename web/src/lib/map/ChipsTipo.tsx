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
    <div role="group" aria-label="Tipos de punto" className="pointer-events-auto flex flex-wrap gap-1 rounded-(--pb-radio-grande) bg-(--pb-superficie) p-1 shadow-(--pb-sombra)">
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
            className={`flex min-h-(--pb-alto-control) items-center gap-2 rounded-full px-4 text-base font-semibold motion-safe:transition-colors ${on ? "bg-(--pb-acento-suave) text-(--pb-acento-fuerte)" : "text-(--pb-texto-2) hover:bg-(--pb-superficie-2)"}`}
          >
            <img src={t.icono} alt="" aria-hidden width={18} height={18} className={on ? "" : "opacity-40 grayscale"} />
            {t.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
