import { useEffect, useRef, useState } from "react";

type CifraProps = {
  valor: number;
  decimales?: number;
  prefijo?: string;
  sufijo?: string;
};

function reduceMovimiento() {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Número grande que sube desde 0 cuando entra en pantalla. Con movimiento reducido muestra el valor final. */
export function Cifra({ valor, decimales = 0, prefijo = "", sufijo = "" }: CifraProps) {
  const [actual, setActual] = useState(() => (reduceMovimiento() ? valor : 0));
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || reduceMovimiento()) return;
    let raf = 0;
    const observador = new IntersectionObserver(
      ([entrada]) => {
        if (!entrada.isIntersecting) return;
        observador.disconnect();
        const inicio = performance.now();
        const duracion = 1600;
        const paso = (ahora: number) => {
          const t = Math.min(1, (ahora - inicio) / duracion);
          const eased = 1 - Math.pow(1 - t, 3);
          setActual(valor * eased);
          if (t < 1) raf = requestAnimationFrame(paso);
        };
        raf = requestAnimationFrame(paso);
      },
      { threshold: 0.6 },
    );
    observador.observe(el);
    return () => {
      observador.disconnect();
      cancelAnimationFrame(raf);
    };
  }, [valor]);

  const texto = actual.toLocaleString("es-MX", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

  return (
    <span ref={ref} className="pb-cifra" aria-label={`${prefijo}${valor.toLocaleString("es-MX", { minimumFractionDigits: decimales, maximumFractionDigits: decimales })}${sufijo}`}>
      <span aria-hidden="true">
        {prefijo}
        {texto}
        {sufijo}
      </span>
    </span>
  );
}
