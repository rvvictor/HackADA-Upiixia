import { useEffect, useId, useState } from "react";
import { api } from "../../lib/api";
import { Barras, Lineas } from "./graficasCrecimiento";
import type { AlcaldiaInfo } from "./puntos";
import type { Crecimiento } from "./tiposCrecimiento";

type Props = { alcaldias: AlcaldiaInfo[]; seleccion: string; onSeleccion: (cve: string) => void };

// Maqueta viva: white card, tokens only, every figure keeps its source line and no real/simulado chip
// (uak decision CO-028).
const FUENTE = "text-base text-(--pb-texto-2)";

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
    <section aria-label="Alcaldía" className="w-full rounded-(--pb-radio-tarjeta) bg-(--pb-superficie) p-4 shadow-(--pb-sombra)">
      <label className="block text-base font-semibold" htmlFor="sel-alcaldia">
        Alcaldía
      </label>
      <select
        id="sel-alcaldia"
        value={seleccion}
        onChange={(e) => onSeleccion(e.target.value)}
        className="mt-1 min-h-(--pb-alto-control) w-full rounded-(--pb-radio-control) border-2 border-(--pb-borde-fuerte) bg-(--pb-superficie) px-3 text-lg"
      >
        {alcaldias.map((x) => (
          <option key={x.cvegeo} value={x.cvegeo}>
            {x.prioridad ? "★ " : ""}
            {x.nombre}
          </option>
        ))}
      </select>
      {a && (
        <div className="mt-3">
          <p className="text-lg">
            {Object.entries(a.puntos_por_tipo)
              .map(([t, n]) => `${n.toLocaleString("es-MX")} ${t}`)
              .join(" · ") || "Sin puntos"}
          </p>
          <p className={FUENTE}>Fuente: {a.fuente}</p>
        </div>
      )}
      {a && (
        <>
          <button
            type="button"
            aria-expanded={abierto}
            aria-controls={idDetalle}
            onClick={() => setAbierto((v) => !v)}
            className="mt-3 min-h-(--pb-alto-control) w-full rounded-full border-2 border-(--pb-borde-fuerte) px-4 text-base font-semibold hover:bg-(--pb-superficie-2)"
          >
            {abierto ? "Ocultar detalle" : "Ver detalle"}
          </button>
          <div id={idDetalle} hidden={!abierto} className="mt-3 max-h-[28vh] space-y-3 overflow-auto">
            {a.cnbv ? (
              <div>
                <p className="text-lg">
                  Transacciones con tarjeta por adulto:{" "}
                  <strong className="pb-cifra">{a.cnbv.tpv_por_adulto ?? "sin dato"}</strong> ({a.cnbv.trimestre ?? "s/f"})
                </p>
                <p className={FUENTE}>Fuente: {a.cnbv.fuente}</p>
              </div>
            ) : (
              <p className={FUENTE}>Sin dato CNBV para esta alcaldía.</p>
            )}
            {serie.length > 0 && (
              <div>
                <Lineas series={serie} />
                <p className={FUENTE}>Fuente: {serie[0].fuente}</p>
              </div>
            )}
            {altas.length > 0 && (
              <div>
                <Barras series={altas} />
                <p className={FUENTE}>Fuente: {altas[0].fuente}</p>
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}
