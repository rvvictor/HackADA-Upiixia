import { api } from "../../lib/api";
import { ofertaNuevaMock, ofertasMock, sesionMock } from "./mock";
import type { Oferta, Sesion } from "./tipos";

// Cliente de IDEA-v2.md §8 con modo mock automático si la API aún no existe (404, red o respuesta no JSON).
let mock = false;
let sondeos = 0;
let locales: Oferta[] = [];

export const enModoMock = () => mock;

export class CodigoInvalido extends Error {}

function sinApi(e: unknown): boolean {
  if (e instanceof TypeError || e instanceof SyntaxError) return true;
  return e instanceof Error && /^(404|405|500|502|503|504)\b/.test(e.message);
}

function cabeceras(token?: string): HeadersInit {
  return token && token !== "mock" ? { "Content-Type": "application/json", Authorization: `Bearer ${token}` } : { "Content-Type": "application/json" };
}

// Entrada solo con el número de repartidor (CO-026): la API abre sesión si el número existe.
export async function iniciarSesion(id: string): Promise<Sesion> {
  try {
    const s = await api<Sesion>("/repartidores/sesion", { method: "POST", body: JSON.stringify({ id }) });
    mock = false;
    return { ...s, repartidor_id: s.repartidor_id ?? id };
  } catch (e) {
    if (sinApi(e)) {
      mock = true;
      sondeos = 0;
      locales = ofertasMock();
      return sesionMock(id);
    }
    throw new CodigoInvalido("Ese número de repartidor no está registrado.");
  }
}

export async function listarOfertas(s: Sesion): Promise<Oferta[]> {
  if (mock) {
    sondeos += 1;
    if (sondeos === 3 && !locales.some((o) => o.id === "O-DEMO3")) locales = [...locales, ofertaNuevaMock()];
    return locales;
  }
  const r = await api<Oferta[] | { ofertas: Oferta[] }>(`/ofertas?repartidor_id=${encodeURIComponent(s.repartidor_id)}`, {
    headers: cabeceras(s.token),
  });
  return Array.isArray(r) ? r : r.ofertas;
}

async function cambiar(s: Sesion, id: string, accion: "tomar" | "completar"): Promise<void> {
  if (mock) {
    const estado = accion === "tomar" ? "tomada" : "completada";
    locales = locales.map((o) => (o.id === id ? { ...o, estado, repartidor_id: s.repartidor_id } : o));
    return;
  }
  await api(`/ofertas/${encodeURIComponent(id)}/${accion}`, {
    method: "POST",
    headers: cabeceras(s.token),
    body: JSON.stringify({ repartidor_id: s.repartidor_id }),
  });
}

export const tomarOferta = (s: Sesion, id: string) => cambiar(s, id, "tomar");
export const completarOferta = (s: Sesion, id: string) => cambiar(s, id, "completar");
