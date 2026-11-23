import { useState, type ReactNode } from "react";
import { CheckCircle, Crosshair, ShareNetwork, Storefront } from "@phosphor-icons/react";

import type { FeatureProps } from "../../App";
import { api } from "../../lib/api";
import { Boton, Chip } from "../../lib/ui";
import { LISTA_EJEMPLO, RUTA_EJEMPLO, SEDE } from "./ejemplo";
import { MapaRuta } from "./MapaRuta";
import type { Parada, Punto, Ruta } from "./tipos";

export const route = "usuario";
export const label = "Vecina";
export const order = 2;

// Recipe "flow" (web/DESIGN.md §6): three numbered steps on the left, the route drawn on the map on the right
// (below the list on phones). Text 18 px, controls 48 px. No real/simulado chips (uak decision CO-028).

type Estado = "vacio" | "cargando" | "listo" | "error";

const PAGO: Record<string, string> = {
  efectivo: "Efectivo",
  transferencia: "Transferencia",
  dimo: "DiMo",
  codi: "CoDi",
  tarjeta: "Tarjeta",
};

function km(metros: number): string {
  return metros >= 1000 ? `${(metros / 1000).toFixed(1)} km` : `${metros} m`;
}

// The API explains each stop with text like "(impulso 0.80, estimado)". The data type stays in the API; on screen
// we drop that parenthetical (uak decision CO-028: no real/estimado/simulado text).
function razonLimpia(razon: string): string {
  return razon.replace(/\s*\([^)]*\b(real|estimad[oa]|simulad[oa])\b[^)]*\)/gi, "").trim();
}

function textoWhatsApp(ruta: Ruta): string {
  const lineas = ruta.paradas.map((p) => `${p.orden}. ${p.negocio.nombre}: ${p.articulos.join(", ")}`);
  return `Mi ruta de compras de barrio (${km(ruta.distancia_m)} a pie, 0 cadenas):\n${lineas.join("\n")}\nHecha con colonIA`;
}

function Paso({ numero, titulo, activo, children }: { numero: number; titulo: string; activo: boolean; children?: ReactNode }) {
  return (
    <section aria-labelledby={`paso-${numero}`} className="flex gap-4">
      <span
        aria-hidden="true"
        className={`pb-display grid size-10 shrink-0 place-items-center rounded-full text-lg font-extrabold ${
          activo ? "bg-(--pb-acento) text-(--pb-sobre-acento)" : "bg-(--pb-superficie-2) text-(--pb-texto-2)"
        }`}
      >
        {numero}
      </span>
      <div className="min-w-0 flex-1 pt-1.5">
        <h2 id={`paso-${numero}`} className={`text-[1.25rem] font-semibold ${activo ? "" : "text-(--pb-texto-2)"}`}>
          <span className="sr-only">Paso {numero}: </span>
          {titulo}
        </h2>
        {children && <div className="mt-3">{children}</div>}
      </div>
    </section>
  );
}

export default function Usuario(_props: FeatureProps) {
  const [lista, setLista] = useState(LISTA_EJEMPLO);
  const [origen, setOrigen] = useState<Punto>(SEDE);
  const [usaUbicacion, setUsaUbicacion] = useState(false);
  const [estado, setEstado] = useState<Estado>("vacio");
  const [ruta, setRuta] = useState<Ruta | null>(null);
  const [esEjemplo, setEsEjemplo] = useState(false);
  const [compras, setCompras] = useState<Set<string>>(new Set());

  async function armar() {
    if (!lista.trim()) return;
    setEstado("cargando");
    setCompras(new Set());
    try {
      const r = await api<Ruta>("/ruta", { method: "POST", body: JSON.stringify({ origen, texto_lista: lista }) });
      setRuta(r);
      setEsEjemplo(false);
      setEstado("listo");
    } catch {
      // Sin API: mostrar la ruta de ejemplo, avisando que lo es, para que la demo no se caiga.
      setRuta(RUTA_EJEMPLO);
      setEsEjemplo(true);
      setEstado("error");
    }
  }

  function usarUbicacion() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setOrigen({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setUsaUbicacion(true);
      },
      () => setUsaUbicacion(false),
      { timeout: 6000 },
    );
  }

  async function compreAqui(p: Parada) {
    setCompras((prev) => new Set(prev).add(p.negocio.id));
    try {
      await api("/eventos", {
        method: "POST",
        body: JSON.stringify({ tipo: "compre_aqui", negocio_id: p.negocio.id, h3: p.negocio.h3 }),
      });
    } catch {
      // El registro es best effort; el botón ya confirmó al usuario.
    }
  }

  const hayRuta = !!ruta && estado !== "cargando";

  return (
    <div className="grid min-h-full lg:h-full lg:grid-cols-[30rem_minmax(0,1fr)]">
      <div className="flex min-h-0 flex-col gap-7 p-4 md:p-8 lg:overflow-y-auto">
        <header>
          <h1 className="pb-display text-[2.3rem] font-extrabold leading-tight md:text-[2.8rem]">Tu mandado, sin cadenas</h1>
          <p className="mt-2 text-lg text-(--pb-texto-2)">Una ruta a pie solo por tianguis, mercados y tienditas de tu barrio.</p>
        </header>

        <Paso numero={1} titulo="Escribe tu lista" activo={!hayRuta}>
          <label htmlFor="lista" className="sr-only">
            Tu lista del mandado
          </label>
          <textarea
            id="lista"
            value={lista}
            onChange={(e) => setLista(e.target.value)}
            rows={3}
            placeholder="2 kilos de jitomate, tortillas, tenis para niño…"
            className="w-full resize-none rounded-(--pb-radio-control) border-2 border-(--pb-borde-fuerte) bg-(--pb-superficie) p-3 text-lg leading-snug"
          />
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Boton tamano="lg" onClick={armar} disabled={estado === "cargando" || !lista.trim()}>
              {estado === "cargando" ? "Armando…" : "Armar mi ruta"}
            </Boton>
            <Boton variante="fantasma" icono={<Crosshair />} onClick={usarUbicacion}>
              Usar mi ubicación
            </Boton>
          </div>
          <p className="mt-2 text-base text-(--pb-texto-2)">
            {usaUbicacion ? "Salimos desde tu ubicación." : "Salimos desde la Utopía Elena Poniatowska, San Lucas, Coyoacán."}
          </p>
        </Paso>

        <Paso numero={2} titulo="Te armamos la ruta" activo={hayRuta}>
          {estado === "cargando" && (
            <div role="status" aria-label="Buscando en los negocios de tu barrio" className="flex flex-col gap-2">
              <div className="h-10 w-3/4 rounded-full bg-(--pb-superficie-2) motion-safe:animate-pulse" />
              <div className="h-10 w-1/2 rounded-full bg-(--pb-superficie-2) motion-safe:animate-pulse" />
            </div>
          )}
          {estado === "vacio" && <p className="text-lg text-(--pb-texto-2)">Aparece aquí y en el mapa en cuanto la armes.</p>}
          {hayRuta && ruta && (
            <div className="flex flex-col gap-3">
              {esEjemplo && (
                <p role="alert" className="rounded-(--pb-radio-control) bg-(--pb-superficie-2) px-4 py-3 text-lg">
                  No pudimos conectar con el servidor. Te mostramos una ruta de ejemplo.
                </p>
              )}
              <div>
                <p className="flex items-baseline gap-3">
                  <span className="pb-display pb-cifra text-[3rem] font-extrabold leading-none text-(--pb-acento-fuerte)">0</span>
                  <span className="text-xl font-semibold">cadenas</span>
                </p>
                <p className="mt-1 text-lg text-(--pb-texto-2)">
                  {km(ruta.distancia_m)} a pie, {ruta.minutos} min, {ruta.paradas.length} paradas
                </p>
              </div>
              {ruta.resumen.paradas_impulso > 0 && (
                <p className="text-lg">
                  <strong className="pb-cifra">{ruta.resumen.paradas_impulso}</strong> paradas están en zonas que necesitan clientes.
                </p>
              )}
              {ruta.aviso && <p className="text-base text-(--pb-texto-2)">{ruta.aviso}</p>}
            </div>
          )}
        </Paso>

        <Paso numero={3} titulo="Ve y compra en tu barrio" activo={hayRuta}>
          {hayRuta && ruta && (
            <div className="flex flex-col gap-3">
              <ol className="flex flex-col gap-3">
                {ruta.paradas.map((p) => {
                  const hecha = compras.has(p.negocio.id);
                  return (
                    <li key={p.negocio.id} className="rounded-(--pb-radio-tarjeta) bg-(--pb-superficie) p-4 shadow-(--pb-sombra)">
                      <div className="flex items-start gap-3">
                        <span
                          aria-hidden="true"
                          className={`grid size-9 shrink-0 place-items-center rounded-full text-base font-bold text-(--pb-superficie) ${
                            p.negocio.tipo === "alta" ? "bg-(--pb-acento)" : "bg-(--pb-texto)"
                          }`}
                        >
                          {p.orden}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="text-xl font-semibold leading-tight">{p.negocio.nombre}</p>
                          {p.negocio.tipo === "alta" && (
                            <p className="mt-0.5 flex items-center gap-1 text-base font-semibold text-(--pb-acento-fuerte)">
                              <Storefront size={18} aria-hidden="true" /> Recién llegó a colonIA
                            </p>
                          )}
                          <p className="text-base text-(--pb-texto-2)">{p.negocio.giro}</p>
                          <p className="mt-2 text-lg">
                            <span className="font-semibold">Compras aquí:</span> {p.articulos.join(", ")}
                          </p>
                          <ul className="mt-1 text-base text-(--pb-texto-2)" aria-label="Por qué esta parada">
                            {p.por_que.map((razon) => (
                              <li key={razon}>{razonLimpia(razon)}</li>
                            ))}
                          </ul>
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {p.negocio.formas_pago.map((f) => (
                              <Chip key={f}>{PAGO[f.toLowerCase()] ?? f}</Chip>
                            ))}
                            {p.negocio.acepta_mercomuna && <Chip>Acepta Mercomuna</Chip>}
                          </div>
                          <div className="mt-3">
                            {hecha ? (
                              <p role="status" className="flex min-h-(--pb-alto-control) items-center gap-2 text-lg font-semibold text-(--pb-acento-fuerte)">
                                <CheckCircle size={24} weight="fill" aria-hidden="true" />
                                ¡Gracias por comprar en tu barrio!
                              </p>
                            ) : (
                              <Boton variante="secundario" onClick={() => compreAqui(p)}>
                                Compré aquí
                              </Boton>
                            )}
                          </div>
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ol>

              {ruta.sin_resultado.length > 0 && (
                <p className="rounded-(--pb-radio-control) bg-(--pb-superficie-2) px-4 py-3 text-lg">
                  No encontramos comercio de barrio para: {ruta.sin_resultado.join(", ")}.
                </p>
              )}

              <a
                href={`https://wa.me/?text=${encodeURIComponent(textoWhatsApp(ruta))}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex min-h-(--pb-alto-control) items-center justify-center gap-2 rounded-full bg-(--pb-texto) px-6 text-lg font-semibold text-(--pb-superficie)"
              >
                <ShareNetwork size={22} aria-hidden="true" />
                Compartir por WhatsApp
              </a>
            </div>
          )}
        </Paso>
      </div>

      <section aria-label="Mapa de tu ruta" className="relative order-first h-[46vh] min-h-72 lg:order-none lg:h-full">
        <MapaRuta ruta={ruta} origen={origen} />
      </section>
    </div>
  );
}
