import { COLORES } from "./colores";
import type { SerieAlcaldia } from "./tipos";

const fmt = (n: number) => n.toLocaleString("es-MX");

export function Leyenda({ series }: { series: SerieAlcaldia[] }) {
  return (
    <ul className="flex flex-wrap gap-x-5 gap-y-1 text-base text-(--pb-texto-2)">
      {series.map((s, i) => (
        <li key={s.alcaldia_cvegeo} className="flex items-center gap-2">
          <span aria-hidden className="inline-block h-2.5 w-5 rounded-full" style={{ background: COLORES[i % 2] }} />
          {s.alcaldia}
        </li>
      ))}
    </ul>
  );
}

/** Quarterly lines: soft grid, area under the first series, value labels at the end of each line. */
export function Lineas({ series }: { series: SerieAlcaldia[] }) {
  const W = 340;
  const H = 150;
  const P = { l: 38, r: 46, t: 12, b: 24 };
  const valores = series.flatMap((s) => s.puntos.map((p) => p.valor));
  if (valores.length === 0) return <p className="text-(--pb-texto-2)">Sin datos todavía.</p>;
  const max = Math.max(...valores);
  const min = Math.min(...valores);
  const pad = Math.max(1, (max - min) * 0.15);
  const [y0, y1] = [min - pad, max + pad];
  const n = Math.max(1, (series[0]?.puntos.length ?? 1) - 1);
  const x = (i: number) => P.l + (i / n) * (W - P.l - P.r);
  const y = (v: number) => P.t + (1 - (v - y0) / (y1 - y0)) * (H - P.t - P.b);
  const periodos = series[0]?.puntos.map((p) => p.periodo) ?? [];
  const marcas = [0, Math.round(n / 2), n];
  const guias = [y0 + (y1 - y0) * 0.2, (y0 + y1) / 2, y1 - (y1 - y0) * 0.2];
  // End labels: keep them at least 16 px apart so two close values never overlap.
  const etiquetasY = series.map((s) => y(s.puntos.at(-1)?.valor ?? 0));
  const orden = etiquetasY.map((v, i) => [v, i] as const).sort((a, b) => a[0] - b[0]);
  for (let k = 1; k < orden.length; k++) {
    const [prev] = orden[k - 1];
    if (orden[k][0] - prev < 16) orden[k] = [prev + 16, orden[k][1]];
  }
  orden.forEach(([v, i]) => (etiquetasY[i] = v));
  const resumen = series
    .map((s) => `${s.alcaldia}: de ${fmt(s.puntos[0]?.valor ?? 0)} a ${fmt(s.puntos.at(-1)?.valor ?? 0)}`)
    .join("; ");

  return (
    <figure className="flex flex-col gap-2">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${periodos[0]} a ${periodos.at(-1)}. ${resumen}`}>
        <defs>
          <linearGradient id="pb-area" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="var(--pb-acento)" stopOpacity="0.18" />
            <stop offset="100%" stopColor="var(--pb-acento)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {guias.map((g) => (
          <g key={g}>
            <line x1={P.l} x2={W - P.r} y1={y(g)} y2={y(g)} stroke="var(--pb-borde)" strokeDasharray="3 5" />
            <text x={P.l - 8} y={y(g) + 4} textAnchor="end" className="fill-(--pb-texto-2) text-[14px]">
              {fmt(Math.round(g))}
            </text>
          </g>
        ))}
        {series[0] && (
          <path
            d={`M ${x(0)} ${H - P.b} ${series[0].puntos.map((p, i) => `L ${x(i)} ${y(p.valor)}`).join(" ")} L ${x(n)} ${H - P.b} Z`}
            fill="url(#pb-area)"
          />
        )}
        {series.map((s, i) => {
          const ultimo = s.puntos.at(-1);
          return (
            <g key={s.alcaldia_cvegeo}>
              <polyline
                fill="none"
                stroke={COLORES[i % 2]}
                strokeWidth="3"
                strokeLinejoin="round"
                strokeLinecap="round"
                points={s.puntos.map((p, j) => `${x(j)},${y(p.valor)}`).join(" ")}
              />
              {ultimo && (
                <>
                  <circle cx={x(n)} cy={y(ultimo.valor)} r="5" fill="var(--pb-superficie)" stroke={COLORES[i % 2]} strokeWidth="3" />
                  <text x={x(n) + 10} y={etiquetasY[i] + 5} className="text-[15px] font-semibold" fill={COLORES[i % 2]}>
                    {fmt(ultimo.valor)}
                  </text>
                </>
              )}
            </g>
          );
        })}
        {marcas.map((m) => (
          <text key={m} x={x(m)} y={H - 6} textAnchor={m === 0 ? "start" : m === n ? "end" : "middle"} className="fill-(--pb-texto-2) text-[14px]">
            {periodos[m]}
          </text>
        ))}
      </svg>
      <Leyenda series={series} />
    </figure>
  );
}

/** Grouped bars per year with the latest year's values written on top. */
export function Barras({ series }: { series: SerieAlcaldia[] }) {
  const W = 340;
  const H = 150;
  const P = { l: 4, r: 4, t: 22, b: 24 };
  const periodos = series[0]?.puntos.map((p) => p.periodo) ?? [];
  if (periodos.length === 0) return <p className="text-(--pb-texto-2)">Sin datos todavía.</p>;
  const max = Math.max(1, ...series.flatMap((s) => s.puntos.map((p) => p.valor)));
  const grupo = (W - P.l - P.r) / periodos.length;
  const ancho = Math.min(18, (grupo * 0.7) / Math.max(1, series.length));
  const alto = (v: number) => (v / max) * (H - P.t - P.b);
  const resumen = series.map((s) => `${s.alcaldia}: ${s.puntos.map((p) => `${p.periodo} ${fmt(p.valor)}`).join(", ")}`).join(". ");

  return (
    <figure className="flex flex-col gap-2">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={resumen}>
        <line x1={P.l} x2={W - P.r} y1={H - P.b} y2={H - P.b} stroke="var(--pb-borde-fuerte)" />
        {periodos.map((periodo, j) => {
          const cx = P.l + grupo * j + grupo / 2;
          const ultimo = j === periodos.length - 1;
          return (
            <g key={periodo}>
              {series.map((s, i) => {
                const v = s.puntos[j]?.valor ?? 0;
                const bx = cx - (series.length * ancho) / 2 + i * ancho;
                return (
                  <g key={s.alcaldia_cvegeo}>
                    <rect x={bx + 1} y={H - P.b - alto(v)} width={ancho - 2} height={alto(v)} rx="4" fill={COLORES[i % 2]} opacity={ultimo ? 1 : 0.55}>
                      <title>{`${s.alcaldia} ${periodo}: ${fmt(v)}`}</title>
                    </rect>
                    {ultimo && (
                      <text x={bx + ancho / 2} y={H - P.b - alto(v) - 6} textAnchor="middle" className="text-[14px] font-semibold" fill={COLORES[i % 2]}>
                        {fmt(v)}
                      </text>
                    )}
                  </g>
                );
              })}
              <text x={cx} y={H - 7} textAnchor="middle" className={`text-[14px] ${ultimo ? "fill-(--pb-texto) font-semibold" : "fill-(--pb-texto-2)"}`}>
                {ultimo ? periodo : `'${periodo.slice(-2)}`}
              </text>
            </g>
          );
        })}
      </svg>
      <Leyenda series={series} />
    </figure>
  );
}

// Schematic CDMX: the 16 alcaldías as hexagons, roughly in their geographic place (north at the top).
const ALCALDIAS_MAPA: { nombre: string; corto: string; fila: number; col: number }[] = [
  { nombre: "Azcapotzalco", corto: "AZC", fila: 0, col: 1 },
  { nombre: "Gustavo A. Madero", corto: "GAM", fila: 0, col: 2 },
  { nombre: "Miguel Hidalgo", corto: "MH", fila: 1, col: 1 },
  { nombre: "Cuauhtémoc", corto: "CUH", fila: 1, col: 2 },
  { nombre: "Venustiano Carranza", corto: "VC", fila: 1, col: 3 },
  { nombre: "Cuajimalpa", corto: "CUJ", fila: 2, col: 0 },
  { nombre: "Álvaro Obregón", corto: "AO", fila: 2, col: 1 },
  { nombre: "Benito Juárez", corto: "BJ", fila: 2, col: 2 },
  { nombre: "Iztacalco", corto: "IZC", fila: 2, col: 3 },
  { nombre: "La Magdalena Contreras", corto: "MC", fila: 3, col: 0 },
  { nombre: "Coyoacán", corto: "COY", fila: 3, col: 1 },
  { nombre: "Iztapalapa", corto: "IZP", fila: 3, col: 2 },
  { nombre: "Tlalpan", corto: "TLP", fila: 4, col: 1 },
  { nombre: "Xochimilco", corto: "XOC", fila: 4, col: 2 },
  { nombre: "Tláhuac", corto: "TLH", fila: 4, col: 3 },
  { nombre: "Milpa Alta", corto: "MA", fila: 5, col: 2 },
];

export function MapaAlcaldias({ activas }: { activas: string[] }) {
  const r = 26;
  const w = Math.sqrt(3) * r;
  const h = 1.5 * r;
  const punto = (fila: number, col: number) => [w / 2 + 6 + col * w + (fila % 2 ? w / 2 : 0), r + 4 + fila * h];
  const hexagono = (cx: number, cy: number) =>
    Array.from({ length: 6 }, (_, k) => {
      const a = (Math.PI / 180) * (60 * k - 90);
      return `${cx + (r - 1.5) * Math.cos(a)},${cy + (r - 1.5) * Math.sin(a)}`;
    }).join(" ");
  const encendida = (nombre: string) => activas.some((a) => a.localeCompare(nombre, "es", { sensitivity: "base" }) === 0);
  const ancho = w * 4.5 + 12;
  const alto = r * 2 + h * 5 + 8;

  return (
    <svg
      viewBox={`0 0 ${ancho} ${alto}`}
      className="h-auto w-44 shrink-0"
      role="img"
      aria-label={`Las 16 alcaldías de la CDMX. Activas hoy: ${activas.join(" e ")}.`}
    >
      {ALCALDIAS_MAPA.map((a) => {
        const [cx, cy] = punto(a.fila, a.col);
        const on = encendida(a.nombre);
        return (
          <g key={a.nombre}>
            <title>{`${a.nombre}${on ? " · activa" : " · siguiente fase"}`}</title>
            <polygon
              points={hexagono(cx, cy)}
              fill={on ? "var(--pb-acento)" : "var(--pb-superficie-2)"}
              stroke={on ? "var(--pb-acento-fuerte)" : "var(--pb-borde)"}
              strokeWidth="1.5"
            />
            <text x={cx} y={cy + 4} textAnchor="middle" className={`text-[15px] font-bold ${on ? "fill-white" : "fill-(--pb-texto-2)"}`}>
              {a.corto}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
