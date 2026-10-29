// Puntos por tipo y alcaldías (GET /api/puntos y /api/alcaldias, CO-012).
// TODO CO-007: cuando web/src/lib/map/iconos.ts y ChipsTipo.tsx estén en main, sustituir este adaptador.
import { api } from "../../lib/api";
import type { TipoDato } from "./datos";

export type TipoPunto = "tianguis" | "mercado" | "negocio_local";

export const TIPOS: { id: TipoPunto; etiqueta: string; glifo: string; color: string }[] = [
  { id: "tianguis", etiqueta: "Tianguis", glifo: "●", color: "#c2410c" },
  { id: "mercado", etiqueta: "Mercado", glifo: "■", color: "#0e5c58" },
  { id: "negocio_local", etiqueta: "Negocio local", glifo: "▲", color: "#4338ca" },
];

export type PuntoMapa = {
  id: string;
  tipo: TipoPunto;
  nombre: string | null;
  alcaldia_cvegeo: string;
  lat: number;
  lng: number;
  tipo_dato: TipoDato;
  fuente: string;
};

export type AlcaldiaInfo = {
  cvegeo: string;
  nombre: string;
  prioridad: boolean;
  puntos_por_tipo: Record<string, number>;
  tipo_dato: TipoDato;
  fuente: string;
  cnbv: { trimestre: string | null; tpv_por_adulto: number | null; tipo_dato: TipoDato; fuente: string } | null;
};

type RespuestaPuntos = { puntos: PuntoMapa[]; total: number; truncado: boolean };

const PRIORITARIAS = ["09003", "09007"];

export async function cargarAlcaldiasInfo(): Promise<AlcaldiaInfo[]> {
  try {
    return await api<AlcaldiaInfo[]>("/alcaldias");
  } catch {
    return [];
  }
}

async function pedir(tipos: TipoPunto[], alcaldia: string): Promise<PuntoMapa[]> {
  try {
    const r = await api<RespuestaPuntos>(`/puntos?tipo=${tipos.join(",")}&alcaldia=${alcaldia}`);
    return r.puntos;
  } catch {
    return [];
  }
}

/** Pide primero 09003 y 09007 (se pintan al llegar) y después el resto en segundo plano. */
export async function cargarPuntosProgresivo(
  tipos: TipoPunto[],
  todas: string[],
  alLlegar: (nuevos: PuntoMapa[]) => void,
  vivo: () => boolean,
): Promise<void> {
  if (!tipos.length) return;
  for (const cve of PRIORITARIAS) {
    const p = await pedir(tipos, cve);
    if (!vivo()) return;
    alLlegar(p);
  }
  const resto = todas.filter((c) => !PRIORITARIAS.includes(c));
  await Promise.all(
    resto.map(async (cve) => {
      const p = await pedir(tipos, cve);
      if (vivo()) alLlegar(p);
    }),
  );
}
