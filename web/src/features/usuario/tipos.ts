// Shape of POST /api/ruta (PB-007). Local until web/src/lib/types.ts (PB-002) lands on main.
import type { TipoDato } from "../../lib/ui";

export type NegocioParada = {
  id: string;
  nombre: string;
  tipo: "negocio" | "tianguis" | "mercado" | "alta";
  giro: string;
  lat: number;
  lng: number;
  h3: string | null;
  formas_pago: string[];
  acepta_mercomuna: boolean | null;
  tipo_dato: TipoDato;
  impulso: number;
};

export type Parada = {
  orden: number;
  negocio: NegocioParada;
  articulos: string[];
  por_que: string[];
};

export type Ruta = {
  paradas: Parada[];
  geometria: { type: "LineString"; coordinates: [number, number][] } | null;
  distancia_m: number;
  minutos: number;
  resumen: { barrial_pct: number; cadenas: number; paradas_impulso: number };
  sin_resultado: string[];
  aviso: string | null;
  demo_data: boolean;
};

export type Punto = { lat: number; lng: number };
