import { useCallback, useEffect, useState } from "react";
import { Bicycle, CheckCircle, PencilSimple, Storefront, UserCircle } from "@phosphor-icons/react";
import type { FeatureProps } from "../../App";
import { api } from "../../lib/api";
import { Boton, PageHeader, PageLayout, Tarjeta } from "../../lib/ui";
import { DONA_LUPE_ID, mockDonaLupe } from "./mock";
import { normalizar, pagina as normalizarPagina } from "./normalizar";
import type { Cifra, EscalonVista, EstadoEscalon, EstadoPrograma, FichaVista, NegocioVista, PaginaVista } from "./tipos";

export const route = "negocio";
export const label = "Negocio";
export const order = 3;

// Recipe "detail" (web/DESIGN.md §6). Hero: the card of the business that just signed up by voice note, next to
// the delivery person of its colonia. No real/simulado chips on screen (uak decision CO-028).

// Demo selector: live altas from the bot first (newest on top), then Doña Lupe and businesses near the venue
// (ids and names from data/processed/negocios.json).
const NEGOCIOS = [
  { id: DONA_LUPE_ID, nombre: "Puesto de Doña Lupe" },
  { id: "neg-0015", nombre: "Abarrotes Lupita" },
  { id: "neg-0037", nombre: "Recaudería Los Ángeles" },
  { id: "neg-0205", nombre: "Carnicería Los Arcos" },
];

// The only public delivery profile we can read without a session (the demo rider; app/services/repartidores.py).
const REPARTIDOR_DEMO = "R-00001";

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

const TEXTO_2 = "text-(--pb-texto-2)";
const CAMPO =
  "min-h-(--pb-alto-control) w-full rounded-(--pb-radio-control) border-2 border-(--pb-borde-fuerte) bg-(--pb-superficie) px-3 text-lg";

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
    queueMicrotask(() => vivo && setEstado({ fase: "cargando" }));
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

  const negocio = estado.fase === "listo" ? estado.negocio : null;
  const sub = negocio ? [negocio.ficha.giro, negocio.ficha.colonia].filter(Boolean).join(" · ") : undefined;

  return (
    <PageLayout>
      <PageHeader
        titulo={negocio?.ficha.nombre ?? "Tu negocio"}
        descripcion={sub || "Tu ficha, tu repartidor y lo que sigue para crecer."}
        acciones={<Selector id={id} />}
      />
      {estado.fase === "cargando" && <Esqueleto />}
      {estado.fase === "error" && (
        <Tarjeta role="alert" className="border-(--pb-error)">
          <p className="text-xl font-semibold">No pudimos cargar este negocio.</p>
          <p className={`mt-2 text-lg ${TEXTO_2}`}>Revisa tu conexión e inténtalo otra vez. (Detalle: {estado.mensaje})</p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Boton onClick={() => setIntento((n) => n + 1)}>Intentar otra vez</Boton>
            <Boton variante="secundario" onClick={() => (window.location.hash = `#/negocio/${DONA_LUPE_ID}`)}>
              Ver a Doña Lupe
            </Boton>
          </div>
        </Tarjeta>
      )}
      {negocio && (
        <Panel
          key={negocio.id || id}
          negocio={negocio}
          id={id}
          onCambio={(n) => setEstado({ fase: "listo", negocio: n })}
        />
      )}
    </PageLayout>
  );
}

function Esqueleto() {
  return (
    <div role="status" aria-label="Cargando la información de tu negocio" className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
      {[0, 1].map((i) => (
        <div key={i} className="h-72 rounded-(--pb-radio-tarjeta) bg-(--pb-superficie-2) motion-safe:animate-pulse" />
      ))}
    </div>
  );
}

function Selector({ id }: { id: string }) {
  const altas = useAltasEnVivo();
  const opciones = [...altas, ...NEGOCIOS.filter((n) => !altas.some((a) => a.id === n.id))];
  const conocido = opciones.some((n) => n.id === id);
  return (
    <div className="flex w-full flex-col gap-1 md:w-80">
      <label htmlFor="negocio-selector" className={`text-base font-medium ${TEXTO_2}`}>
        Elige un negocio
      </label>
      <select
        id="negocio-selector"
        value={id}
        onChange={(e) => (window.location.hash = `#/negocio/${encodeURIComponent(e.target.value)}`)}
        className={CAMPO}
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

function Panel({ negocio, id, onCambio }: { negocio: NegocioVista; id: string; onCambio: (n: NegocioVista) => void }) {
  const [editando, setEditando] = useState(false);
  return (
    <div className="flex flex-col gap-6">
      {negocio.demo_data && (
        <p role="note" className={`rounded-(--pb-radio-control) bg-(--pb-superficie-2) px-4 py-3 text-lg ${TEXTO_2}`}>
          Sin conexión con el servidor: te mostramos el ejemplo de Doña Lupe.
        </p>
      )}
      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <FichaTarjeta negocio={negocio} id={id} onCambio={onCambio} editando={editando} setEditando={setEditando} />
        <div className="flex flex-col gap-6">
          <RepartidorTarjeta negocio={negocio} id={id} onAgregarColonia={() => setEditando(true)} />
          <AvanceTarjeta negocio={negocio} />
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <EscaleraTarjeta escalera={negocio.escalera} />
        <div className="flex flex-col gap-6">
          <PaginaTarjeta id={id} inicial={negocio.pagina} offline={negocio.demo_data} />
          <ProgramasTarjeta negocio={negocio} />
        </div>
      </div>
    </div>
  );
}

const PAGO: Record<string, string> = {
  efectivo: "Efectivo",
  transferencia: "Transferencia",
  tarjeta: "Tarjeta",
  codi: "CoDi",
  dimo: "DiMo",
};

type Borrador = { nombre: string; giro: string; colonia: string; horario: string; formas_pago: string[] };

function borradorDe(f: FichaVista): Borrador {
  return {
    nombre: f.nombre,
    giro: f.giro ?? "",
    colonia: f.colonia ?? "",
    horario: f.horario ?? "",
    formas_pago: f.formas_pago.map((p) => p.toLowerCase()),
  };
}

type Guardado = { fase: "quieto" } | { fase: "guardando" } | { fase: "ok"; local: boolean } | { fase: "error"; mensaje: string };

/** Hero of the screen: what the AI extracted from the voice note, editable in place. */
type FichaProps = {
  negocio: NegocioVista;
  id: string;
  onCambio: (n: NegocioVista) => void;
  editando: boolean;
  setEditando: (v: boolean) => void;
};

function FichaTarjeta({ negocio, id, onCambio, editando, setEditando }: FichaProps) {
  const f = negocio.ficha;
  const [b, setB] = useState<Borrador>(() => borradorDe(f));
  const [guardado, setGuardado] = useState<Guardado>({ fase: "quieto" });

  const guardar = () => {
    const cambios = { ...b, giro: b.giro || null, colonia: b.colonia || null, horario: b.horario || null };
    const local = () => {
      onCambio({ ...negocio, ficha: { ...f, ...cambios } });
      setEditando(false);
      setGuardado({ fase: "ok", local: true });
    };
    if (negocio.demo_data) return local(); // sample data: nothing to save on the server
    setGuardado({ fase: "guardando" });
    api<unknown>(`/negocio/${encodeURIComponent(id)}/ficha`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cambios),
    })
      .then((datos) => {
        onCambio(normalizar(datos));
        setEditando(false);
        setGuardado({ fase: "ok", local: false });
      })
      .catch((e: unknown) => setGuardado({ fase: "error", mensaje: e instanceof Error ? e.message : "sin respuesta" }));
  };

  const accion = !editando && (
    <Boton
      variante="secundario"
      icono={<PencilSimple />}
      onClick={() => {
        setB(borradorDe(f));
        setGuardado({ fase: "quieto" });
        setEditando(true);
      }}
    >
      Editar
    </Boton>
  );

  return (
    <Tarjeta antetitulo="Lo que dijiste en tu nota de voz" titulo="Tu ficha" accion={accion} className="shadow-(--pb-sombra-alta)">
      {f.descripcion && !editando && <p className="mb-4 text-xl leading-relaxed">“{f.descripcion}”</p>}

      {editando ? (
        <form
          className="grid gap-4 sm:grid-cols-2"
          onSubmit={(e) => {
            e.preventDefault();
            guardar();
          }}
        >
          <Campo etiqueta="Nombre" valor={b.nombre} onCambio={(v) => setB({ ...b, nombre: v })} requerido />
          <Campo etiqueta="Qué vendes" valor={b.giro} onCambio={(v) => setB({ ...b, giro: v })} />
          <Campo etiqueta="Colonia" valor={b.colonia} onCambio={(v) => setB({ ...b, colonia: v })} />
          <Campo etiqueta="Horario" valor={b.horario} onCambio={(v) => setB({ ...b, horario: v })} ayuda="Ejemplo: de 7:00 a 15:00" />
          <fieldset className="sm:col-span-2">
            <legend className="mb-2 text-base font-medium">Cobras con</legend>
            <div className="flex flex-wrap gap-2">
              {Object.entries(PAGO).map(([clave, texto]) => {
                const on = b.formas_pago.includes(clave);
                return (
                  <button
                    key={clave}
                    type="button"
                    aria-pressed={on}
                    onClick={() =>
                      setB({ ...b, formas_pago: on ? b.formas_pago.filter((p) => p !== clave) : [...b.formas_pago, clave] })
                    }
                    className={`min-h-(--pb-alto-control) rounded-full border-2 px-4 text-base font-semibold ${
                      on
                        ? "border-(--pb-acento) bg-(--pb-acento-suave) text-(--pb-acento-fuerte)"
                        : "border-(--pb-borde-fuerte) bg-(--pb-superficie) text-(--pb-texto)"
                    }`}
                  >
                    {texto}
                  </button>
                );
              })}
            </div>
          </fieldset>
          <div className="flex flex-wrap gap-3 sm:col-span-2">
            <Boton type="submit" disabled={guardado.fase === "guardando" || !b.nombre.trim()}>
              {guardado.fase === "guardando" ? "Guardando…" : "Guardar cambios"}
            </Boton>
            <Boton variante="fantasma" onClick={() => setEditando(false)}>
              Cancelar
            </Boton>
          </div>
          {guardado.fase === "error" && (
            <p role="alert" className="text-lg text-(--pb-error) sm:col-span-2">
              No se guardó. Inténtalo otra vez. ({guardado.mensaje})
            </p>
          )}
        </form>
      ) : (
        <>
          <dl className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
            <Dato termino="Qué vendes" valor={f.giro} />
            <Dato termino="Colonia" valor={f.colonia} />
            <Dato termino="Horario" valor={f.horario} />
            <Dato termino="Cobras con" valor={f.formas_pago.map((p) => PAGO[p.toLowerCase()] ?? p).join(", ") || null} />
            {f.acepta_mercomuna !== null && <Dato termino="Mercomuna" valor={f.acepta_mercomuna ? "Sí aceptas" : "Todavía no"} />}
          </dl>
          {f.productos.length > 0 && (
            <ul className="mt-5 flex flex-wrap gap-2" aria-label="Productos y precios">
              {f.productos.map((p) => (
                <li key={p.nombre} className="flex items-baseline gap-2 rounded-full bg-(--pb-superficie-2) px-4 py-2 text-lg">
                  <span className="font-medium capitalize">{p.nombre}</span>
                  {p.precio !== null && (
                    <span className="pb-cifra font-semibold text-(--pb-acento-fuerte)">
                      ${p.precio}
                      {p.unidad ? ` el ${p.unidad}` : ""}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
          {guardado.fase === "ok" && (
            <p role="status" className="mt-4 flex items-center gap-2 text-lg text-(--pb-jade)">
              <CheckCircle size={22} weight="fill" aria-hidden="true" />
              {guardado.local ? "Cambios listos en esta pantalla (sin conexión, no se guardaron)." : "Cambios guardados."}
            </p>
          )}
        </>
      )}
    </Tarjeta>
  );
}

function Campo({
  etiqueta,
  valor,
  onCambio,
  ayuda,
  requerido = false,
}: {
  etiqueta: string;
  valor: string;
  onCambio: (v: string) => void;
  ayuda?: string;
  requerido?: boolean;
}) {
  const idCampo = `campo-${etiqueta.toLowerCase().replace(/\s+/g, "-")}`;
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={idCampo} className="text-base font-medium">
        {etiqueta}
      </label>
      <input
        id={idCampo}
        value={valor}
        required={requerido}
        onChange={(e) => onCambio(e.target.value)}
        aria-describedby={ayuda ? `${idCampo}-ayuda` : undefined}
        className={CAMPO}
      />
      {ayuda && (
        <p id={`${idCampo}-ayuda`} className={`text-base ${TEXTO_2}`}>
          {ayuda}
        </p>
      )}
    </div>
  );
}

function Dato({ termino, valor }: { termino: string; valor: string | null }) {
  return (
    <div>
      <dt className={`text-base ${TEXTO_2}`}>{termino}</dt>
      <dd className="text-lg font-semibold">{valor || "Sin dato todavía"}</dd>
    </div>
  );
}

type Repartidor = {
  id: string;
  nombre_mostrar?: string;
  colonias?: string[];
  transporte?: string;
  rutas_completadas?: number;
  negocio_id?: string | null;
};

type EstadoRep = { fase: "cargando" } | { fase: "listo"; rep: Repartidor | null };

/** The delivery person of the same colonia, when there is one. Never invents a match. */
function RepartidorTarjeta({ negocio, id, onAgregarColonia }: { negocio: NegocioVista; id: string; onAgregarColonia: () => void }) {
  const colonia = negocio.ficha.colonia;
  const [estado, setEstado] = useState<EstadoRep>({ fase: "cargando" });

  useEffect(() => {
    let vivo = true;
    api<Repartidor>(`/repartidores/${REPARTIDOR_DEMO}`)
      .then((r) => {
        if (!vivo) return;
        const mismo = r.negocio_id === id || (!!colonia && (r.colonias ?? []).some((c) => c.toLowerCase() === colonia.toLowerCase()));
        setEstado({ fase: "listo", rep: mismo ? r : null });
      })
      .catch(() => vivo && setEstado({ fase: "listo", rep: null }));
    return () => {
      vivo = false;
    };
  }, [id, colonia]);

  return (
    <Tarjeta titulo="Tu repartidor de la colonia">
      {estado.fase === "cargando" && <div className="h-20 rounded-(--pb-radio-control) bg-(--pb-superficie-2) motion-safe:animate-pulse" />}
      {estado.fase === "listo" && estado.rep && (
        <div className="flex items-center gap-4">
          <span className="grid size-14 shrink-0 place-items-center rounded-full bg-(--pb-acento-suave) text-(--pb-acento-fuerte)">
            {estado.rep.transporte === "bici" ? <Bicycle size={30} aria-hidden="true" /> : <UserCircle size={30} aria-hidden="true" />}
          </span>
          <div className="min-w-0">
            <p className="text-xl font-semibold">{estado.rep.nombre_mostrar ?? estado.rep.id}</p>
            <p className={`text-lg ${TEXTO_2}`}>
              Reparte en {(estado.rep.colonias ?? []).join(", ") || colonia}
              {estado.rep.transporte ? ` · en ${estado.rep.transporte}` : ""}
            </p>
            {typeof estado.rep.rutas_completadas === "number" && (
              <p className="text-lg">
                <span className="pb-cifra font-semibold">{estado.rep.rutas_completadas}</span> rutas completadas
              </p>
            )}
          </div>
        </div>
      )}
      {estado.fase === "listo" && !estado.rep && !colonia && (
        <div className="flex flex-col items-start gap-3">
          <p className="text-lg">Dinos en qué colonia está tu negocio y te mostramos a quien reparte ahí.</p>
          <Boton variante="secundario" icono={<PencilSimple />} onClick={onAgregarColonia}>
            Agregar mi colonia
          </Boton>
        </div>
      )}
      {estado.fase === "listo" && !estado.rep && colonia && (
        <div className="flex items-start gap-3">
          <Storefront size={28} className="mt-0.5 shrink-0 text-(--pb-texto-2)" aria-hidden="true" />
          <p className="text-lg">
            Todavía no hay repartidor en {colonia}. Cuando alguien de tu colonia se registre en el bot de Telegram,
            aparecerá aquí.
          </p>
        </div>
      )}
    </Tarjeta>
  );
}

function Numero({ texto, cifra }: { texto: string; cifra: Cifra }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="pb-cifra pb-display text-[2.4rem] font-extrabold leading-none">{cifra.valor ?? "0"}</span>
      <span className={`text-base leading-snug ${TEXTO_2}`}>{texto}</span>
    </div>
  );
}

function AvanceTarjeta({ negocio }: { negocio: NegocioVista }) {
  const a = negocio.avance;
  const prom = a.promedio_zona_apariciones;
  return (
    <Tarjeta titulo="Mi avance" accion={<span className={`text-base ${TEXTO_2}`}>{a.periodo}</span>}>
      <div className="grid grid-cols-3 gap-3">
        <Numero texto="veces en rutas de compra" cifra={a.apariciones_ruta} />
        <Numero texto="“Compré aquí”" cifra={a.compre_aqui} />
        <Numero texto="visitas a tu página" cifra={a.vistas_pagina} />
      </div>
      {prom && prom.valor !== null && (
        <p className={`mt-4 text-lg ${TEXTO_2}`}>
          Promedio de tu zona: <strong className="pb-cifra text-(--pb-texto)">{prom.valor}</strong> veces en rutas
        </p>
      )}
      <p className={`mt-2 text-base ${TEXTO_2}`}>Solo tú ves estos números.</p>
    </Tarjeta>
  );
}

const ESCALON: Record<EstadoEscalon, { texto: string; clase: string }> = {
  logrado: { texto: "Logrado", clase: "bg-(--pb-texto) text-(--pb-superficie)" },
  siguiente: { texto: "Tu siguiente paso", clase: "bg-(--pb-acento) text-(--pb-sobre-acento)" },
  pendiente: { texto: "Pendiente", clase: "bg-(--pb-superficie-2) text-(--pb-texto-2)" },
  proximamente: { texto: "Próximamente", clase: "bg-(--pb-superficie-2) text-(--pb-texto-2)" },
  horizonte: { texto: "En el horizonte", clase: "bg-(--pb-superficie-2) text-(--pb-texto-2)" },
};

function EscaleraTarjeta({ escalera }: { escalera: EscalonVista[] }) {
  return (
    <Tarjeta titulo="Tu escalera de barrio">
      {escalera.length === 0 ? (
        <p className={`text-lg ${TEXTO_2}`}>Todavía no hay escalones para este negocio.</p>
      ) : (
        <ol className="flex flex-col gap-3">
          {escalera.map((e) => {
            const est = ESCALON[e.estado];
            const activo = e.estado === "siguiente";
            return (
              <li
                key={e.numero}
                className={`rounded-(--pb-radio-control) p-4 ${activo ? "bg-(--pb-acento-suave)" : "bg-(--pb-superficie-2)/60"}`}
              >
                <div className="flex flex-wrap items-center gap-3">
                  <span aria-hidden="true" className="pb-display text-[1.6rem] font-extrabold leading-none text-(--pb-texto-2)">
                    {e.numero}
                  </span>
                  <h3 className="text-[1.15rem] font-semibold">
                    <span className="sr-only">Escalón {e.numero}: </span>
                    {e.nombre}
                  </h3>
                  <span className={`ml-auto rounded-full px-3 py-1 text-base font-semibold ${est.clase}`}>{est.texto}</span>
                </div>
                {e.beneficio && <p className="mt-2 text-lg">{e.beneficio}</p>}
                {e.siguiente_accion && (
                  <p className={`mt-1 text-lg ${activo ? "font-semibold" : TEXTO_2}`}>Qué sigue: {e.siguiente_accion}</p>
                )}
              </li>
            );
          })}
        </ol>
      )}
      <p className={`mt-3 text-base ${TEXTO_2}`}>Nada aquí es obligatorio ni es un trámite. Tú decides cuándo subir.</p>
    </Tarjeta>
  );
}

const PROGRAMA: Record<EstadoPrograma, string> = {
  existe: "Ya existe",
  por_verificar: "Por confirmar",
  propuesta: "Propuesta",
};

function ProgramasTarjeta({ negocio }: { negocio: NegocioVista }) {
  return (
    <Tarjeta titulo="Programas para ti">
      {negocio.programas.length === 0 ? (
        <p className={`text-lg ${TEXTO_2}`}>Por ahora no encontramos programas para tu negocio.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {negocio.programas.map((p) => (
            <li key={p.id}>
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-lg font-semibold">{p.nombre}</h3>
                <span className="rounded-full bg-(--pb-superficie-2) px-3 py-0.5 text-base font-medium text-(--pb-texto-2)">
                  {PROGRAMA[p.estado]}
                </span>
                {p.puede_entrar && <span className="text-base font-semibold text-(--pb-acento-fuerte)">Puedes entrar</span>}
              </div>
              {p.que_es && <p className="mt-1 text-lg">{p.que_es}</p>}
              {p.como_entrar && <p className={`text-base ${TEXTO_2}`}>Cómo entrar: {p.como_entrar}</p>}
              {p.url_oficial && (
                <a
                  href={p.url_oficial}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 inline-flex min-h-(--pb-alto-control) items-center text-lg font-semibold text-(--pb-acento-fuerte) underline"
                >
                  Sitio oficial
                </a>
              )}
            </li>
          ))}
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

const ENLACE =
  "inline-flex min-h-(--pb-alto-control) items-center justify-center rounded-full border-2 border-(--pb-borde-fuerte) bg-(--pb-superficie) px-5 text-lg font-semibold hover:bg-(--pb-superficie-2)";

function PaginaTarjeta({ id, inicial, offline }: { id: string; inicial: PaginaVista | null; offline: boolean }) {
  const [estado, setEstado] = useState<EstadoPagina>(inicial ? { fase: "lista", pagina: inicial } : { fase: "inicial" });

  const generar = useCallback(() => {
    setEstado({ fase: "generando" });
    api<unknown>(`/negocio/${encodeURIComponent(id)}/pagina`, { method: "POST" })
      .then((datos) => {
        const p = normalizarPagina(datos);
        setEstado(p ? { fase: "lista", pagina: p } : { fase: "error", mensaje: "respuesta sin enlace" });
      })
      .catch((error: unknown) => setEstado({ fase: "error", mensaje: error instanceof Error ? error.message : "sin respuesta" }));
  }, [id]);

  return (
    <Tarjeta titulo="Mi página web">
      {estado.fase !== "lista" && (
        <p className={`mb-4 text-lg ${TEXTO_2}`}>
          Una página sencilla con tus productos, horario y formas de pago, más un cartel con código QR para tu puesto.
        </p>
      )}
      <Boton onClick={generar} disabled={estado.fase === "generando"} aria-busy={estado.fase === "generando"} anchoCompleto>
        {estado.fase === "generando" ? "Generando…" : estado.fase === "lista" ? "Volver a generar" : "Generar mi página"}
      </Boton>
      {estado.fase === "error" && (
        <p role="alert" className="mt-3 text-lg text-(--pb-error)">
          No se pudo generar la página{offline ? " (sin conexión con el servidor)" : ""}. Inténtalo otra vez. ({estado.mensaje})
        </p>
      )}
      {estado.fase === "lista" && (
        <div className="mt-4 flex items-start gap-4">
          {estado.pagina.qr ? (
            <img
              src={estado.pagina.qr}
              alt="Código QR que abre tu página"
              className="size-32 shrink-0 rounded-(--pb-radio-control) border border-(--pb-borde) bg-(--pb-superficie) [image-rendering:pixelated]"
            />
          ) : (
            <p className={`text-base ${TEXTO_2}`}>El código QR aparece al generar tu página.</p>
          )}
          <div className="flex flex-1 flex-col gap-2">
            <a href={estado.pagina.url} target="_blank" rel="noreferrer" className={ENLACE}>
              Ver mi página
            </a>
            <a href={estado.pagina.cartel} target="_blank" rel="noreferrer" className={ENLACE}>
              Imprimir cartel
            </a>
          </div>
        </div>
      )}
    </Tarjeta>
  );
}
