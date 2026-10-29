// TODO CO-007: adaptador mínimo; reemplazar por lib/map/iconos.ts y ChipsTipo.tsx cuando estén en main.
import { TIPOS, type TipoPunto } from "./puntos";

export function ChipsTipoMinimo({ activos, onAlternar }: { activos: TipoPunto[]; onAlternar: (t: TipoPunto) => void }) {
  return (
    <div role="group" aria-label="Tipos de punto" className="pointer-events-auto flex flex-wrap gap-1 rounded-2xl bg-white p-1.5 shadow-md">
      {TIPOS.map((t) => {
        const on = activos.includes(t.id);
        return (
          <button
            key={t.id}
            type="button"
            aria-pressed={on}
            onClick={() => onAlternar(t.id)}
            className={`flex items-center gap-1.5 rounded-xl px-3 py-2 text-base font-semibold ${on ? "bg-stone-900 text-white" : "text-stone-900 hover:bg-stone-100"}`}
          >
            <span aria-hidden style={{ color: on ? "#fff" : t.color }}>{t.glifo}</span>
            {t.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
