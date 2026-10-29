# Ficha de impacto económico

Regla: **solo hay cifras con fuente y `tipo_dato`.** Lo que no se puede verificar dice "no verificado". No hay ahorros, ingresos ni porcentajes de mejora inventados: colonIA todavía no tiene usuarios reales, así que **no afirmamos un impacto medido**. Lo que sí mostramos es el tamaño del universo al que apunta y cómo lo mediremos.

`tipo_dato`: `real` (de una fuente oficial o publicada), `estimado` (calculado por nosotros, con el cálculo a la vista), `simulado` (inventado para la demo, rotulado así).

## 1. El universo al que apunta (datos de la CDMX)

| Cifra | Valor | `tipo_dato` | Fuente |
|---|---:|---|---|
| Tianguis registrados en la CDMX | 1,367 | real | `data/processed/tianguis_abierto.json`; ficha `data/fuentes/tianguis.md` (archivo `ubicacion_tianguis.csv`, consultado el 2026-10-25; sitio exacto de descarga por confirmar) |
| Mercados públicos | 329 | real | `data/processed/mercados.json`; ficha `data/fuentes/mercados.md` |
| Tianguis en Iztapalapa / Coyoacán | 360 / 137 | real | `data/fuentes/tianguis.md` |
| Mercados en Iztapalapa / Coyoacán | 19 / 24 | real | `data/fuentes/mercados.md` |
| Colonias en el catálogo | 1,543 | real | `data/fuentes/colonias.md` |
| Colonias prioritarias (Coyoacán 98 + Iztapalapa 198) | 296 | real | `data/fuentes/colonias.md` |
| Negocios locales del DENUE (sin cadenas, estratos 0 a 10 personas): Iztapalapa 43,638, Coyoacán 12,033, y 300 por cada una de las otras 14 alcaldías; total 59,871 | 59,871 | real, **en revisión** (rama `feat/co-004`, aún no en `main`) | `data/fuentes/denue.md` en esa rama, INEGI DENUE, descarga del 2026-10-29. Las 14 alcaldías restantes son una muestra, no el total. |
| Negocios simulados con forma de DENUE (los que usa `main` hoy) | 520 | simulado | `data/fuentes/negocios.md` |

Nota de consistencia: `IDEA.md` §10 cita 362 tianguis en Iztapalapa y 136 en Coyoacán (Chilango); el archivo oficial que procesamos da 360 y 137. Usamos el archivo procesado para todo lo que se muestra.

## 2. Cifras citables de contexto (de `IDEA.md` §10)

Verificadas por el equipo el 25-oct-2026 en las fuentes enlazadas; son datos de otros, no resultados de colonIA.

| Cifra | `tipo_dato` | Fuente |
|---|---|---|
| 339 mercados públicos y ~7 millones de clientes por semana | real (citada) | Presentación de retos del Chilangatón 2026 (SEDECO, SECTEI, SAF); documento del evento. Nota: nuestro archivo procesado trae 329 mercados; la diferencia no está explicada. |
| 30.6 % de los negocios usó internet y 6.7 % vendió en línea (2023) | real (citada) | [STyFE CDMX con datos de Censos Económicos 2024](https://deet.trabajo.cdmx.gob.mx/storage/app/media/uploaded-files/b03-censos-economicos-012025docx.pdf) |
| Facturación promedio de tienditas −42.8 % entre 2017 y 2023 (nacional) | real (citada) | [El CEO con datos de ANPEC](https://elceo.com/negocios/tiendas-de-la-esquina-pierden-clientes-sus-ventas-cayeron-42-8-en-un-sexenio/) |
| 700 mil apoyos Mercomuna en 2026 | real (citada) | [Chilango](https://www.chilango.com/noticias/vales-mercomuna-cdmx-entregara-700-mil-apoyos-2026/) |
| Más de 15 mil negocios aceptan vales Mercomuna | real (citada) | [Posta](https://www.posta.com.mx/cdmx/vales-mercomuna-2026-la-lista-completa-de-tiendas-y-mercados-de-cdmx-donde-si-te-los-aceptan/vl2231918) |
| 11,261 millones de pagos con tarjeta y 6.44 billones de pesos en México en 2025 | real (citada) | [Expansión](https://expansion.mx/economia/2026/02/26/tarjetas-bancarias-mueven-record-de-6-4-billones-de-pesos-en-2025-bajo-la-lupa-regulatoria) |
| "Mi Mercado en Casa" (2022) arrancó en 2 mercados con meta de 40 | real (citada) | [Chilango](https://www.chilango.com/noticias/mi-mercado-en-casa-app-con-la-que-mercados-haran-envios-a-domicilio/) |

## 3. Una estimación, con su cálculo

| Cifra | Valor | `tipo_dato` | Cálculo |
|---|---:|---|---|
| Ticket promedio nacional por pago con tarjeta, 2025 | ≈ 572 pesos | **estimado** | 6.44 billones ÷ 11,261 millones de pagos = 571.9. Es un promedio nacional de todos los giros, no de un tianguis; no se usa para proyectar ventas. |

## 4. Lo que la herramienta afectaría y todavía no podemos medir

| Qué | Estado |
|---|---|
| Ventas adicionales de un negocio dado de alta | **no verificado**: sin usuarios reales |
| Ahorro en comisiones de plataformas de reparto | **no verificado**: no tenemos fuente de comisión |
| Ingreso del repartidor por ruta | **simulado**: el pago estimado de la demo no es una tarifa real (`demo_data: true`) |
| Dinero que "se queda en la colonia" | **no verificado**: requiere datos de transacciones reales (CNBV hoy simulada) |
| Población y dinero con tarjeta por hexágono y alcaldía | **simulado** (`data/fuentes/geo.md`); la actividad derivada es `estimado` sobre ese dato |

## 5. Cómo se medirá en el piloto

Indicadores definidos antes de medir, para no ajustar la meta después. Detalle y fechas en `ruta_30_dias.md`.

| Indicador | Cómo se mide | Dato requerido |
|---|---|---|
| Negocios dados de alta por voz y confirmados | Conteo en la plataforma | `real de plataforma` |
| Tiempo de alta | Cronómetro desde la nota de voz hasta **Así queda** | `real de plataforma` |
| Pedidos entregados por repartidores de la colonia | Conteo de rutas completadas | `real de plataforma` |
| Ventas del negocio antes y después | Registro voluntario del comerciante con su consentimiento | declarado, a validar |
| Kilómetros por entrega | Distancia de la ruta | `estimado` |

## 6. Límites honestos

- La demo usa datos simulados en población, dinero y repartidores; cada uno está rotulado en pantalla.
- Un tianguis o mercado registrado no es un negocio activo hoy; el conteo es del registro, no de operación verificada.
- El DENUE es un directorio y puede incluir negocios cerrados o con coordenadas aproximadas.
