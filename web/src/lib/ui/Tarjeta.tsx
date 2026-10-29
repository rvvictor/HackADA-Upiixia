import type { HTMLAttributes, ReactNode } from "react";

type TarjetaProps = HTMLAttributes<HTMLElement> & {
  titulo?: ReactNode;
  /** Small uppercase line above the title, e.g. "Paso 3". */
  antetitulo?: ReactNode;
  /** Right side of the header, e.g. an Etiqueta or a ghost button. */
  accion?: ReactNode;
  /** "elevada" lifts on hover (clickable cards); "plana" has no shadow (nested groups). */
  variante?: "normal" | "elevada" | "plana";
};

const variantes = {
  normal: "shadow-(--pb-sombra)",
  elevada: "shadow-(--pb-sombra) motion-safe:transition-[transform,box-shadow] motion-safe:duration-200 hover:-translate-y-0.5 hover:shadow-(--pb-sombra-alta)",
  plana: "",
};

/** White surface with a hairline border; use only when it groups something real (DESIGN.md §4). */
export function Tarjeta({ titulo, antetitulo, accion, variante = "normal", className = "", children, ...rest }: TarjetaProps) {
  return (
    <section
      className={`rounded-(--pb-radio-tarjeta) border border-(--pb-borde) bg-(--pb-superficie) p-6 ${variantes[variante]} ${className}`}
      {...rest}
    >
      {(titulo || accion || antetitulo) && (
        <header className="mb-4 flex items-start justify-between gap-3">
          <div className="min-w-0">
            {antetitulo && (
              <p className="mb-1 text-[0.778rem] font-semibold uppercase tracking-[0.12em] text-(--pb-acento)">{antetitulo}</p>
            )}
            {titulo && <h2 className="text-[1.333rem] font-semibold leading-tight tracking-tight">{titulo}</h2>}
          </div>
          {accion}
        </header>
      )}
      {children}
    </section>
  );
}
