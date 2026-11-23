// TODO CO-007: adaptador mínimo; reemplazar por lib/map/iconos.ts y ChipsTipo.tsx cuando estén en main.
// Maqueta viva: chips píldora de 48 px; el glifo conserva el color del punto en el mapa (puntos.ts, CO-031).
import { TIPOS, type TipoPunto } from "./puntos";

export function ChipsTipoMinimo({ activos, onAlternar }: { activos: TipoPunto[]; onAlternar: (t: TipoPunto) => void }) {
  return (
    <div
      role="group"
      aria-label="Tipos de punto"
      className="pointer-events-auto flex flex-wrap gap-1 rounded-(--pb-radio-grande) bg-(--pb-superficie) p-1 shadow-(--pb-sombra)"
    >
      {TIPOS.map((t) => {
        const on = activos.includes(t.id);
        return (
          <button
            key={t.id}
            type="button"
            aria-pressed={on}
            onClick={() => onAlternar(t.id)}
            className={`flex min-h-(--pb-alto-control) items-center gap-2 rounded-full px-4 text-base font-semibold motion-safe:transition-colors ${
              on ? "bg-(--pb-acento-suave) text-(--pb-acento-fuerte)" : "text-(--pb-texto-2) hover:bg-(--pb-superficie-2)"
            }`}
          >
            <span aria-hidden="true" style={{ color: t.color }}>
              {t.glifo}
            </span>
            {t.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
