import { metaCapa, type Capa } from "../../lib/map/hex";
import { ETIQUETA_TIPO, type TipoDato } from "./datos";

/** Leyenda de una sola rampa: altura y color miden lo mismo (IDEA-v2 §1.2). */
export function Leyenda({ capa, tipoDato }: { capa: Capa; tipoDato?: TipoDato }) {
  const m = metaCapa(capa);
  const pasos = [1, 2, 3, 4, 5].map((n) => `var(--pb-${m.rampa}-${n})`).join(", ");
  return (
    <section aria-label="Leyenda del mapa" className="w-72 max-w-full rounded-2xl border border-stone-400 bg-white p-3 shadow-md">
      <p className="text-base font-bold text-stone-900">{m.metrica}</p>
      <div aria-hidden className="mt-2 h-3 rounded-full" style={{ background: `linear-gradient(to right, ${pasos})` }} />
      <div className="mt-1 flex justify-between text-sm text-stone-800">
        <span>Menos</span>
        <span>Más (más alto y más intenso)</span>
      </div>
      <p className="mt-2 text-sm text-stone-800">
        <span className="font-semibold">{ETIQUETA_TIPO[tipoDato ?? m.tipo_dato]}</span> · Fuente: {m.fuente}
      </p>
    </section>
  );
}
