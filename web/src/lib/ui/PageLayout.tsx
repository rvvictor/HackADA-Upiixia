import type { HTMLAttributes, ReactNode } from "react";

type PageLayoutProps = HTMLAttributes<HTMLDivElement> & {
  /** "lectura" (default): centered column up to 1280 px. "lleno": edge to edge, full height (map views). */
  ancho?: "lectura" | "lleno";
  children: ReactNode;
};

/** Content container for a view inside AppShell. Gutters: 16 px on phones, 32 px from md. */
export function PageLayout({ ancho = "lectura", className = "", children, ...rest }: PageLayoutProps) {
  const base = ancho === "lleno" ? "relative h-full w-full" : "mx-auto w-full max-w-[1280px] px-4 py-6 md:px-8 md:py-10";
  return (
    <div className={`${base} ${className}`} {...rest}>
      {children}
    </div>
  );
}
