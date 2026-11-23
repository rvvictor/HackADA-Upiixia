import { Basket, Bicycle, House, MapTrifold, Storefront, type Icon } from "@phosphor-icons/react";
import { Logo } from "./Logo";

export type NavItem = { route: string; label: string };

// One icon per known view; an unknown view falls back to the map icon so a new feature never breaks the bar.
const iconos: Record<string, Icon> = {
  inicio: House,
  mapa: MapTrifold,
  usuario: Basket,
  negocio: Storefront,
  repartidor: Bicycle,
};

type NavBarProps = { items: NavItem[]; actual?: string };

/** Top bar on desktop (logo + text tabs); on phones the tabs move to a bottom bar reachable with one thumb. */
export function NavBar({ items, actual }: NavBarProps) {
  return (
    <>
      <header className="relative z-20 flex h-(--pb-alto-nav) shrink-0 items-center justify-between gap-6 bg-(--pb-fondo) px-4 md:px-8">
        <a href="#/inicio" className="rounded-full" aria-label="colonIA, ir al inicio">
          <Logo className="text-[1.4rem]" />
        </a>
        <nav aria-label="Vistas" className="hidden items-center gap-1 md:flex">
          {items.map((it) => {
            const activo = it.route === actual;
            return (
              <a
                key={it.route}
                href={`#/${it.route}`}
                aria-current={activo ? "page" : undefined}
                className={`inline-flex min-h-(--pb-alto-control) items-center rounded-full px-4 text-base font-medium motion-safe:transition-colors ${
                  activo
                    ? "bg-(--pb-acento-suave) text-(--pb-acento-fuerte)"
                    : "text-(--pb-texto-2) hover:bg-(--pb-superficie-2) hover:text-(--pb-texto)"
                }`}
              >
                {it.label}
              </a>
            );
          })}
        </nav>
      </header>
      <nav
        aria-label="Vistas"
        className="fixed inset-x-0 bottom-0 z-30 grid border-t border-(--pb-borde) bg-(--pb-superficie) pb-[env(safe-area-inset-bottom)] md:hidden"
        style={{ gridTemplateColumns: `repeat(${items.length}, minmax(0, 1fr))` }}
      >
        {items.map((it) => {
          const activo = it.route === actual;
          const Icono = iconos[it.route] ?? MapTrifold;
          return (
            <a
              key={it.route}
              href={`#/${it.route}`}
              aria-current={activo ? "page" : undefined}
              className={`flex min-h-16 flex-col items-center justify-center gap-0.5 text-[0.8125rem] font-medium ${
                activo ? "text-(--pb-acento)" : "text-(--pb-texto-2)"
              }`}
            >
              <Icono size={24} weight={activo ? "fill" : "regular"} aria-hidden="true" />
              {it.label}
            </a>
          );
        })}
      </nav>
    </>
  );
}
