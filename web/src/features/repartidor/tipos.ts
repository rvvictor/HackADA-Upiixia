import type { TipoDato } from "../../lib/ui";

export type Transporte = "bici" | "bici_electrica" | "a_pie" | "scooter_electrico" | "moto" | "auto";

export const ECOLOGICOS: Transporte[] = ["bici", "bici_electrica", "a_pie", "scooter_electrico"];

export type Parada = { lat: number; lng: number; h3?: string; colonia: string };

// Campos de IDEA-v2.md §7. La prioridad y la foto de ID nunca llegan a esta vista.
export type Oferta = {
  id: string;
  ts: string;
  negocio_id: string;
  negocio_nombre?: string;
  tipo_negocio: string;
  origen?: { lat: number; lng: number };
  paradas: Parada[];
  distancia_m: number;
  minutos_est: number;
  pago_est: number;
  tipo_dato_pago: TipoDato;
  colonia: string;
  estado: "abierta" | "tomada" | "completada" | "cancelada";
  repartidor_id?: string;
  demo_data?: boolean;
};

export type Sesion = {
  token: string;
  repartidor_id: string;
  nombre_mostrar?: string;
  transporte?: Transporte;
  demo_data?: boolean;
};
