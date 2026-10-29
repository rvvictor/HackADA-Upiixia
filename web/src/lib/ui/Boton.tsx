import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variante = "primario" | "secundario" | "fantasma" | "oscuro";
type Tamano = "md" | "lg";

const variantes: Record<Variante, string> = {
  primario:
    "bg-(--pb-acento) text-white border-transparent shadow-(--pb-sombra-marca) hover:bg-(--pb-acento-fuerte) hover:-translate-y-0.5",
  secundario:
    "bg-(--pb-superficie) text-(--pb-texto) border-(--pb-borde) shadow-(--pb-sombra) hover:border-(--pb-borde-fuerte) hover:-translate-y-0.5",
  fantasma: "bg-transparent text-(--pb-texto) border-transparent hover:bg-(--pb-superficie-2)",
  oscuro: "bg-(--pb-texto) text-white border-transparent hover:bg-black hover:-translate-y-0.5",
};

const tamanos: Record<Tamano, string> = {
  md: "min-h-(--pb-alto-control) px-5 text-base",
  lg: "min-h-14 px-7 text-lg",
};

type BotonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variante?: Variante;
  tamano?: Tamano;
  icono?: ReactNode;
  anchoCompleto?: boolean;
};

/** One `primario` per screen; labels of 3 words or fewer (DESIGN.md §5). */
export function Boton({
  variante = "primario",
  tamano = "md",
  icono,
  anchoCompleto = false,
  className = "",
  type = "button",
  children,
  ...rest
}: BotonProps) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full border font-semibold tracking-tight motion-safe:transition-[background-color,transform,box-shadow,border-color] motion-safe:duration-200 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none ${variantes[variante]} ${tamanos[tamano]} ${anchoCompleto ? "w-full" : ""} ${className}`}
      {...rest}
    >
      {icono && <span aria-hidden="true" className="inline-flex text-[1.222rem]">{icono}</span>}
      {children}
    </button>
  );
}
