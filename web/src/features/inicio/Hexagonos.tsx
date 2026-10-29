import type { CSSProperties } from "react";
import { cellToBoundary, gridDiskDistances, latLngToCell } from "h3-js";

// Centro simulado: Coyoacán, sede del Chilangatón (IDEA.md §10). Todo lo que se dibuja aquí es demo.
const CENTRO: [number, number] = [19.3486, -99.153];
const RESOLUCION = 8;
const ANILLOS = 6;
const LADO = 600;

type Color = "rosa" | "cempasuchil" | "jade" | "anil";
const PALETA: Color[] = ["anil", "anil", "jade", "anil", "rosa", "anil", "jade", "anil", "cempasuchil", "anil", "jade", "anil"];

type Celda = { id: string; d: string; anillo: number; color: Color; o: number };

// Proyección plana local (equirectangular corregida por coseno): suficiente para una rejilla de ~10 km.
function construirRejilla(): { celdas: Celda[]; radio: number } {
  const origen = latLngToCell(CENTRO[0], CENTRO[1], RESOLUCION);
  const anillos = gridDiskDistances(origen, ANILLOS);
  const cosLat = Math.cos((CENTRO[0] * Math.PI) / 180);
  const proyectar = (lat: number, lng: number): [number, number] => [
    (lng - CENTRO[1]) * cosLat,
    -(lat - CENTRO[0]),
  ];

  const crudas: { id: string; anillo: number; pts: [number, number][] }[] = [];
  anillos.forEach((ring, anillo) => {
    ring.forEach((id) => {
      crudas.push({
        id,
        anillo,
        pts: cellToBoundary(id, false).map(([lat, lng]) => proyectar(lat, lng)),
      });
    });
  });

  let max = 0;
  crudas.forEach((c) => c.pts.forEach(([x, y]) => (max = Math.max(max, Math.abs(x), Math.abs(y)))));
  const escala = (LADO / 2 - 14) / max;
  const mitad = LADO / 2;

  const celdas = crudas.map((c, i) => {
    const d = c.pts
      .map(([x, y], j) => `${j === 0 ? "M" : "L"}${(mitad + x * escala).toFixed(1)} ${(mitad + y * escala).toFixed(1)}`)
      .join(" ") + "Z";
    const color = c.anillo === 0 ? "cempasuchil" : PALETA[(i * 7 + c.anillo * 3) % PALETA.length];
    const o = 0.12 + ((i * 37) % 50) / 100;
    return { id: c.id, d, anillo: c.anillo, color, o };
  });

  return { celdas, radio: ANILLOS };
}

const COLOR_VAR: Record<Color, string> = {
  rosa: "var(--ci-rosa)",
  cempasuchil: "var(--ci-cempasuchil)",
  jade: "var(--ci-jade)",
  anil: "var(--ci-anil-luz)",
};

const { celdas, radio } = construirRejilla();

/** Rejilla de hexágonos H3 (res 8) alrededor de Coyoacán. Se enciende en olas desde el centro. */
export function RejillaHex({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox={`0 0 ${LADO} ${LADO}`}
      className={className}
      role="img"
      aria-labelledby="titulo-hex"
    >
      <title id="titulo-hex">
        Rejilla de hexágonos H3 simulada alrededor de Coyoacán: las celdas se encienden en olas desde el centro.
      </title>
      <defs>
        <radialGradient id="halo-hex" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#FFB703" stopOpacity="0.35" />
          <stop offset="60%" stopColor="#E6007E" stopOpacity="0.12" />
          <stop offset="100%" stopColor="#E6007E" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx={LADO / 2} cy={LADO / 2} r={LADO / 2} fill="url(#halo-hex)" />
      {celdas.map((c) => (
        <path
          key={c.id}
          d={c.d}
          className="hx"
          style={
            {
              "--c": COLOR_VAR[c.color],
              "--o": c.o.toFixed(2),
              "--d": (c.anillo / radio).toFixed(3),
            } as CSSProperties
          }
        />
      ))}
      <circle cx={LADO / 2} cy={LADO / 2} r="7" fill="#FFB703" className="hx-centro" />
    </svg>
  );
}
