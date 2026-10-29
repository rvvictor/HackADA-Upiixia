// Datos de la vista SEDECO: tipos (nombres de campo de la API y de data/processed/*),
// llamadas con respaldo a datos de ejemplo, y cálculos de cobertura en el navegador.
import { cellToBoundary, gridDisk, latLngToCell } from "h3-js";
import * as turf from "@turf/turf";
import { api } from "../../lib/api";

export type TipoDato = "real" | "estimado" | "simulado";
export type Origen = "api" | "ejemplo";
export type CapaHex = "actividad" | "oferta" | "poblacion" | "impulso";
export type Campo = "poblacion" | "negocios_barriales" | "negocios_total" | "actividad_tpv_est" | "impulso";

export type PropsHex = {
  h3: string;
  alcaldia_cvegeo: string;
  poblacion: number | null;
  negocios_barriales: number | null;
  negocios_total: number | null;
  actividad_tpv_est: number | null;
  impulso: number | null;
  cluster_id: string | number | null;
  oculto: boolean;
  tipo_campos: Partial<Record<Campo, TipoDato>>;
  periodo_cnbv: string | null;
  // Normalizados 0–1 para la altura del 3D (se calculan al cargar).
  n_actividad?: number;
  n_negocios?: number;
  n_poblacion?: number;
};

export type HexFeature = {
  type: "Feature";
  geometry: { type: "Polygon"; coordinates: number[][][] };
  properties: PropsHex;
};
export type ColeccionHex = { type: "FeatureCollection"; features: HexFeature[] };

export type Tianguis = {
  id: string;
  nombre: string;
  tipo: string;
  alcaldia_cvegeo: string;
  colonia: string | null;
  lat: number;
  lng: number;
  dias: number[]; // 0 = lunes … 6 = domingo
  abre: string; // "HH:MM"
  cierra: string;
  tipo_dato: TipoDato;
  fuente: string;
};

export type Alcaldia = {
  cvegeo: string;
  municipio: string;
  trimestre: string;
  transacciones_tpv: number;
  adultos: number;
  tpv_por_adulto: number;
  tipo_dato: TipoDato;
  fuente_url: string | null;
};

export type Alta = {
  id: string;
  ts: number;
  lat?: number;
  lng?: number;
  ficha?: { nombre?: string; lat?: number; lng?: number };
};

type Dato<T> = { valor: T; tipo_dato: TipoDato; fuente: string; periodo: string };
export type Resumen = {
  altas_hoy?: Dato<number>;
  poblacion_cubierta_pct?: Dato<number>;
};

export const DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"];
export const NOMBRE_ALCALDIA: Record<string, string> = { "09003": "Coyoacán", "09007": "Iztapalapa" };
export const ETIQUETA_TIPO: Record<TipoDato, string> = { real: "Dato real", estimado: "Estimado", simulado: "Simulado" };

/** Día de hoy en la escala 0 = lunes … 6 = domingo. */
export function diaHoy(): number {
  return (new Date().getDay() + 6) % 7;
}

const aMinutos = (hora: string) => {
  const [h, m] = hora.split(":").map(Number);
  return h * 60 + (m || 0);
};

/** Un tianguis está abierto si su lista de días incluye el día y la hora cae en [abre, cierra). */
export function estaAbierto(t: Tianguis, dia: number, hora: number): boolean {
  const minuto = hora * 60;
  return t.dias.includes(dia) && minuto >= aMinutos(t.abre) && minuto < aMinutos(t.cierra);
}

// ---------- Llamadas con respaldo ----------

export async function cargarHex(): Promise<{ data: ColeccionHex; origen: Origen }> {
  try {
    const data = await api<ColeccionHex>("/hex");
    if (!data?.features?.length) throw new Error("vacío");
    return { data: normalizarHex(data), origen: "api" };
  } catch {
    return { data: normalizarHex(hexEjemplo()), origen: "ejemplo" };
  }
}

export async function cargarTianguis(dia: number, hora: number): Promise<{ lista: Tianguis[]; origen: Origen }> {
  const horaTxt = `${String(hora).padStart(2, "0")}:00`;
  try {
    // PB-006 responde {dia, hora, abiertos, puntos[{..., abierto}], cobertura}; se acepta también una lista simple.
    const r = await api<Tianguis[] | { puntos: (Tianguis & { abierto?: boolean })[] }>(
      `/tianguis?dia=${dia}&hora=${encodeURIComponent(horaTxt)}`,
    );
    const lista = Array.isArray(r) ? r : r.puntos.filter((p) => p.abierto !== false);
    return { lista, origen: "api" };
  } catch {
    return { lista: TIANGUIS_EJEMPLO, origen: "ejemplo" };
  }
}

export async function cargarAlcaldias(): Promise<{ lista: Alcaldia[]; origen: Origen }> {
  try {
    const lista = await api<Alcaldia[]>("/dinero/alcaldias");
    if (!lista?.length) throw new Error("vacío");
    return { lista, origen: "api" };
  } catch {
    return { lista: ALCALDIAS_EJEMPLO, origen: "ejemplo" };
  }
}

/** Resumen del servidor si existe; si no, null y la vista calcula la cobertura en el navegador. */
export async function cargarResumen(dia: number, hora: number): Promise<Resumen | null> {
  try {
    // PB-006 manda números sueltos y su tipo en tipo_campos; aquí se vuelven Dato<number>.
    const r = await api<Record<string, unknown> & { tipo_campos?: Record<string, TipoDato> }>(
      `/sedeco/resumen?dia=${dia}&hora=${String(hora).padStart(2, "0")}:00`,
    );
    const dato = (clave: string): Dato<number> | undefined => {
      const v = r[clave];
      if (typeof v === "number") return { valor: v, tipo_dato: r.tipo_campos?.[clave] ?? "estimado", fuente: "Pulso Barrial", periodo: "hoy" };
      return (v as Dato<number> | undefined) ?? undefined;
    };
    return { altas_hoy: dato("altas_hoy"), poblacion_cubierta_pct: dato("poblacion_cubierta_pct") };
  } catch {
    return null;
  }
}

/** Altas nuevas desde `desde` (segundos). Falla en silencio (404 incluido). */
export async function cargarAltas(desde: number): Promise<{ ts: number; altas: Alta[] } | null> {
  try {
    // PB-008 responde {altas, desde, ultimo_ts}.
    const r = await api<{ altas: Alta[]; ts?: number; ultimo_ts?: number }>(`/altas/live?desde=${desde}`);
    return { ts: r.ts ?? r.ultimo_ts ?? desde, altas: r.altas ?? [] };
  } catch {
    return null;
  }
}

// ---------- Cobertura: 800 m alrededor de cada tianguis abierto ----------

/** Porcentaje de población cuyo centroide de hexágono cae a menos de 800 m de un tianguis abierto. */
export function calcularCobertura(hex: ColeccionHex, abiertos: Tianguis[]): number {
  const total = hex.features.reduce((s, f) => s + (f.properties.poblacion ?? 0), 0);
  if (!total || !abiertos.length) return 0;
  const zonas = abiertos.flatMap((t) => {
    const z = turf.buffer(turf.point([t.lng, t.lat]), 0.8, { units: "kilometers", steps: 16 });
    return z ? [z] : [];
  });
  let cubierta = 0;
  for (const f of hex.features) {
    const centro = turf.centroid(f);
    if (zonas.some((z) => turf.booleanPointInPolygon(centro, z))) {
      cubierta += f.properties.poblacion ?? 0;
    }
  }
  return Math.round((cubierta / total) * 1000) / 10;
}

// ---------- Normalización para el 3D ----------

function normalizarHex(c: ColeccionHex): ColeccionHex {
  const max = (fn: (p: PropsHex) => number | null) => Math.max(1e-9, ...c.features.map((f) => fn(f.properties) ?? 0));
  const mA = max((p) => p.actividad_tpv_est);
  const mN = max((p) => p.negocios_barriales);
  const mP = max((p) => p.poblacion);
  return {
    ...c,
    features: c.features.map((f) => ({
      ...f,
      properties: {
        ...f.properties,
        n_actividad: (f.properties.actividad_tpv_est ?? 0) / mA,
        n_negocios: (f.properties.negocios_barriales ?? 0) / mN,
        n_poblacion: (f.properties.poblacion ?? 0) / mP,
      },
    })),
  };
}

// ---------- Datos de ejemplo (solo si la API no responde) ----------

function ruido(texto: string): number {
  let h = 2166136261;
  for (const ch of texto) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return (h >>> 0) / 4294967295;
}

function hexEjemplo(): ColeccionHex {
  const centros: [number, number, string][] = [
    [19.3467, -99.1617, "09003"], // Coyoacán
    [19.3572, -99.0654, "09007"], // Iztapalapa
  ];
  const features: HexFeature[] = [];
  const vistos = new Set<string>();
  for (const [lat, lng, cve] of centros) {
    for (const celda of gridDisk(latLngToCell(lat, lng, 9), 7)) {
      if (vistos.has(celda)) continue;
      vistos.add(celda);
      const anillo = cellToBoundary(celda, true) as number[][];
      const r = ruido(celda);
      const negocios = Math.floor(r * 40);
      const oculto = negocios < 3;
      features.push({
        type: "Feature",
        geometry: { type: "Polygon", coordinates: [anillo] },
        properties: {
          h3: celda,
          alcaldia_cvegeo: cve,
          poblacion: Math.round(800 + ruido(celda + "p") * 3000),
          negocios_barriales: Math.floor(negocios * 0.4),
          negocios_total: negocios,
          actividad_tpv_est: oculto ? null : Math.round((negocios * (0.5 + ruido(celda + "a"))) * 100) / 100,
          impulso: oculto ? null : Math.round(ruido(celda + "i") * 1000) / 1000,
          cluster_id: null,
          oculto,
          tipo_campos: { poblacion: "simulado", negocios_barriales: "simulado", negocios_total: "simulado", actividad_tpv_est: "estimado", impulso: "estimado" },
          periodo_cnbv: "2023-T2",
        },
      });
    }
  }
  return { type: "FeatureCollection", features };
}

const TIANGUIS_EJEMPLO: Tianguis[] = [
  { id: "ej-1", nombre: "Tianguis de ejemplo · Santa Catarina", tipo: "tianguis", alcaldia_cvegeo: "09003", colonia: "Santa Catarina", lat: 19.3336, lng: -99.1468, dias: [0, 1, 2, 3, 4, 5], abre: "07:00", cierra: "18:00", tipo_dato: "simulado", fuente: "Ejemplo" },
  { id: "ej-2", nombre: "Tianguis de ejemplo · Churubusco", tipo: "tianguis", alcaldia_cvegeo: "09003", colonia: "Churubusco", lat: 19.3532, lng: -99.142, dias: [1, 3], abre: "08:00", cierra: "16:00", tipo_dato: "simulado", fuente: "Ejemplo" },
  { id: "ej-3", nombre: "Tianguis de ejemplo · Coyoacán centro", tipo: "tianguis", alcaldia_cvegeo: "09003", colonia: "Coyoacán", lat: 19.35, lng: -99.162, dias: [5, 6], abre: "08:00", cierra: "17:00", tipo_dato: "simulado", fuente: "Ejemplo" },
  { id: "ej-4", nombre: "Tianguis de ejemplo · Cabeza de Juárez", tipo: "tianguis", alcaldia_cvegeo: "09007", colonia: "Cabeza de Juárez", lat: 19.3514, lng: -99.0604, dias: [0, 2, 4], abre: "07:00", cierra: "15:00", tipo_dato: "simulado", fuente: "Ejemplo" },
  { id: "ej-5", nombre: "Tianguis de ejemplo · San Lorenzo Tezonco", tipo: "tianguis", alcaldia_cvegeo: "09007", colonia: "San Lorenzo Tezonco", lat: 19.3297, lng: -99.0716, dias: [1, 2, 3, 4, 5, 6], abre: "06:00", cierra: "14:00", tipo_dato: "simulado", fuente: "Ejemplo" },
  { id: "ej-6", nombre: "Tianguis de ejemplo · Ejército de Oriente", tipo: "tianguis", alcaldia_cvegeo: "09007", colonia: "Ejército de Oriente", lat: 19.3648, lng: -99.0773, dias: [6], abre: "07:00", cierra: "13:00", tipo_dato: "simulado", fuente: "Ejemplo" },
];

const ALCALDIAS_EJEMPLO: Alcaldia[] = [
  { cvegeo: "09003", municipio: "Coyoacán", trimestre: "2023-T2", transacciones_tpv: 9850000, adultos: 488000, tpv_por_adulto: 20.18, tipo_dato: "simulado", fuente_url: null },
  { cvegeo: "09007", municipio: "Iztapalapa", trimestre: "2023-T2", transacciones_tpv: 14200000, adultos: 1390000, tpv_por_adulto: 10.22, tipo_dato: "simulado", fuente_url: null },
];
