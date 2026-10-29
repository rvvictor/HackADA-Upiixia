import type { HTMLAttributes, ReactNode } from "react";

type SeccionProps = HTMLAttributes<HTMLElement> & {
  antetitulo?: ReactNode;
  titulo?: ReactNode;
  descripcion?: ReactNode;
  oscuro?: boolean;
};

/** A page section with an editorial header: small rosa kicker, big display title, one-line description. */
export function Seccion({ antetitulo, titulo, descripcion, oscuro = false, className = "", children, ...rest }: SeccionProps) {
  return (
    <section
      className={`relative px-5 py-16 sm:px-10 sm:py-24 ${oscuro ? "bg-(--pb-hero-fondo) text-(--pb-hero-texto)" : ""} ${className}`}
      {...rest}
    >
      <div className="mx-auto max-w-6xl">
        {(antetitulo || titulo || descripcion) && (
          <header className="mb-10 max-w-3xl">
            {antetitulo && (
              <p className="mb-3 text-sm font-semibold uppercase tracking-[0.14em] text-(--pb-marca)">{antetitulo}</p>
            )}
            {titulo && <h2 className="pb-display text-[2.5rem] font-bold sm:text-[3.5rem]">{titulo}</h2>}
            {descripcion && (
              <p className={`mt-4 text-lg leading-relaxed ${oscuro ? "text-(--pb-hero-texto-2)" : "text-(--pb-texto-2)"}`}>
                {descripcion}
              </p>
            )}
          </header>
        )}
        {children}
      </div>
    </section>
  );
}
