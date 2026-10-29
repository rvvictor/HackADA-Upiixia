# Cuello de botella

## 1. El cuello de botella del comercio de proximidad

El comercio de barrio (tianguis, mercados y pequeños negocios) no se queda sin clientes por falta de gente en la colonia, sino porque **no puede volverse visible, ni entregar, sin pagar a alguien más ni saber de tecnología**. Son tres trabas encadenadas:

| # | Traba | Qué pasa hoy | Qué ataca colonIA |
|---|---|---|---|
| 1 | **Catálogo digital sin conocimientos técnicos** | Para aparecer en línea hay que llenar formularios, subir fotos y mantener una cuenta. Quien vende nopales y no usa apps no lo hace. Solo 6.7 % de los negocios vendió en línea en 2023 (STyFE CDMX, datos de Censos Económicos 2024; `IDEA.md` §10). | Una nota de voz por Telegram da de alta el negocio: la IA extrae la ficha, la persona confirma con **Así queda** y aparece en el mapa y en una página propia. |
| 2 | **Última milla sin comisiones** | Entregar a domicilio depende de plataformas que cobran comisión o de que el dueño deje el puesto. | Una red de repartidores de la misma colonia (en bici de preferencia) toma ofertas de ruta desde un portal. El repartidor se da de alta por Telegram. Estado: alta en revisión (CO-009), portal en curso. |
| 3 | **Visibilidad y demanda** | Los 1,367 tianguis y 329 mercados registrados no aparecen juntos en un mapa vivo con su oferta (conteos reales, `data/fuentes/tianguis.md` y `mercados.md`). El vecino no sabe qué hay cerca y la alcaldía decide sin ver dónde falta comercio. | Mapa con los tres tipos de negocio por colonia y una ruta de compras que pasa solo por negocios de barrio, nunca por cadenas. |

Por qué es cuello y no solo molestia: sin catálogo no hay pedido; sin pedido no hay ruta que repartir; sin repartidor local, el pedido se va a una plataforma y el valor sale de la colonia. colonIA quita las tres trabas con el mismo gesto: hablarle al celular.

Cuánto cuesta cada traba en pesos: **no verificado**. No tenemos una medición propia ni una fuente citable de comisión de plataformas; por eso no ponemos cifra. Ver `ficha_impacto.md`.

## 2. Los cuellos de la propia solución

Lo que todavía nos frena, dicho claro:

| Cuello | Estado hoy | Qué haría falta |
|---|---|---|
| **Verificación de identidad del repartidor** | En demo está simulada: se da por buena y se borra la foto (`demo_data: true`). Fuera de demo la foto queda en `data/live/ids/` (no versionada) hasta que una persona la revise. | Una persona responsable o un proveedor de verificación; criterio escrito de qué ID vale; borrado tras verificar. |
| **Pago al repartidor** | Fuera de alcance. La app muestra un pago *estimado*, no procesa pagos. | Definir quién paga (negocio, cliente o programa), cómo (efectivo, DiMo, CoDi) y qué pasa en disputas. |
| **Datos de población y de dinero (CNBV)** | **Simulados**: población y negocios por hexágono, y transacciones TPV por alcaldía (`data/fuentes/geo.md`). La actividad por hexágono es estimada sobre ese dato simulado. | Población del Censo (INEGI) y la base de inclusión financiera de la CNBV; recalcular hexágonos. |
| **Negocios del DENUE** | En revisión en la rama `feat/co-004` (Coyoacán e Iztapalapa completas, otras alcaldías en muestra). En `main` los 520 negocios siguen simulados. La cobertura es por círculos desde el centro de cada colonia: puede haber huecos. | Integrar la rama; validar con recorrido en campo. |
| **Horarios de tianguis y mercados** | La fuente no trae horarios de mercados; el horario por defecto está marcado (`horario_por_defecto: true`) y no debe leerse como dato real. | Captura en campo o por las altas de los propios comerciantes. |
| **Aspectos legales** | La priorización por edad y estudiante y el aviso de privacidad están **por validar con asesoría legal** (`docs/legal/priorizacion.md`). | Revisión legal antes de cualquier piloto real. |
| **Premio de la bici** | Propuesta: falta patrocinador y número de rutas (`IDEA-v2.md` §4.4). Todo `simulado` en demo. | Confirmar patrocinador. |
| **Dependencia de modelos externos** | Los IDs de modelo siguen por validar. Mitigado con modelo de respaldo, reglas locales y respuestas grabadas (`DEMO_MODE=1`). | Medir tasa de error de la extracción con voces reales. |
| **Adopción** | No hay usuarios reales todavía. | Piloto con colectivos locales; ver `ruta_30_dias.md`. |
