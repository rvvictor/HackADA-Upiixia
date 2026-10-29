import { useState } from "react";

import type { FeatureProps } from "../../App";
import { api } from "../../lib/api";
import { Boton, Chip, Etiqueta, Tarjeta } from "../../lib/ui";
import { LISTA_EJEMPLO, RUTA_EJEMPLO, SEDE } from "./ejemplo";
import { MapaRuta } from "./MapaRuta";
import type { Parada, Punto, Ruta } from "./tipos";

export const route = "usuario";
export const label = "Vecina";
export const order = 2;

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

function textoWhatsApp(ruta: Ruta): string {
  const lineas = ruta.paradas.map((p) => `${p.orden}. ${p.negocio.nombre}: ${p.articulos.join(", ")}`);
  return `Mi ruta de compras de barrio (${km(ruta.distancia_m)} a pie, 0 cadenas):\n${lineas.join("\n")}\nHecha con Pulso Barrial`;
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
      // Sin API: mostrar la ruta de ejemplo, marcada como tal, para que la demo no se caiga.
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

  return (
    <div className="grid h-full grid-cols-1 gap-4 bg-(--pb-fondo) p-4 lg:grid-cols-[minmax(0,1fr)_26rem]">
      <section className="relative min-h-80" aria-label="Mapa de tu ruta">
        <MapaRuta ruta={ruta} origen={origen} />
      </section>

      <aside className="flex min-h-0 flex-col gap-3 overflow-y-auto">
        <Tarjeta titulo="¿Qué necesitas comprar?">
          <label htmlFor="lista" className="sr-only">
            Tu lista del mandado
          </label>
          <textarea
            id="lista"
            value={lista}
            onChange={(e) => setLista(e.target.value)}
            rows={3}
            placeholder="2 kilos de jitomate, tortillas, tenis para niño…"
            className="w-full resize-none rounded-lg border border-(--pb-borde-fuerte) bg-(--pb-superficie) p-3 text-lg leading-snug focus:outline-2 focus:outline-(--pb-foco)"
          />
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Boton onClick={armar} disabled={estado === "cargando"}>
              {estado === "cargando" ? "Armando…" : "Armar mi ruta"}
            </Boton>
            <Boton variante="secundario" onClick={usarUbicacion}>
              Usar mi ubicación
            </Boton>
          </div>
          <p className="mt-2 text-sm text-(--pb-texto-2)">
            {usaUbicacion ? "Salimos desde tu ubicación." : "Salimos desde la Utopía Elena Poniatowska, San Lucas, Coyoacán."}
          </p>
        </Tarjeta>

        {estado === "vacio" && (
          <p className="px-1 text-base text-(--pb-texto-2)">
            Te armamos una ruta a pie que pasa solo por negocios de tu barrio: tianguis, mercados y tienditas. Nunca por
            cadenas.
          </p>
        )}

        {estado === "cargando" && (
          <p role="status" className="px-1 text-lg">
            Buscando en los negocios de tu barrio…
          </p>
        )}

        {ruta && estado !== "cargando" && (
          <>
            {esEjemplo && (
              <p role="alert" className="rounded-lg bg-(--pb-acento-suave) px-3 py-2 text-base">
                No pudimos conectar con el servidor. Te mostramos una ruta de ejemplo (datos de ejemplo).
              </p>
            )}
            <div className="flex flex-wrap items-center gap-2" aria-label="Resumen de la ruta">
              <Chip activo>0 cadenas</Chip>
              <Chip>{km(ruta.distancia_m)} a pie · {ruta.minutos} min</Chip>
              <Chip>{ruta.paradas.length} paradas</Chip>
              {ruta.resumen.paradas_impulso > 0 && (
                <Chip>
                  {ruta.resumen.paradas_impulso} en zonas que necesitan clientes
                </Chip>
              )}
              {ruta.demo_data && <Etiqueta tipo="simulado" fuente="Negocios simulados con forma del DENUE" />}
            </div>
            {ruta.aviso && <p className="text-sm text-(--pb-texto-2)">{ruta.aviso}</p>}

            <ol className="flex flex-col gap-3">
              {ruta.paradas.map((p) => (
                <li key={p.negocio.id}>
                  <Tarjeta
                    titulo={
                      <span className="flex items-center gap-2">
                        <span
                          aria-hidden="true"
                          className={`flex size-8 shrink-0 items-center justify-center rounded-full text-white ${
                            p.negocio.tipo === "alta" ? "bg-(--pb-real-texto)" : "bg-(--pb-acento)"
                          }`}
                        >
                          {p.orden}
                        </span>
                        <span>{p.negocio.nombre}</span>
                      </span>
                    }
                  >
                    <p className="text-base text-(--pb-texto-2)">{p.negocio.giro}</p>
                    <p className="mt-1 text-lg">
                      <span className="font-semibold">Compras aquí:</span> {p.articulos.join(", ")}
                    </p>
                    <ul className="mt-2 flex flex-col gap-0.5 text-base text-(--pb-texto-2)" aria-label="Por qué esta parada">
                      {p.por_que.map((razon) => (
                        <li key={razon}>· {razon}</li>
                      ))}
                    </ul>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {p.negocio.formas_pago.map((f) => (
                        <Chip key={f}>{PAGO[f.toLowerCase()] ?? f}</Chip>
                      ))}
                      {p.negocio.acepta_mercomuna && <Chip>Acepta Mercomuna</Chip>}
                      <Etiqueta tipo={p.negocio.tipo_dato} />
                    </div>
                    <div className="mt-3">
                      <Boton
                        variante={compras.has(p.negocio.id) ? "fantasma" : "secundario"}
                        onClick={() => compreAqui(p)}
                        disabled={compras.has(p.negocio.id)}
                      >
                        {compras.has(p.negocio.id) ? "¡Gracias por comprar en tu barrio!" : "Compré aquí"}
                      </Boton>
                    </div>
                  </Tarjeta>
                </li>
              ))}
            </ol>

            {ruta.sin_resultado.length > 0 && (
              <Tarjeta titulo="No encontramos comercio de barrio para:">
                <p className="text-lg">{ruta.sin_resultado.join(", ")}</p>
              </Tarjeta>
            )}

            <a
              href={`https://wa.me/?text=${encodeURIComponent(textoWhatsApp(ruta))}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex min-h-12 items-center justify-center rounded-lg bg-(--pb-real-texto) px-5 text-lg font-semibold text-white"
            >
              Compartir por WhatsApp
            </a>
          </>
        )}
      </aside>
    </div>
  );
}
