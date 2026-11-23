import type { ReactNode } from "react";
import { NavBar, type NavItem } from "./NavBar";

type AppShellProps = { items: NavItem[]; actual?: string; children: ReactNode };

/** The frame of every view: nav on top (bottom bar on phones) and a main area that fills the rest of the screen.
 *  Map views fill `main` edge to edge; text views wrap their content in `PageLayout`. */
export function AppShell({ items, actual, children }: AppShellProps) {
  return (
    <div className="flex h-[100dvh] flex-col bg-(--pb-fondo) font-sans text-(--pb-texto)">
      <a
        href="#contenido"
        className="sr-only z-50 rounded-full bg-(--pb-acento) px-4 py-3 text-(--pb-sobre-acento) focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Saltar al contenido
      </a>
      <NavBar items={items} actual={actual} />
      {/* Bottom padding on phones leaves room for the bottom bar; md:pb-0 because the tabs live in the top bar there. */}
      <main id="contenido" className="relative min-h-0 flex-1 overflow-y-auto pb-[calc(4rem+env(safe-area-inset-bottom))] md:pb-0">
        {children}
      </main>
    </div>
  );
}
