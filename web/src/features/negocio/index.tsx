import { useCallback, useEffect, useState } from "react";
import type { FeatureProps } from "../../App";
import { api } from "../../lib/api";
import { DONA_LUPE_ID, mockDonaLupe } from "./mock";
import { normalizar, pagina as normalizarPagina } from "./normalizar";
import type { Cifra, EscalonVista, EstadoEscalon, EstadoPrograma, NegocioVista, PaginaVista } from "./tipos";
import { Boton, Etiqueta, Tarjeta } from "./ui";

export const route = "negocio";
export const label = "Negocio";
export const order = 3;

// Demo selector: live altas from the bot first (newest on top), then Doña Lupe and businesses near the venue
// (ids and names from data/processed/negocios.json).
const NEGOCIOS = [
  { id: DONA_LUPE_ID, nombre: "Puesto de Doña Lupe" },
  { id: "neg-0015", nombre: "Abarrotes Lupita" },
  { id: "neg-0037", nombre: "Recaudería Los Ángeles" },
  { id: "neg-0205", nombre: "Carnicería Los Arcos" },
];

type Opcion = { id: string; nombre: string };
type AltasLive = { altas?: { id?: string; ts?: number; ficha?: { nombre?: string } }[] };

function useAltasEnVivo(): Opcion[] {
  const [altas, setAltas] = useState<Opcion[]>([]);
  useEffect(() => {
    let vivo = true;
    api<AltasLive>("/altas/live?desde=0")
      .then((r) => {
        if (!vivo) return;
        const lista = [...(r.altas ?? [])]
          .sort((a, b) => (b.ts ?? 0) - (a.ts ?? 0))
          .filter((a): a is { id: string; ficha?: { nombre?: string } } => typeof a.id === "string")
          .map((a) => ({ id: a.id, nombre: `${a.ficha?.nombre ?? a.id} · alta nueva` }));
        setAltas(lista);
      })
      .catch(() => undefined); // sin servidor: el selector se queda con la lista fija
    return () => {
      vivo = false;
    };
  }, []);
  return altas;
}

const FOCO = "focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-[var(--pb-foco,#1d4ed8)]";
const TEXTO_2 = "text-[var(--pb-texto-2,#48515c)]";

type Estado =
  | { fase: "cargando" }
  | { fase: "listo"; negocio: NegocioVista }
  | { fase: "error"; mensaje: string };

export default function VistaNegocio({ params }: FeatureProps) {
  const id = params[0] ? decodeURIComponent(params[0]) : DONA_LUPE_ID;
  const [estado, setEstado] = useState<Estado>({ fase: "cargando" });
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vivo = true;
    setEstado({ fase: "cargando" });
    api<unknown>(`/negocio/${encodeURIComponent(id)}`)
      .then((datos) => vivo && setEstado({ fase: "listo", negocio: normalizar(datos) }))
      .catch((error: unknown) => {
        if (!vivo) return;
        // Sample data only for Doña Lupe; never show her data under another business's name.
        if (id === DONA_LUPE_ID) setEstado({ fase: "listo", negocio: normalizar(mockDonaLupe, true) });
        else setEstado({ fase: "error", mensaje: error instanceof Error ? error.message : "sin respuesta" });
      });
    return () => {
      vivo = false;
    };
  }, [id, intento]);

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 bg-[var(--pb-fondo,#f6f7f9)] px-5 py-3 text-[var(--pb-texto,#15191e)]">
      <Selector id={id} />
      {estado.fase === "cargando" && (
        <p role="status" className={`p-6 text-xl ${TEXTO_2}`}>
          Cargando la información de tu negocio…
        </p>
      )}
      {estado.fase === "error" && (
        <div role="alert" className="flex flex-col items-start gap-3 rounded-2xl border border-[var(--pb-error,#b42318)] bg-white p-6">
          <p className="text-xl font-semibold">No pudimos cargar este negocio.</p>
          <p className={`text-lg ${TEXTO_2}`}>Revisa tu conexión e inténtalo otra vez. (Detalle: {estado.mensaje})</p>
          <div className="flex flex-wrap gap-3">
            <Boton onClick={() => setIntento((n) => n + 1)}>Intentar otra vez</Boton>
            <Boton variante="secundario" onClick={() => (window.location.hash = `#/negocio/${DONA_LUPE_ID}`)}>
              Ver el ejemplo de Doña Lupe
            </Boton>
          </div>
        </div>
      )}
      {estado.fase === "listo" && <Panel key={estado.negocio.id || id} negocio={estado.negocio} id={id} />}
    </div>
  );
}

function Selector({ id }: { id: string }) {
  const altas = useAltasEnVivo();
  const opciones = [...altas, ...NEGOCIOS.filter((n) => !altas.some((a) => a.id === n.id))];
  const conocido = opciones.some((n) => n.id === id);
  return (
    <div className="flex shrink-0 flex-wrap items-center gap-3">
      <label htmlFor="negocio-selector" className="text-lg font-medium">
        Elige un negocio
      </label>
      <select
        id="negocio-selector"
        value={id}
        onChange={(e) => (window.location.hash = `#/negocio/${encodeURIComponent(e.target.value)}`)}
        className={`min-h-12 rounded-xl border-2 border-[var(--pb-borde-fuerte,#7d8793)] bg-white px-3 text-lg ${FOCO}`}
      >
        {!conocido && <option value={id}>{id}</option>}
        {opciones.map((n) => (
          <option key={n.id} value={n.id}>
            {n.nombre}
          </option>
        ))}
      </select>
    </div>
  );
}

function Panel({ negocio, id }: { negocio: NegocioVista; id: string }) {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3">
      {negocio.demo_data && (
        <p role="note" className="flex shrink-0 flex-wrap items-center gap-2 rounded-xl border border-dashed border-[var(--pb-borde-fuerte,#7d8793)] bg-[var(--pb-simulado-fondo,#eceff3)] px-4 py-2 text-lg">
          <Etiqueta tipo="simulado" fuente="mock local de la vista Negocio" />
          Datos de ejemplo: no hay conexión con el servidor, así que mostramos un ejemplo de Doña Lupe.
        </p>
      )}
      <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 overflow-auto lg:grid-cols-3 lg:overflow-hidden">
        <div className="flex min-h-0 flex-col gap-3 lg:overflow-auto">
          <AvanceTarjeta negocio={negocio} />
          <FichaTarjeta negocio={negocio} />
        </div>
        <div className="min-h-0 lg:overflow-auto">
          <EscaleraTarjeta escalera={negocio.escalera} />
        </div>
        <div className="flex min-h-0 flex-col gap-3 lg:overflow-auto">
          <PaginaTarjeta id={id} inicial={negocio.pagina} demo={negocio.demo_data} />
          <ProgramasTarjeta negocio={negocio} />
        </div>
      </div>
    </div>
  );
}

const PAGO: Record<string, string> = {
  efectivo: "Efectivo",
  transferencia: "Transferencia",
  dimo: "DiMo",
  codi: "CoDi",
  tarjeta: "Tarjeta",
};

function FichaTarjeta({ negocio }: { negocio: NegocioVista }) {
  const f = negocio.ficha;
  const tipoPrecio = negocio.demo_data ? "simulado" : "real";
  return (
    <Tarjeta titulo={f.nombre}>
      {f.giro && <p className={`text-lg ${TEXTO_2}`}>{f.giro}</p>}
      {f.descripcion && <p className="mt-1 text-lg">{f.descripcion}</p>}
      <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-lg">
        {f.horario && (
          <>
            <dt className="font-semibold">Horario</dt>
            <dd>{f.horario}</dd>
          </>
        )}
        {f.colonia && (
          <>
            <dt className="font-semibold">Colonia</dt>
            <dd>{f.colonia}</dd>
          </>
        )}
        {f.formas_pago.length > 0 && (
          <>
            <dt className="font-semibold">Cobras con</dt>
            <dd>{f.formas_pago.map((p) => PAGO[p.toLowerCase()] ?? p).join(" · ")}</dd>
          </>
        )}
        {f.acepta_mercomuna !== null && (
          <>
            <dt className="font-semibold">Mercomuna</dt>
            <dd>{f.acepta_mercomuna ? "Sí aceptas" : "Todavía no"}</dd>
          </>
        )}
      </dl>
      {f.productos.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-2" aria-label="Productos y precios">
          {f.productos.map((p) => (
            <li key={p.nombre} className="flex items-center gap-2 rounded-xl bg-[var(--pb-superficie-2,#eef1f4)] px-3 py-1 text-lg">
              <span className="capitalize">{p.nombre}</span>
              {p.precio !== null && (
                <>
                  <span className="pb-cifra font-semibold tabular-nums">
                    ${p.precio}
                    {p.unidad ? ` el ${p.unidad}` : ""}
                  </span>
                  <Etiqueta tipo={tipoPrecio} fuente={negocio.demo_data ? "Ejemplo" : "Ficha del negocio"} />
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </Tarjeta>
  );
}

function Numero({ texto, cifra }: { texto: string; cifra: Cifra }) {
  return (
    <div className="flex flex-col gap-1 rounded-xl bg-[var(--pb-superficie-2,#eef1f4)] p-3">
      <span className="pb-cifra text-[2rem] font-bold leading-none tabular-nums">{cifra.valor ?? "—"}</span>
      <span className="text-lg leading-snug">{texto}</span>
      <Etiqueta tipo={cifra.tipo_dato} fuente={cifra.fuente} className="self-start" />
    </div>
  );
}

function AvanceTarjeta({ negocio }: { negocio: NegocioVista }) {
  const a = negocio.avance;
  const prom = a.promedio_zona_apariciones;
  return (
    <Tarjeta
      titulo="Mi avance"
      extra={<span className={`text-base ${TEXTO_2}`}>· solo tú lo ves · {a.periodo}</span>}
    >
      <div className="grid grid-cols-3 gap-2">
        <Numero texto="veces en rutas de compra" cifra={a.apariciones_ruta} />
        <Numero texto="“Compré aquí”" cifra={a.compre_aqui} />
        <Numero texto="visitas a tu página" cifra={a.vistas_pagina} />
      </div>
      {prom && prom.valor !== null && (
        <p className="mt-2 flex flex-wrap items-center gap-2 text-lg">
          Promedio de tu zona: <strong className="pb-cifra tabular-nums">{prom.valor}</strong> veces en rutas
          <Etiqueta tipo={prom.tipo_dato} fuente={prom.fuente} />
        </p>
      )}
      {(a.nota || a.tipo_dato === "simulado") && (
        <p className={`mt-2 text-base ${TEXTO_2}`}>
          {a.nota ?? "Cifras de ejemplo: aún no hay suficientes visitas reales de tu negocio."}
        </p>
      )}
    </Tarjeta>
  );
}

const ESCALON: Record<EstadoEscalon, { texto: string; clase: string; icono: string }> = {
  logrado: { texto: "Logrado", clase: "bg-[var(--pb-real-fondo,#dcfce7)] text-[var(--pb-real-texto,#14532d)]", icono: "✓" },
  siguiente: { texto: "Tu siguiente paso", clase: "bg-[var(--pb-acento-suave,#fff1e6)] text-[var(--pb-acento-fuerte,#9a3412)]", icono: "→" },
  pendiente: { texto: "Pendiente", clase: "bg-[var(--pb-superficie-2,#eef1f4)] text-[var(--pb-texto-2,#48515c)]", icono: "·" },
  proximamente: { texto: "Próximamente", clase: "bg-[var(--pb-superficie-2,#eef1f4)] text-[var(--pb-texto-2,#48515c)]", icono: "…" },
  horizonte: { texto: "En el horizonte", clase: "bg-[var(--pb-superficie-2,#eef1f4)] text-[var(--pb-texto-2,#48515c)]", icono: "☆" },
};

function EscaleraTarjeta({ escalera }: { escalera: EscalonVista[] }) {
  return (
    <Tarjeta titulo="Tu escalera de barrio">
      {escalera.length === 0 ? (
        <p className={`text-lg ${TEXTO_2}`}>Todavía no hay escalones para este negocio.</p>
      ) : (
        <ol className="flex flex-col gap-2">
          {escalera.map((e) => {
            const est = ESCALON[e.estado];
            const activo = e.estado === "siguiente";
            return (
              <li
                key={e.numero}
                className={`rounded-xl border-2 p-3 ${
                  activo ? "border-[var(--pb-acento,#c2410c)]" : "border-[var(--pb-borde,#d3d9e0)]"
                }`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    aria-hidden="true"
                    className="flex size-9 items-center justify-center rounded-full bg-[var(--pb-texto,#15191e)] text-lg font-bold text-white"
                  >
                    {e.numero}
                  </span>
                  <h3 className="text-[1.222rem] font-semibold">
                    <span className="sr-only">Escalón {e.numero}: </span>
                    {e.nombre}
                  </h3>
                  <span className={`ml-auto rounded-full px-3 py-0.5 text-base font-semibold ${est.clase}`}>
                    <span aria-hidden="true">{est.icono} </span>
                    {est.texto}
                  </span>
                </div>
                {e.beneficio && <p className="mt-1 text-lg">{e.beneficio}</p>}
                {e.siguiente_accion && (
                  <p className={`mt-1 text-lg ${activo ? "font-semibold" : TEXTO_2}`}>
                    <span className="font-semibold">Qué sigue: </span>
                    {e.siguiente_accion}
                  </p>
                )}
              </li>
            );
          })}
        </ol>
      )}
      <p className={`mt-2 text-base ${TEXTO_2}`}>Nada aquí es obligatorio ni es un trámite. Tú decides cuándo subir.</p>
    </Tarjeta>
  );
}

const PROGRAMA: Record<EstadoPrograma, { texto: string; clase: string }> = {
  existe: { texto: "Existe", clase: "bg-[var(--pb-real-fondo,#dcfce7)] text-[var(--pb-real-texto,#14532d)]" },
  por_verificar: {
    texto: "Por verificar",
    clase: "bg-[var(--pb-estimado-fondo,#dbeafe)] text-[var(--pb-estimado-texto,#1e3a8a)]",
  },
  propuesta: {
    texto: "Propuesta",
    clase: "border border-dashed border-[var(--pb-simulado-texto,#3d4651)] bg-[var(--pb-simulado-fondo,#eceff3)] text-[var(--pb-simulado-texto,#3d4651)]",
  },
};

function ProgramasTarjeta({ negocio }: { negocio: NegocioVista }) {
  return (
    <Tarjeta titulo="Programas para ti">
      {negocio.programas.length === 0 ? (
        <p className={`text-lg ${TEXTO_2}`}>Por ahora no encontramos programas para tu negocio.</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {negocio.programas.map((p) => {
            const est = PROGRAMA[p.estado];
            return (
              <li key={p.id} className="rounded-xl border border-[var(--pb-borde,#d3d9e0)] p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-semibold">{p.nombre}</h3>
                  <span className={`rounded-full px-3 py-0.5 text-base font-semibold ${est.clase}`}>{est.texto}</span>
                  {p.puede_entrar && <span className="text-base font-semibold text-[var(--pb-real-texto,#14532d)]">Puedes entrar</span>}
                </div>
                {p.que_es && <p className="mt-1 text-lg">{p.que_es}</p>}
                {p.motivo && <p className={`text-base ${TEXTO_2}`}>Por qué: {p.motivo}</p>}
                {p.como_entrar && <p className={`text-base ${TEXTO_2}`}>Cómo entrar: {p.como_entrar}</p>}
                {p.url_oficial && (
                  <a
                    href={p.url_oficial}
                    target="_blank"
                    rel="noreferrer"
                    className={`mt-1 inline-flex min-h-12 items-center text-lg font-semibold text-[var(--pb-foco,#1d4ed8)] underline ${FOCO}`}
                  >
                    Sitio oficial
                  </a>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </Tarjeta>
  );
}

type EstadoPagina =
  | { fase: "inicial" }
  | { fase: "generando" }
  | { fase: "lista"; pagina: PaginaVista }
  | { fase: "error"; mensaje: string };

const ENLACE = `inline-flex min-h-12 items-center justify-center rounded-xl border-2 border-[var(--pb-borde-fuerte,#7d8793)] bg-white px-4 text-lg font-semibold hover:bg-[var(--pb-superficie-2,#eef1f4)] ${FOCO}`;

function PaginaTarjeta({ id, inicial, demo }: { id: string; inicial: PaginaVista | null; demo: boolean }) {
  const [estado, setEstado] = useState<EstadoPagina>(inicial ? { fase: "lista", pagina: inicial } : { fase: "inicial" });

  const generar = useCallback(() => {
    setEstado({ fase: "generando" });
    api<unknown>(`/negocio/${encodeURIComponent(id)}/pagina`, { method: "POST" })
      .then((datos) => {
        const p = normalizarPagina(datos);
        setEstado(p ? { fase: "lista", pagina: p } : { fase: "error", mensaje: "respuesta sin enlace" });
      })
      .catch((error: unknown) =>
        setEstado({ fase: "error", mensaje: error instanceof Error ? error.message : "sin respuesta" }),
      );
  }, [id]);

  return (
    <Tarjeta titulo="Mi página web">
      {estado.fase !== "lista" && (
        <p className={`mb-2 text-lg ${TEXTO_2}`}>
          Una página sencilla con tus productos, horario y formas de pago, más un cartel con código QR para tu puesto.
        </p>
      )}
      <Boton onClick={generar} disabled={estado.fase === "generando"} aria-busy={estado.fase === "generando"} className="w-full">
        {estado.fase === "generando" ? "Generando tu página…" : estado.fase === "lista" ? "Volver a generar mi página" : "Generar mi página"}
      </Boton>
      {estado.fase === "error" && (
        <p role="alert" className="mt-2 text-lg text-[var(--pb-error,#b42318)]">
          No se pudo generar la página{demo ? " (sin conexión con el servidor)" : ""}. Inténtalo otra vez. ({estado.mensaje})
        </p>
      )}
      {estado.fase === "lista" && (
        <div className="mt-3 flex flex-col gap-3">
          <div className="flex items-start gap-3">
            {estado.pagina.qr ? (
              <img
                src={estado.pagina.qr}
                alt="Código QR que abre tu página"
                className="size-32 shrink-0 rounded-lg border border-[var(--pb-borde,#d3d9e0)] bg-white [image-rendering:pixelated]"
              />
            ) : (
              <p className={`text-base ${TEXTO_2}`}>El código QR aparece al generar tu página.</p>
            )}
            <div className="flex flex-1 flex-col gap-2">
              <a href={estado.pagina.url} target="_blank" rel="noreferrer" className={ENLACE}>
                Ver mi página
              </a>
              <a href={estado.pagina.cartel} target="_blank" rel="noreferrer" className={ENLACE}>
                Imprimir mi cartel
              </a>
            </div>
          </div>
          <iframe
            title="Vista previa de tu página"
            src={estado.pagina.url}
            className="h-56 w-full rounded-xl border border-[var(--pb-borde,#d3d9e0)] bg-white"
          />
        </div>
      )}
    </Tarjeta>
  );
}
