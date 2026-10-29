// View model for the Negocio screen. Accepts both shapes seen so far:
// the PB-002 contract (web/src/lib/types.ts NegocioDetalle) and the PB-009 backend (app/services/negocio.py).
// normalizar.ts maps either into this. Swap to web/src/lib/types.ts once PB-002 lands on main.

export type TipoDato = "real" | "estimado" | "simulado";
export type EstadoPrograma = "existe" | "por_verificar" | "propuesta";
export type EstadoEscalon = "logrado" | "siguiente" | "pendiente" | "proximamente" | "horizonte";

export type Cifra = {
  valor: number | null;
  tipo_dato: TipoDato;
  fuente: string | null;
};

export type ProductoVista = { nombre: string; precio: number | null; unidad: string | null };

export type FichaVista = {
  nombre: string;
  giro: string | null;
  descripcion: string | null;
  colonia: string | null;
  horario: string | null;
  productos: ProductoVista[];
  formas_pago: string[];
  acepta_mercomuna: boolean | null;
  ubicacion: "exacta" | "aproximada" | null;
  aparecer_en_rutas: boolean | null;
  whatsapp: boolean;
};

export type AvanceVista = {
  tipo_dato: TipoDato;
  periodo: string;
  nota: string | null;
  apariciones_ruta: Cifra;
  compre_aqui: Cifra;
  vistas_pagina: Cifra;
  busquedas: Cifra | null;
  promedio_zona_apariciones: Cifra | null;
};

export type EscalonVista = {
  numero: number;
  nombre: string;
  estado: EstadoEscalon;
  beneficio: string;
  siguiente_accion: string | null;
};

export type ProgramaVista = {
  id: string;
  nombre: string;
  que_es: string;
  como_entrar: string | null;
  url_oficial: string | null;
  estado: EstadoPrograma;
  puede_entrar: boolean | null;
  motivo: string | null;
};

export type PaginaVista = {
  slug: string | null;
  url: string;
  cartel: string;
  qr: string | null;
};

export type NegocioVista = {
  id: string;
  ficha: FichaVista;
  avance: AvanceVista;
  escalera: EscalonVista[];
  programas: ProgramaVista[];
  pagina: PaginaVista | null;
  demo_data: boolean;
};
