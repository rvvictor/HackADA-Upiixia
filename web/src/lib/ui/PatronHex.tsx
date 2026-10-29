import { useId } from "react";

type PatronHexProps = {
  className?: string;
  /** Stroke color; defaults to the border token. */
  color?: string;
  /** Hexagon size in px. */
  tamano?: number;
  opacidad?: number;
};

/** Hexagon grid texture (the same H3 motif as the map) for section and hero backgrounds. Purely decorative. */
export function PatronHex({ className = "", color = "var(--pb-borde)", tamano = 28, opacidad = 0.6 }: PatronHexProps) {
  const id = useId();
  const w = tamano * Math.sqrt(3);
  const h = tamano * 3;
  const r = tamano;
  const puntos = (cx: number, cy: number) =>
    [0, 1, 2, 3, 4, 5]
      .map((i) => {
        const a = (Math.PI / 3) * i - Math.PI / 6;
        return `${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`;
      })
      .join(" ");
  return (
    <svg aria-hidden="true" className={`pointer-events-none absolute inset-0 h-full w-full ${className}`} style={{ opacity: opacidad }}>
      <defs>
        <pattern id={id} width={w} height={h} patternUnits="userSpaceOnUse">
          <polygon points={puntos(w / 2, r)} fill="none" stroke={color} strokeWidth="1" />
          <polygon points={puntos(0, r * 2.5)} fill="none" stroke={color} strokeWidth="1" />
          <polygon points={puntos(w, r * 2.5)} fill="none" stroke={color} strokeWidth="1" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill={`url(#${id})`} />
    </svg>
  );
}
