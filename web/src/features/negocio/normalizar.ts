import type {
  AvanceVista,
  Cifra,
  EscalonVista,
  EstadoEscalon,
  EstadoPrograma,
  FichaVista,
  NegocioVista,
  PaginaVista,
  ProgramaVista,
  TipoDato,
} from "./tipos";

// The backend shape is still moving (PB-002 contract vs PB-009). Read defensively: never crash the demo.
type Crudo = Record<string, unknown>;

const obj = (v: unknown): Crudo => (v && typeof v === "object" && !Array.isArray(v) ? (v as Crudo) : {});
const str = (v: unknown): string | null => (typeof v === "string" && v.trim() ? v : null);
const num = (v: unknown): number | null => (typeof v === "number" && Number.isFinite(v) ? v : null);
const bool = (v: unknown): boolean | null => (typeof v === "boolean" ? v : null);
const arr = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);

function tipo(v: unknown, def: TipoDato = "simulado"): TipoDato {
  return v === "real" || v === "estimado" || v === "simulado" ? v : def;
}

const FUENTE_PLATAFORMA = "Pulso Barrial (eventos de la plataforma)";
const FUENTE_SIMULADA = "Historia simulada de la plataforma";

function cifra(v: unknown, tipoGeneral: TipoDato): Cifra | null {
  if (typeof v === "number") {
    return { valor: v, tipo_dato: tipoGeneral, fuente: tipoGeneral === "simulado" ? FUENTE_SIMULADA : FUENTE_PLATAFORMA };
  }
  const o = obj(v);
  if (!("valor" in o)) return null;
  const t = tipo(o.tipo_dato, tipoGeneral);
  return { valor: num(o.valor), tipo_dato: t, fuente: str(o.fuente) ?? (t === "simulado" ? FUENTE_SIMULADA : FUENTE_PLATAFORMA) };
}

const vacia = (t: TipoDato): Cifra => ({ valor: null, tipo_dato: t, fuente: null });

function avance(v: unknown): AvanceVista {
  const a = obj(v);
  const t = tipo(a.tipo_dato);
  const conteos = obj(a.conteos);
  const usaConteos = Object.keys(conteos).length > 0;
  const fuente = usaConteos ? conteos : a;
  const dias = num(a.dias);
  return {
    tipo_dato: t,
    periodo: dias ? `últimos ${dias} días` : "últimos 7 días",
    nota: str(a.nota),
    apariciones_ruta: cifra(fuente.apariciones_ruta ?? fuente.rutas, t) ?? vacia(t),
    compre_aqui: cifra(fuente.compre_aqui, t) ?? vacia(t),
    vistas_pagina: cifra(fuente.vistas_pagina ?? fuente.visitas_pagina, t) ?? vacia(t),
    busquedas: cifra(fuente.busquedas, t),
    promedio_zona_apariciones: cifra(a.promedio_zona_apariciones, t),
  };
}

function ficha(v: unknown, descripcionTop: unknown): FichaVista {
  const f = obj(v);
  const abre = str(f.abre);
  const cierra = str(f.cierra);
  const ubic = f.ubicacion === "exacta" || f.ubicacion === "aproximada" ? f.ubicacion : null;
  return {
    nombre: str(f.nombre) ?? "Negocio sin nombre",
    giro: str(f.giro) ?? str(f.clase_nombre),
    descripcion: str(f.descripcion) ?? str(descripcionTop),
    colonia: str(f.colonia),
    horario: str(f.horario) ?? (abre && cierra ? `de ${abre} a ${cierra}` : null),
    productos: arr(f.productos).map((p) => {
      const o = obj(p);
      return { nombre: str(o.nombre) ?? "producto", precio: num(o.precio), unidad: str(o.unidad) };
    }),
    formas_pago: arr(f.formas_pago).filter((x): x is string => typeof x === "string"),
    acepta_mercomuna: bool(f.acepta_mercomuna),
    ubicacion: ubic,
    aparecer_en_rutas: bool(f.aparecer_en_rutas),
    whatsapp: Boolean(str(f.whatsapp) ?? str(f.telefono)),
  };
}

const ESTADOS_ESCALON: EstadoEscalon[] = ["logrado", "siguiente", "pendiente", "proximamente", "horizonte"];

function escalera(v: unknown): EscalonVista[] {
  return arr(v)
    .map((e, i) => {
      const o = obj(e);
      const estado = ESTADOS_ESCALON.includes(o.estado as EstadoEscalon) ? (o.estado as EstadoEscalon) : "pendiente";
      return {
        numero: num(o.numero) ?? num(o.orden) ?? i + 1,
        nombre: str(o.nombre) ?? `Escalón ${i + 1}`,
        estado,
        beneficio: str(o.beneficio) ?? "",
        siguiente_accion: str(o.siguiente_accion),
      };
    })
    .sort((a, b) => a.numero - b.numero);
}

function programas(v: unknown): ProgramaVista[] {
  return arr(v).map((p, i) => {
    const o = obj(p);
    const estado: EstadoPrograma =
      o.estado === "existe" || o.estado === "propuesta" || o.estado === "por_verificar" ? o.estado : "por_verificar";
    return {
      id: str(o.id) ?? `programa-${i}`,
      nombre: str(o.nombre) ?? "Programa",
      que_es: str(o.que_es) ?? "",
      como_entrar: str(o.como_entrar),
      url_oficial: str(o.url_oficial),
      estado,
      puede_entrar: bool(o.puede_entrar),
      motivo: str(o.motivo),
    };
  });
}

export function pagina(v: unknown): PaginaVista | null {
  const o = obj(v);
  const url = str(o.url);
  if (!url) return null;
  return {
    slug: str(o.slug),
    url,
    cartel: str(o.cartel) ?? str(o.cartel_url) ?? `${url}/cartel`,
    qr: str(o.qr) ?? str(o.qr_data_uri),
  };
}

export function normalizar(v: unknown, demo = false): NegocioVista {
  const n = obj(v);
  return {
    id: str(n.id) ?? "",
    ficha: ficha(n.ficha, n.descripcion),
    avance: avance(n.avance),
    escalera: escalera(n.escalera),
    programas: programas(n.programas),
    pagina: pagina(n.pagina),
    demo_data: demo || n.demo_data === true,
  };
}
