/// <reference types="node" />
import assert from "node:assert/strict";
import { test } from "node:test";
import { CAPAS, expresionAltura, expresionColor, propiedadCapa } from "./hex.ts";

// Sin navegador: las rampas se pasan a mano para no leer tokens CSS.
const RAMPA = ["#000001", "#000002", "#000003", "#000004", "#000005"];
(globalThis as { document?: unknown }).document ??= { documentElement: {} };
(globalThis as { getComputedStyle?: unknown }).getComputedStyle ??= () => ({ getPropertyValue: () => "#c9cdd3" });

/** Propiedades leídas con ["get", x] en toda la expresión, sin la bandera de privacidad. */
function propiedadesLeidas(expr: unknown, acc = new Set<string>()): Set<string> {
  if (Array.isArray(expr)) {
    if (expr[0] === "get" && typeof expr[1] === "string") acc.add(expr[1]);
    else expr.forEach((e) => propiedadesLeidas(e, acc));
  }
  return acc;
}
const sinOculto = (s: Set<string>) => [...s].filter((p) => p !== "oculto");

for (const capa of CAPAS) {
  test(`capa ${capa.id}: altura y color leen la misma propiedad`, () => {
    const altura = sinOculto(propiedadesLeidas(expresionAltura(capa.id)));
    const color = sinOculto(propiedadesLeidas(expresionColor(capa.id, RAMPA)));
    assert.deepEqual(altura, [propiedadCapa(capa.id)]);
    assert.deepEqual(color, [propiedadCapa(capa.id)]);
  });
}

test("cada capa lee una propiedad distinta", () => {
  assert.equal(new Set(CAPAS.map((c) => c.propiedad)).size, CAPAS.length);
});
