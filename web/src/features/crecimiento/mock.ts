import type { Crecimiento, Punto } from "./tipos";

// Shown only when the API fails. Everything here is sample data (demo_data: true) and the UI says so.
const trimestres = (base: number): Punto[] =>
  [2023, 2024, 2025].flatMap((anio, i) =>
    [1, 2, 3, 4].map((t, j) => ({ periodo: `${anio}-T${t}`, valor: base + (i * 4 + j) * 9 })),
  );
const anios = (base: number): Punto[] =>
  [2019, 2020, 2021, 2022, 2023, 2024, 2025].map((a, i) => ({
    periodo: String(a),
    valor: base + ((i * 137) % 400),
  }));

const FUENTE_MOCK = "muestra local (sin conexión)";

export const MOCK: Crecimiento = {
  generado: "",
  alcaldias: ["09003", "09007"],
  serie_trimestral: [
    { alcaldia_cvegeo: "09003", alcaldia: "Coyoacán", indicador: "Cuentas de captación por cada 10 mil adultos", puntos: trimestres(260), tipo_dato: "simulado", fuente: FUENTE_MOCK },
    { alcaldia_cvegeo: "09007", alcaldia: "Iztapalapa", indicador: "Cuentas de captación por cada 10 mil adultos", puntos: trimestres(190), tipo_dato: "simulado", fuente: FUENTE_MOCK },
  ],
  altas_negocios_por_anio: [
    { alcaldia_cvegeo: "09003", alcaldia: "Coyoacán", indicador: "Altas de negocios por año", puntos: anios(1200), tipo_dato: "simulado", fuente: FUENTE_MOCK },
    { alcaldia_cvegeo: "09007", alcaldia: "Iztapalapa", indicador: "Altas de negocios por año", puntos: anios(2100), tipo_dato: "simulado", fuente: FUENTE_MOCK },
  ],
  altas_plataforma: { fecha: "", hoy: 0, total: 0, tipo_dato: "simulado", fuente: FUENTE_MOCK, archivo_disponible: false },
  rutas_por_hexagono: { hexagonos: [], total: 0, tipo_dato: "simulado", fuente: FUENTE_MOCK, archivo_disponible: false },
  escala: {
    alcaldias_activas: ["Coyoacán", "Iztapalapa"],
    alcaldias_totales: 16,
    parametro: "ALCALDIAS",
    costo: "Casi cero: bot de Telegram gratuito, datos abiertos de la CDMX e INEGI, código abierto.",
    piezas: [
      "Telegram como canal de alta: sin app que instalar.",
      "Datos abiertos (DENUE, tianguis y mercados SEDECO) como base.",
      "Código abierto: cualquier alcaldía puede correrlo.",
      "Cambiar la variable ALCALDIAS agrega una alcaldía sin tocar código.",
    ],
    tipo_dato: "estimado",
    fuente: FUENTE_MOCK,
  },
  demo_data: true,
};
