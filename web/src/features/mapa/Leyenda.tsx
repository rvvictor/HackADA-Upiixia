import { metaCapa, type Capa } from "../../lib/map/hex";
import type { TipoDato } from "./datos";

/** Leyenda de una sola rampa: altura y color miden lo mismo (IDEA-v2 §1.2). Legible a 1280×720 y a 390 px.
 *  `tipoDato` se acepta por compatibilidad, pero no se muestra (uak decision CO-028: sin etiquetas en pantalla). */
export function Leyenda({ capa }: { capa: Capa; tipoDato?: TipoDato }) {
  const m = metaCapa(capa);
  const pasos = [1, 2, 3, 4, 5].map((n) => `var(--pb-${m.rampa}-${n})`).join(", ");
  return (
    <section
      aria-label="Leyenda del mapa"
      className="w-80 max-w-full rounded-(--pb-radio-tarjeta) bg-(--pb-vidrio) p-3 md:p-4 text-(--pb-texto) shadow-(--pb-sombra-alta) backdrop-blur-sm"
    >
      <p className="text-base font-semibold">{m.metrica}</p>
      <div aria-hidden="true" className="mt-2 h-3 rounded-full" style={{ background: `linear-gradient(to right, ${pasos})` }} />
      <div className="mt-1 flex justify-between text-base text-(--pb-texto-2)">
        <span>Menos</span>
        <span>Más alto y más intenso</span>
      </div>
      <p className="mt-2 text-base text-(--pb-texto-2)">Fuente: {m.fuente}</p>
    </section>
  );
}
