import type { Oferta, Sesion } from "./tipos";

// Datos de demostración: se usan solo si la API aún no responde. Todo lleva demo_data: true.
const ahora = () => new Date().toISOString();

export function sesionMock(id: string): Sesion {
  const impar = Number(id.slice(-1)) % 2 === 1;
  return {
    token: "mock",
    repartidor_id: id,
    nombre_mostrar: "Repartidor de ejemplo",
    transporte: impar ? "moto" : "bici",
    demo_data: true,
  };
}

export function ofertasMock(): Oferta[] {
  return [
    {
      id: "O-DEMO1",
      ts: ahora(),
      negocio_id: "demo-1",
      negocio_nombre: "Fonda Doña Lupe",
      tipo_negocio: "negocio_local",
      origen: { lat: 19.3467, lng: -99.1617 },
      paradas: [
        { lat: 19.3512, lng: -99.1561, colonia: "Del Carmen" },
        { lat: 19.3398, lng: -99.1523, colonia: "Parque San Andrés" },
      ],
      distancia_m: 2400,
      minutos_est: 22,
      pago_est: 68,
      tipo_dato_pago: "simulado",
      colonia: "Del Carmen",
      estado: "abierta",
      demo_data: true,
    },
    {
      id: "O-DEMO2",
      ts: ahora(),
      negocio_id: "demo-2",
      negocio_nombre: "Tortillería La Esperanza",
      tipo_negocio: "negocio_local",
      origen: { lat: 19.3585, lng: -99.1702 },
      paradas: [{ lat: 19.3641, lng: -99.1655, colonia: "Santa Catarina" }],
      distancia_m: 1100,
      minutos_est: 12,
      pago_est: 42,
      tipo_dato_pago: "simulado",
      colonia: "Santa Catarina",
      estado: "abierta",
      demo_data: true,
    },
  ];
}

/** Oferta que "llega" durante la demo para mostrar el polling de 5 s. */
export function ofertaNuevaMock(): Oferta {
  return {
    id: "O-DEMO3",
    ts: ahora(),
    negocio_id: "demo-3",
    negocio_nombre: "Frutería Los Viveros",
    tipo_negocio: "negocio_local",
    origen: { lat: 19.3361, lng: -99.1789 },
    paradas: [
      { lat: 19.3315, lng: -99.1732, colonia: "Los Reyes" },
      { lat: 19.3279, lng: -99.1681, colonia: "Los Reyes" },
      { lat: 19.3302, lng: -99.1604, colonia: "Santo Domingo" },
    ],
    distancia_m: 3100,
    minutos_est: 30,
    pago_est: 85,
    tipo_dato_pago: "simulado",
    colonia: "Los Reyes",
    estado: "abierta",
    demo_data: true,
  };
}
