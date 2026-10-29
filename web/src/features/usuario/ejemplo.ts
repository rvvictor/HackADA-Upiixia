import type { Punto, Ruta } from "./tipos";

// Sede del evento (Utopía Elena Poniatowska Amor, San Lucas, Coyoacán): origen si no hay ubicación.
export const SEDE: Punto = { lat: 19.3486, lng: -99.153 };

export const LISTA_EJEMPLO = "2 kilos de jitomate, tortillas, chiles secos, tenis para niño, pilas";

// Respuesta de ejemplo para cuando la API no responde. Se muestra con la leyenda "datos de ejemplo".
export const RUTA_EJEMPLO: Ruta = {
  paradas: [
    {
      orden: 1,
      negocio: {
        id: "ej-1", nombre: "Abarrotes Lupita", tipo: "negocio", giro: "Abarrotes, ultramarinos y misceláneas",
        lat: 19.3493, lng: -99.1522, h3: null, formas_pago: ["efectivo", "transferencia"], acepta_mercomuna: true,
        tipo_dato: "simulado", impulso: 0.71,
      },
      articulos: ["pilas"],
      por_que: ["Zona con poco movimiento de pago digital (impulso 0.71, estimado)", "A 1 min a pie", "Acepta Mercomuna"],
    },
    {
      orden: 2,
      negocio: {
        id: "ej-2", nombre: "Puesto de Doña Lupe", tipo: "alta", giro: "Frutas y verduras", lat: 19.3501,
        lng: -99.1541, h3: null, formas_pago: ["efectivo", "transferencia"], acepta_mercomuna: null,
        tipo_dato: "simulado", impulso: 0.64,
      },
      articulos: ["2 kilos de jitomate"],
      por_que: ["Se sumó hoy a la red de barrio", "A 3 min a pie"],
    },
    {
      orden: 3,
      negocio: {
        id: "ej-3", nombre: "Tortillería Doña Chela", tipo: "negocio", giro: "Tortillería y molino de nixtamal",
        lat: 19.3478, lng: -99.1556, h3: null, formas_pago: ["efectivo"], acepta_mercomuna: false,
        tipo_dato: "simulado", impulso: 0.4,
      },
      articulos: ["tortillas", "chiles secos"],
      por_que: ["Cubre 2 de tus artículos", "A 4 min a pie"],
    },
    {
      orden: 4,
      negocio: {
        id: "ej-4", nombre: "Calzado El Pípila", tipo: "negocio", giro: "Calzado", lat: 19.3462, lng: -99.1538,
        h3: null, formas_pago: ["efectivo", "dimo"], acepta_mercomuna: false, tipo_dato: "simulado", impulso: 0.55,
      },
      articulos: ["tenis para niño"],
      por_que: ["A 5 min a pie"],
    },
  ],
  geometria: {
    type: "LineString",
    coordinates: [
      [-99.153, 19.3486], [-99.1522, 19.3493], [-99.1541, 19.3501], [-99.1556, 19.3478], [-99.1538, 19.3462],
      [-99.153, 19.3486],
    ],
  },
  distancia_m: 1800,
  minutos: 23,
  resumen: { barrial_pct: 100, cadenas: 0, paradas_impulso: 2 },
  sin_resultado: [],
  aviso: null,
  demo_data: true,
};
