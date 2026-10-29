// Sample data for Doña Lupe, used ONLY when GET /api/negocio/alta-puesto-de-dona-lupe fails.
// Mirrors app/fixtures/negocio_detalle.json (PB-002). demo_data: true, every figure is "simulado".
// It never stands in for another business: other ids show an error instead.
const simulada = (valor: number) => ({
  valor,
  tipo_dato: "simulado",
  fuente: "Historia simulada de la plataforma",
  periodo: "últimos 7 días",
});

// Same id the bot and scripts/simular_alta.py create: "alta-" + slug of "Puesto de Doña Lupe" (PB-008).
export const DONA_LUPE_ID = "alta-puesto-de-dona-lupe";

export const mockDonaLupe = {
  demo_data: true,
  id: DONA_LUPE_ID,
  origen: "alta",
  ficha: {
    nombre: "Puesto de Doña Lupe",
    tipo: "puesto",
    clase_nombre: "Frutas y verduras frescas",
    descripcion: "Nopales y jitomate frescos en el Tianguis de San Lucas. Abro de 7 a 3. Acepto transferencia.",
    productos: [
      { nombre: "nopales", precio: 20, unidad: "kg" },
      { nombre: "jitomate", precio: 25, unidad: "kg" },
    ],
    dias: [0],
    abre: "07:00",
    cierra: "15:00",
    formas_pago: ["efectivo", "transferencia"],
    acepta_mercomuna: null,
    whatsapp: null,
    colonia: "San Lucas",
  },
  avance: {
    tipo_dato: "simulado",
    apariciones_ruta: simulada(18),
    busquedas: simulada(29),
    compre_aqui: simulada(7),
    vistas_pagina: simulada(8),
    promedio_zona_apariciones: simulada(9.4),
  },
  escalera: [
    {
      numero: 1,
      nombre: "Visible",
      estado: "logrado",
      beneficio: "Apareces en el mapa y en las rutas de tus vecinas.",
      siguiente_accion: "Pon tu cartel con QR en el puesto.",
    },
    {
      numero: 2,
      nombre: "Cobro digital",
      estado: "logrado",
      beneficio: "Cobras con transferencia, DiMo o CoDi, sin comisión.",
      siguiente_accion: "Activa DiMo en la app de tu banco para cobrar con tu número de celular.",
    },
    {
      numero: 3,
      nombre: "Historial",
      estado: "proximamente",
      beneficio: "Tus cobros digitales arman tu historial.",
      siguiente_accion: "Próximamente. No necesitas hacer nada todavía.",
    },
    {
      numero: 4,
      nombre: "Crédito",
      estado: "horizonte",
      beneficio: "Con historial, acceso a crédito justo para tu negocio.",
      siguiente_accion: "Se habilita cuando exista el historial.",
    },
  ],
  programas: [
    {
      id: "mercomuna",
      nombre: "Mercomuna",
      que_es: "Vales de la Ciudad para comprar en negocios de barrio.",
      como_entrar: "Afiliarse con la alcaldía (requisitos por confirmar).",
      url_oficial: "https://www.sedeco.cdmx.gob.mx/",
      estado: "existe",
      puede_entrar: true,
      motivo: "Vendes frutas y verduras en un tianguis.",
    },
    {
      id: "dimo",
      nombre: "DiMo de Banxico",
      que_es: "Cobra con tu número de celular, sin comisión.",
      como_entrar: "Actívalo en la app de tu banco.",
      url_oficial: "https://www.banxico.org.mx/",
      estado: "existe",
      puede_entrar: true,
      motivo: "Ya aceptas transferencia.",
    },
    {
      id: "codi",
      nombre: "CoDi de Banxico",
      que_es: "Cobro con código QR sin comisión.",
      como_entrar: "Actívalo en la app de tu banco.",
      url_oficial: "https://www.banxico.org.mx/",
      estado: "existe",
      puede_entrar: true,
      motivo: null,
    },
    {
      id: "puntos-barrio",
      nombre: "Puntos de barrio",
      que_es: "Puntos para quien compra en negocios de barrio.",
      como_entrar: "Aún no existe: es una propuesta de Pulso Barrial.",
      url_oficial: null,
      estado: "propuesta",
      puede_entrar: null,
      motivo: null,
    },
  ],
  // No page links in the mock: /n/{slug} only exists after a real POST /api/negocio/{id}/pagina.
  pagina: null,
};
