import { useEffect, useState } from "react";
import type { FeatureProps } from "../../App";
import { api } from "../../lib/api";
import { Cifra, Etiqueta, Tarjeta } from "../../lib/ui";
import { COLORES } from "./colores";
import { Barras, Lineas, MapaAlcaldias } from "./graficas";
import { MOCK } from "./mock";
import type { Crecimiento } from "./tipos";

export const route = "crecimiento";
export const label = "Crecimiento";
export const order = 4;

const POLL_MS = 5000;

function Fuente({ texto }: { texto: string }) {
  return <p className="mt-3 text-[0.833rem] leading-snug text-(--pb-texto-2)">Fuente: {texto}</p>;
}

function FuenteCorta({ texto }: { texto: string }) {
  return <p className="mt-1.5 text-[0.778rem] text-(--pb-texto-2)">Fuente: {texto}</p>;
}

function Esqueleto() {
  return (
    <div role="status" aria-label="Cargando el panel de crecimiento" className="flex h-full flex-col gap-4 p-5">
      <div className="h-10 w-2/5 animate-pulse rounded-(--pb-radio-control) bg-(--pb-superficie-2)" />
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-28 animate-pulse rounded-(--pb-radio-tarjeta) bg-(--pb-superficie-2)" />
        ))}
      </div>
      <div className="grid flex-1 grid-cols-1 gap-4 lg:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="min-h-48 animate-pulse rounded-(--pb-radio-tarjeta) bg-(--pb-superficie-2)" />
        ))}
      </div>
    </div>
  );
}

function Rutas({ data }: { data: Crecimiento["rutas_por_hexagono"] }) {
  if (data.hexagonos.length === 0) {
    return (
      <p className="text-lg text-(--pb-texto-2)">
        {data.archivo_disponible
          ? "Todavía no hay rutas registradas hoy."
          : "Aún no hay rutas: aparecerán en cuanto una vecina arme la suya."}
      </p>
    );
  }
  const max = Math.max(1, ...data.hexagonos.map((h) => h.rutas));
  return (
    <ol className="grid grid-cols-1 gap-x-8 gap-y-2 md:grid-cols-2" aria-label={`${data.total} paradas de ruta en total`}>
      {data.hexagonos.slice(0, 6).map((h, i) => (
        <li key={h.h3} className="grid grid-cols-[1.5rem_8.5rem_minmax(0,1fr)_2rem] items-center gap-2 text-base">
          <span className="pb-cifra text-(--pb-texto-2)">{i + 1}</span>
          <span className="truncate font-mono text-[0.833rem] text-(--pb-texto-2)" title={`Hexágono ${h.h3}`}>
            {h.h3}
          </span>
          <span className="h-3 overflow-hidden rounded-full bg-(--pb-superficie-2)">
            <span
              className="block h-full rounded-full motion-safe:transition-[width] motion-safe:duration-700"
              style={{ width: `${Math.max(6, (h.rutas / max) * 100)}%`, background: COLORES[0] }}
            />
          </span>
          <span className="pb-cifra text-right font-semibold">{h.rutas}</span>
        </li>
      ))}
    </ol>
  );
}

export default function CrecimientoView(_props: FeatureProps) {
  const [data, setData] = useState<Crecimiento | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let vivo = true;
    const cargar = () =>
      api<Crecimiento>("/sedeco/crecimiento")
        .then((d) => {
          if (!vivo) return;
          setData(d);
          setError(false);
        })
        .catch(() => {
          if (!vivo) return;
          setError(true);
          setData((prev) => prev ?? MOCK);
        });
    cargar();
    const id = window.setInterval(cargar, POLL_MS);
    return () => {
      vivo = false;
      window.clearInterval(id);
    };
  }, []);

  if (!data) return <Esqueleto />;

  const altas = data.altas_plataforma;
  const rutas = data.rutas_por_hexagono;
  const escala = data.escala;
  const trimestral = data.serie_trimestral;
  const anual = data.altas_negocios_por_anio;

  return (
    <div className="h-full overflow-auto bg-(--pb-fondo)">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 sm:px-6">
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-[0.778rem] font-semibold uppercase tracking-[0.14em] text-(--pb-acento)">Panel de crecimiento · SEDECO</p>
            <h1 className="pb-display mt-1 text-[2rem] font-bold sm:text-[2.25rem]">La red crece colonia por colonia</h1>
          </div>
          <p className="max-w-sm text-base leading-snug text-(--pb-texto-2)">
            Cada alta por voz y cada ruta de compra se suman aquí en vivo. Se actualiza cada 5 segundos.
          </p>
        </header>

        {(error || data.demo_data) && (
          <p role="status" className="rounded-(--pb-radio-control) border border-(--pb-borde-fuerte) bg-(--pb-simulado-fondo) px-4 py-2 text-base text-(--pb-simulado-texto)">
            {error && data.generado !== ""
              ? "Sin conexión con el servidor: mostramos los últimos datos recibidos."
              : error
                ? "No pudimos conectar con el servidor. Mostramos datos de muestra (simulados), no son cifras reales."
                : "Modo demo: parte de estos datos son de muestra (simulados)."}
          </p>
        )}

        <section aria-label="Cifras clave" className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Tarjeta className="!px-5 !py-3 ring-2 ring-(--pb-acento-suave)">
            <div aria-live="polite">
              <Cifra valor={altas.hoy} etiqueta="Altas hoy por voz" tipo={altas.tipo_dato} fuente={altas.fuente} tamano="md" />
            </div>
            <FuenteCorta texto="Bot de Telegram · en vivo" />
          </Tarjeta>
          <Tarjeta className="!px-5 !py-3">
            <Cifra valor={altas.total} etiqueta="Altas en total" tipo={altas.tipo_dato} fuente={altas.fuente} tamano="md" />
            <FuenteCorta texto="Plataforma · altas registradas" />
          </Tarjeta>
          <Tarjeta className="!px-5 !py-3">
            <Cifra valor={rutas.total} etiqueta="Paradas de ruta en el barrio" tipo={rutas.tipo_dato} fuente={rutas.fuente} tamano="md" />
            <FuenteCorta texto="Rutas armadas en la plataforma" />
          </Tarjeta>
          <Tarjeta className="!px-5 !py-3">
            <Cifra
              valor={escala.alcaldias_activas.length}
              sufijo={` de ${escala.alcaldias_totales}`}
              etiqueta="Alcaldías activas hoy"
              tipo={escala.tipo_dato}
              fuente={escala.fuente}
              tamano="md"
            />
            <FuenteCorta texto="Diseño del equipo" />
          </Tarjeta>
        </section>

        <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
          <Tarjeta
            antetitulo="Inclusión financiera"
            titulo="Por trimestre"
            accion={<Etiqueta tipo={trimestral[0]?.tipo_dato ?? "simulado"} />}
            className="!p-5"
          >
            <p className="-mt-2 mb-1 text-base text-(--pb-texto-2)">{trimestral[0]?.indicador ?? ""}</p>
            <Lineas series={trimestral} />
            <Fuente texto={trimestral[0]?.fuente ?? "—"} />
          </Tarjeta>

          <Tarjeta
            antetitulo="Negocios nuevos"
            titulo="Altas por año"
            accion={<Etiqueta tipo={anual[0]?.tipo_dato ?? "simulado"} />}
            className="!p-5"
          >
            <p className="-mt-2 mb-1 text-base text-(--pb-texto-2)">Negocios que abrieron cada año</p>
            <Barras series={anual} />
            <Fuente texto={anual[0]?.fuente ?? "—"} />
          </Tarjeta>

          <Tarjeta
            antetitulo="Cómo escala"
            titulo={`A las ${escala.alcaldias_totales} alcaldías`}
            accion={<Etiqueta tipo={escala.tipo_dato} />}
            className="!p-5"
          >
            <div className="flex items-start gap-4">
              <MapaAlcaldias activas={escala.alcaldias_activas} />
              <div className="flex min-w-0 flex-col gap-2 text-base leading-snug">
                <p className="rounded-(--pb-radio-control) bg-(--pb-real-fondo) px-3 py-2 font-semibold text-(--pb-real-texto)">
                  Costo casi cero
                </p>
                <p>
                  Hoy: <strong>{escala.alcaldias_activas.join(" e ")}</strong>. Otra alcaldía = su clave en{" "}
                  <code className="rounded bg-(--pb-superficie-2) px-1.5 font-mono text-[0.833rem]">{escala.parametro}</code>.
                </p>
              </div>
            </div>
            <Fuente texto={escala.fuente} />
          </Tarjeta>
        </div>

        <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <Tarjeta
          antetitulo="Demanda que llega al barrio"
          titulo="Hexágonos por los que más pasan las rutas de compra"
          accion={<Etiqueta tipo={rutas.tipo_dato} />}
          className="!p-5 lg:col-span-2"
        >
          <Rutas data={rutas} />
          <Fuente texto={rutas.fuente} />
        </Tarjeta>
        <Tarjeta antetitulo="Por qué cuesta casi cero" titulo={escala.costo} accion={<Etiqueta tipo={escala.tipo_dato} />} className="!p-5">
          <ul className="flex flex-col gap-1.5 text-base leading-snug text-(--pb-texto-2)">
            {escala.piezas.map((p) => (
              <li key={p} className="flex gap-2">
                <span aria-hidden className="mt-2 size-1.5 shrink-0 rounded-full bg-(--pb-acento)" />
                {p}
              </li>
            ))}
          </ul>
        </Tarjeta>
        </div>
      </div>
    </div>
  );
}
