import { animate, useInView, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";

import { Etiqueta, type TipoDato } from "./Etiqueta";

type CifraProps = {
  valor: number | null;
  etiqueta: string;
  /** Every figure says what it is (DESIGN.md §1). */
  tipo: TipoDato;
  fuente?: string;
  /** e.g. "%", " km". */
  sufijo?: string;
  prefijo?: string;
  decimales?: number;
  tamano?: "md" | "lg" | "xl";
  /** Light text for dark backgrounds. */
  oscuro?: boolean;
  className?: string;
};

const tamanos = { md: "text-[2rem]", lg: "text-[2.75rem]", xl: "text-[4rem]" };

function formato(n: number, decimales: number): string {
  return n.toLocaleString("es-MX", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
}

/** A big tabular number that counts up when it enters the screen or changes, with its label and data type. */
export function Cifra({
  valor,
  etiqueta,
  tipo,
  fuente,
  sufijo = "",
  prefijo = "",
  decimales = 0,
  tamano = "md",
  oscuro = false,
  className = "",
}: CifraProps) {
  const ref = useRef<HTMLDivElement>(null);
  const visible = useInView(ref, { once: true, margin: "-40px" });
  const sinMovimiento = useReducedMotion();
  const [mostrado, setMostrado] = useState(0);
  const anterior = useRef(0);

  useEffect(() => {
    if (valor === null || !visible) return;
    if (sinMovimiento) {
      anterior.current = valor;
      queueMicrotask(() => setMostrado(valor));
      return;
    }
    const control = animate(anterior.current, valor, {
      duration: 0.9,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: setMostrado,
    });
    anterior.current = valor;
    return () => control.stop();
  }, [valor, visible, sinMovimiento]);

  return (
    <div ref={ref} className={`flex flex-col gap-1.5 ${className}`}>
      <span
        className={`pb-cifra pb-display font-bold ${tamanos[tamano]} ${oscuro ? "text-(--pb-hero-texto)" : "text-(--pb-texto)"}`}
      >
        {valor === null ? "—" : `${prefijo}${formato(mostrado, decimales)}${sufijo}`}
      </span>
      <span className={`text-base leading-snug ${oscuro ? "text-(--pb-hero-texto-2)" : "text-(--pb-texto-2)"}`}>{etiqueta}</span>
      <Etiqueta tipo={tipo} fuente={fuente} className="self-start" />
    </div>
  );
}
