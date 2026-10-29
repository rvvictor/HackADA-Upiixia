import { useEffect, useId, useState } from "react";
import { api } from "../../lib/api";
import { ETIQUETA_TIPO } from "./datos";
import { Barras, Lineas } from "./graficasCrecimiento";
import type { AlcaldiaInfo } from "./puntos";
import type { Crecimiento } from "./tiposCrecimiento";

type Props = { alcaldias: AlcaldiaInfo[]; seleccion: string; onSeleccion: (cve: string) => void };

/** Selector de las 16 alcaldías (prioritarias primero) y tarjeta con serie CNBV y altas por año. */
export function TarjetaAlcaldia({ alcaldias, seleccion, onSeleccion }: Props) {
  const [abierto, setAbierto] = useState(false);
  const idDetalle = useId();
  const [crec, setCrec] = useState<Crecimiento | null>(null);
  useEffect(() => {
    let vivo = true;
    api<Crecimiento>("/sedeco/crecimiento").then((r) => vivo && setCrec(r)).catch(() => undefined);
    return () => {
      vivo = false;
    };
  }, []);
  const a = alcaldias.find((x) => x.cvegeo === seleccion);
  const serie = crec?.serie_trimestral.filter((s) => s.alcaldia_cvegeo === seleccion) ?? [];
  const altas = crec?.altas_negocios_por_anio.filter((s) => s.alcaldia_cvegeo === seleccion) ?? [];
  return (
    <section aria-label="Alcaldía" className="pointer-events-auto w-72 max-w-full rounded-2xl border border-stone-400 bg-white p-2.5 shadow-md">
      <label className="block text-base font-bold text-stone-900" htmlFor="sel-alcaldia">Alcaldía</label>
      <select
        id="sel-alcaldia"
        value={seleccion}
        onChange={(e) => onSeleccion(e.target.value)}
        className="mt-1 w-full rounded-xl border border-stone-400 bg-white px-3 py-2 text-base"
      >
        {alcaldias.map((x) => (
          <option key={x.cvegeo} value={x.cvegeo}>{x.prioridad ? "★ " : ""}{x.nombre}</option>
        ))}
      </select>
      {a && (
        <div className="mt-2 space-y-2 text-base text-stone-900">
          <p>
            {Object.entries(a.puntos_por_tipo).map(([t, n]) => `${n.toLocaleString("es-MX")} ${t}`).join(" · ") || "Sin puntos"}
            <br />
            <span className="text-sm text-stone-800">{ETIQUETA_TIPO[a.tipo_dato]} · Fuente: {a.fuente}</span>
          </p>
        </div>
      )}
      {a && (
        <>
          <button
            type="button"
            aria-expanded={abierto}
            aria-controls={idDetalle}
            onClick={() => setAbierto((v) => !v)}
            className="mt-2 w-full rounded-xl border border-stone-400 px-3 py-1.5 text-base font-semibold text-stone-900 hover:bg-stone-100"
          >
            {abierto ? "Ocultar detalle" : "Ver detalle"}
          </button>
          <div id={idDetalle} hidden={!abierto} className="mt-2 max-h-[28vh] space-y-2 overflow-auto text-base text-stone-900">
          {a.cnbv ? (
            <p>
              Transacciones con tarjeta por adulto: <b>{a.cnbv.tpv_por_adulto ?? "sin dato"}</b> ({a.cnbv.trimestre ?? "s/f"})
              <br />
              <span className="text-sm text-stone-800">{ETIQUETA_TIPO[a.cnbv.tipo_dato] ?? a.cnbv.tipo_dato} · Fuente: {a.cnbv.fuente}</span>
            </p>
          ) : (
            <p className="text-sm text-stone-800">Sin dato CNBV para esta alcaldía.</p>
          )}
          {serie.length > 0 && (
            <>
              <Lineas series={serie} />
              <p className="text-sm text-stone-800">{ETIQUETA_TIPO[serie[0].tipo_dato]} · Fuente: {serie[0].fuente}</p>
            </>
          )}
          {altas.length > 0 && (
            <>
              <Barras series={altas} />
              <p className="text-sm text-stone-800">{ETIQUETA_TIPO[altas[0].tipo_dato]} · Fuente: {altas[0].fuente}</p>
            </>
          )}
          </div>
        </>
      )}
    </section>
  );
}
