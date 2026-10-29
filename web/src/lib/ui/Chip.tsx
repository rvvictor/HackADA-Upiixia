import type { ReactNode } from "react";

type ChipProps = {
  children: ReactNode;
  icono?: ReactNode;
  /** With onClick the chip is a toggle (aria-pressed, 48 px tall); without it, a static label. */
  activo?: boolean;
  onClick?: () => void;
  /** Static chips only: "marca" (rosa), "exito" (jade), "neutro". */
  tono?: "neutro" | "marca" | "exito";
  className?: string;
};

const base = "inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-3.5 font-medium";

const tonos = {
  neutro: "border-(--pb-borde) bg-(--pb-superficie-2) text-(--pb-texto)",
  marca: "border-transparent bg-(--pb-acento-suave) text-(--pb-acento-fuerte)",
  exito: "border-transparent bg-(--pb-real-fondo) text-(--pb-real-texto)",
};

export function Chip({ children, icono, activo = false, onClick, tono = "neutro", className = "" }: ChipProps) {
  const contenido = (
    <>
      {icono && <span aria-hidden="true" className="inline-flex">{icono}</span>}
      {children}
    </>
  );

  if (!onClick) {
    return <span className={`${base} min-h-9 text-[0.889rem] ${tonos[tono]} ${className}`}>{contenido}</span>;
  }

  return (
    <button
      type="button"
      aria-pressed={activo}
      onClick={onClick}
      className={`${base} min-h-(--pb-alto-control) text-base motion-safe:transition-[background-color,border-color,transform] motion-safe:duration-150 active:scale-[0.98] ${
        activo
          ? "border-(--pb-acento) bg-(--pb-acento) text-white shadow-(--pb-sombra-marca)"
          : "border-(--pb-borde) bg-(--pb-superficie) text-(--pb-texto) hover:border-(--pb-borde-fuerte)"
      } ${className}`}
    >
      {contenido}
    </button>
  );
}
