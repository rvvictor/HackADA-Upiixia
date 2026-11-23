import type { ReactNode } from "react";

type PageHeaderProps = {
  titulo: ReactNode;
  descripcion?: ReactNode;
  /** One primary action at most (DESIGN.md §5). */
  acciones?: ReactNode;
  className?: string;
};

/** View title: display type, one plain-Spanish line under it, actions to the right (stacked on phones). */
export function PageHeader({ titulo, descripcion, acciones, className = "" }: PageHeaderProps) {
  return (
    <header className={`mb-6 flex flex-col gap-4 md:mb-10 md:flex-row md:items-end md:justify-between ${className}`}>
      <div className="max-w-3xl">
        <h1 className="pb-display text-[2.3rem] font-extrabold md:text-[3.2rem]">{titulo}</h1>
        {descripcion && <p className="mt-3 max-w-[48ch] text-lg leading-relaxed text-(--pb-texto-2)">{descripcion}</p>}
      </div>
      {acciones && <div className="flex shrink-0 flex-wrap gap-3">{acciones}</div>}
    </header>
  );
}
