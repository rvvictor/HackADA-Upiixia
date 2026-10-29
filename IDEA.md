> **HackADA (nuevo evento):** este archivo viene de Pulso Barrial (Chilangatón 2026) y es la base de partida. La versión original de las tareas está en `docs/historico/`. Se reescribe con el reto nuevo antes de aprobar el backlog.

# IDEA · Pulso Barrial

> Reto: **Reto 1 · Comercio popular y barrial** · Evento: **Chilangatón 2026 (México Tech Week)**, domingo 25 de octubre de 2026, Utopía Elena Poniatowska Amor, Coyoacán, CDMX. Entrega: **18:00 CST** [To validate].
> Etiquetas: **[Decided]** · **[Recommended]** · **[To validate]**.
> Cada número del pitch sale de §10 con su fuente. §4 → tareas verticales · §6 → contrato · §7 → spikes · §8 → criterios de aceptación.
> Este archivo es la fuente de verdad. Si algo de otro documento del equipo lo contradice, manda este archivo.

> **Ajustes del 25-oct a las 12:00 (mandan sobre el resto del archivo):**
> - Corte de la solución **15:00** (se evalúa solo la solución; quien pasa a semifinal tiene 30 min para el pitch). Freeze 13:57, entrega interna 14:43. Formulario: https://forms.gle/4BFrPf49hDGx8Q5s7
> - Rúbrica oficial: la de `.uak/PROJECT.md` (C1–C8, PDF en `docs/`). La tabla de §8 queda solo como referencia.
> - El backlog es `.uak/TASKS.md` (16 tareas), no el Apéndice E. Lo pesado (DENUE, CNBV, Banxico, Censo, diccionario de 2,000 artículos) se **simula** con scripts y cada dato lleva `tipo_dato: "simulado"` visible en la UI.

---

## 0. Nombre y marca (fijo desde T0)

- Nombre: **Pulso Barrial** · repo: `pulso-barrial` · tagline: **"La red viva de la economía de barrio"** (7 palabras). [Decided]
- Renombrar después de T−50% necesita `uak decision` de un humano.
- Idioma de la interfaz: español de México. README de entrega en inglés (regla del modo sprint).

## 1. Una línea

Para **la SEDECO, el vecino y el comerciante de barrio de la CDMX**, donde **solo 6.7% de los negocios vende en línea y 1,367 tianguis no aparecen juntos en ningún mapa vivo**, **Pulso Barrial** les permite **ver dónde se mueve el dinero y dónde falta comercio barrial (SEDECO), armar una ruta de compras que pasa solo por negocios de barrio (vecino) y aparecer en esa red con una nota de voz (comerciante)**, a diferencia de **los mapas estáticos de tianguis, el directorio de Mercomuna en portal y las apps de pedidos que nadie descargó**.

**Ventaja sobre los otros equipos.** Seis IAs distintas, consultadas con el mismo PDF del reto, propusieron casi lo mismo: un bot de WhatsApp que arma la ficha del puesto y un mapa de pines. Esa será la mitad de la sala. Nosotros tenemos tres cosas que casi nadie traerá:

1. Una **herramienta de decisión para gobierno** (mapa de hexágonos con dinero, población y oferta barrial, por día y hora).
2. Una **ruta de compras que redirige demanda** hacia zonas con poco movimiento, sin pasar nunca por una cadena.
3. Un **ciclo cerrado en vivo**: una nota de voz por Telegram da de alta un puesto, aparece en el mapa, entra a las rutas y suma en el tablero de SEDECO, todo en la misma demo.

Posicionamiento: *"La red de negocios del barrio ya existe en la calle. Pulso Barrial la hace visible, medible y conectada."*

## 2. Usuarios

| Persona | Momento | Necesidad | Paso del flujo |
|---|---|---|---|
| **Mtra. Rocío**, JUD de Mercados y Tianguis (alcaldía) | Recibe solicitudes de tianguis nuevos y decide por presión, sin datos | Ver dónde y qué día falta comercio barrial, dónde se mueve el dinero digital y dónde reforzar | 1, 2, 6 |
| **Analista de Mercomuna** (SEDECO / SAPCI) | Hay colonias con muchas beneficiarias y pocos negocios donde canjear | Saber qué zonas priorizar para afiliar negocios | 2, 6 |
| **Karla, 34 años, vecina de Coyoacán** | Sábado por la mañana, con lista del mandado y ropa para su hijo | Una ruta corta a pie que resuelva su lista en negocios de su colonia | 3 |
| **Doña Lupe, 63 años, tianguista** | Pone su puesto de nopales y verdura; no usa apps | Que la encuentren sin llenar formularios ni descargar nada | 4, 5 |
| **Colectivo juvenil INJUVE "Barrio Vivo"** | Recorre su ruta de tianguis con el celular | Dar de alta y verificar puestos rápido, con foto, voz y ubicación | 4 |

## 3. Caso de la demo

**Coyoacán, junto a la sede, más Iztapalapa como contraste.** [Recommended]

- La sede del evento, la Utopía Elena Poniatowska Amor, está en San Lucas, Coyoacán. Los 5 tianguis que el equipo de campo verifica hoy estarán en Coyoacán, así que ese es el dato real más vivo que tendremos.
- Coyoacán tiene 136 tianguis registrados (tercer lugar de la ciudad) e Iztapalapa 362 (primer lugar). Son vecinas: el mapa muestra dos realidades lado a lado.
- El juez de CANACOPE (Leovigildo Chávez López) publicó su propuesta de "economía de barrio" pensada justamente para Coyoacán (ver §11).
- Los datos de CNBV son reales por alcaldía, así que con dos alcaldías el interruptor "Ver dato real" muestra un contraste real, no un solo número.

El pipeline recibe la lista de alcaldías como parámetro (`ALCALDIAS=09003,09007`): si el equipo prefiere solo Iztapalapa, se cambia una línea.

Historia de la demo: Karla vive en un hexágono de Coyoacán con mucha gente y poco movimiento de pago digital. Su ruta pasa por el puesto de Doña Lupe, que se dio de alta hace un minuto con una nota de voz.

## 4. Flujo de la demo (6 pasos, 3 minutos; cada paso = una tarea vertical)

| # | Quien presenta hace | Se ve en pantalla | API | Prio |
|---|---|---|---|---|
| 1 | Abre la vista **SEDECO** | **Wow 1:** hexágonos 3D de Coyoacán e Iztapalapa; altura = actividad estimada de pago con tarjeta, color = índice de impulso. Interruptor "Ver dato real" cambia a las 2 alcaldías con el dato CNBV | `GET /api/hex` · `GET /api/dinero/alcaldias` | P0 |
| 2 | Mueve la barra de domingo a martes y toca un hexágono | Los tianguis se apagan; aparecen los desiertos del martes; % de población cubierta baja. La tarjeta del hexágono muestra cada cifra con etiqueta **real** o **estimado**, fuente y periodo | `GET /api/tianguis?dia=&hora=` | P0 |
| 3 | Cambia a vista **Usuario**, escribe "2 kilos de jitomate, tortillas, chiles secos, tenis para niño, pilas" | **Wow 2:** ruta a pie con 4–5 paradas, todas de barrio; chip "0 cadenas · 1.8 km · 3 paradas en zonas que necesitan clientes"; cada parada dice por qué fue elegida | `POST /api/ruta` | P0 |
| 4 | Un compañero (o el juez) manda una nota de voz al bot de Telegram: "Soy Doña Lupe, vendo nopales a 20 el kilo y jitomate a 25 en el tianguis de aquí, abro de 7 a 3, acepto transferencia" | **Wow 3:** el bot responde con la ficha para confirmar; al confirmar, en ~10 s el puesto aparece en el mapa con su página web generada | bot → `POST /api/altas` · `GET /api/altas/live` | P0 |
| 5 | Abre la vista **Negocio** de Doña Lupe | Su página web, su avance ("apareciste en 1 ruta hoy"), su escalera de barrio y los programas a los que puede entrar (Mercomuna, cobro sin comisión) | `GET /api/negocio/{id}` · `GET /n/{slug}` | P0 |
| 6 | Vuelve a **SEDECO**, panel de crecimiento | Contador "altas hoy" +1, serie trimestral CNBV por alcaldía, altas de negocios por año (DENUE) y rutas que pasaron por cada hexágono | `GET /api/sedeco/crecimiento` | P1 |

- Wow en una frase: *"Una nota de voz de una tianguista la pone en el mapa del gobierno y en la ruta de compras de su vecina, en menos de un minuto."*
- Segundos hasta el primer wow: **≤ 15** (el mapa 3D aparece al abrir).
- Plan B: `DEMO_MODE=1` usa respuestas grabadas de OpenAI, Mapbox y Telegram (`app/fixtures/`), y `scripts/simular_alta.py` inyecta el alta de Doña Lupe si falla la red. Video del flujo completo en `docs/demo/plan-b.mp4`.

## 5. Núcleo técnico

**Regla de oro: el LLM nunca produce una cifra que se muestre.** Interpreta texto y voz, y elige entre opciones dadas. Todo número sale de un cálculo con datos con fuente.

| Pieza | Método | Qué hace el LLM | Qué hace el cálculo |
|---|---|---|---|
| Mapa de dinero | Reparto proporcional del total real CNBV por alcaldía a hexágonos H3 res 9, con peso por tamaño de negocio (DENUE) | Nada | Todo (§A.2) |
| Índice de impulso | `impulso = rank(pob) × (1 − rank(actividad))`, solo si hay comercio barrial en el hexágono | Nada | Todo (§A.3) |
| Cobertura por día | Buffer de 800 m (Turf.js) alrededor de cada punto abierto; suma de población de AGEB cuyo centroide cae dentro | Nada | Todo (§A.4) |
| Artículo → giro | Diccionario de ≥ 2,000 artículos a clases SCIAN + búsqueda difusa; el LLM solo resuelve lo que no está y elige de una lista cerrada | Elegir clase de un enum | Validar contra el enum (§A.5) |
| Ruta | Puntaje por cercanía e impulso, cobertura voraz de artículos y orden con Mapbox Optimization | Nada | Todo (§A.6) |
| Regla anti-cadenas | 4 filtros deterministas + prueba que bloquea el merge | Nada | Todo (§A.7) |
| Alta por voz | Transcripción + extracción estructurada de la ficha; el comerciante confirma antes de publicar | Transcribir y extraer | Validar esquema, ubicar hexágono y tianguis cercano (§A.8) |
| Página web del negocio | Plantilla HTML con datos de la ficha | Redactar una descripción de ≤ 280 caracteres | Generar HTML y QR (§A.9) |

**Validación honesta** (se muestra en el pitch y en `docs/validacion.md`):
- Artículo → giro: 150 artículos con giro esperado (`evals/articulos.csv`), exactitud reportada tal cual (meta ≥ 90%).
- Anti-cadenas: 0 cadenas en `negocios.json` y en 20 rutas de prueba (prueba automática).
- Mapa de dinero: se dice en voz alta que dentro de una alcaldía la diferencia entre hexágonos viene de la densidad de negocios, no de pagos observados.

## 6. Datos (contrato en `app/schemas/`)

Todos los archivos procesados viven en `data/processed/` y se versionan (son pequeños). Los crudos van en `data/raw/` (ignorado por git). Cada fuente deja una ficha en `data/fuentes/<fuente>.md`; `pipeline/fuentes.py` las une en `data/FUENTES.md`.

| Entidad | Archivo | Campos clave | Fuente (licencia) | Tipo |
|---|---|---|---|---|
| Punto barrial (Tianguis Abierto v0.1) | `tianguis_abierto.json` | `id, tipo, nombre, alcaldia_cvegeo, colonia, lat, lng, h3, dias[0-6], abre, cierra, giros[], productos[], formas_pago[], acepta_mercomuna, fuente, fecha_verificacion, verificado_por, tipo_dato` | SEDECO tianguis y mercados (datos abiertos CDMX) + campo + Telegram | Real |
| Negocio | `negocios.json` | `id, clee, nombre, razon_social, clase_scian, clase_nombre, estrato, tipo_establecimiento, lat, lng, h3, alcaldia_cvegeo, colonia, fecha_alta_denue, es_barrial, motivo_exclusion` | DENUE INEGI (términos de libre uso INEGI) | Real |
| Hexágono | `hex.geojson` | `h3, alcaldia_cvegeo, poblacion, negocios_barriales, negocios_total, actividad_tpv_est, monto_est, impulso, cluster_id, oculto, tipo_campos{campo: real\|estimado}, periodo_cnbv` | Derivado | Mixto |
| Dinero por alcaldía | `cnbv_tpv_municipios.json` | `cvegeo, municipio, trimestre, transacciones_tpv, monto_tpv\|null, adultos, tpv_por_adulto, fuente_url, fecha_descarga` | CNBV, Bases de Datos de Inclusión Financiera | Real |
| Ticket por giro | `banxico_ticket_por_giro.json` | `giro, periodo, operaciones, monto, ticket_promedio_est, serie_id, fuente_url` | Banxico SIE | Real + estimado |
| Población | `poblacion_ageb.json` | `cvegeo_ageb, lat, lng, pob_total, pob_18mas, h3` | Censo 2020 INEGI + Marco Geoestadístico | Real |
| Diccionario | `articulo_giro.json` | `articulo, sinonimos[], clases_scian[], categoria_ui` | Construido (§A.5) | Derivado |
| Programas | `programas.json` | `id, nombre, que_es, para_quien, como_entrar, url_oficial, estado(existe\|por_verificar\|propuesta), fecha_verificacion` | Fuentes oficiales | Real / propuesta |
| Alta (en vivo) | `data/live/altas.jsonl` | `id, ts, ficha{...}, lat, lng, h3, origen(telegram\|campo\|demo), verificado_por, consentimiento_publicar, demo_data` | Plataforma | Real de plataforma |
| Evento (en vivo) | `data/live/eventos.jsonl` | `ts, tipo(busqueda\|aparicion_ruta\|compre_aqui\|vista_pagina\|alta), negocio_id, h3, demo_data` | Plataforma | Real de plataforma |
| Historia simulada | `data/demo/plataforma_simulada.json` | Igual que eventos, con `demo_data: true` | Script | **Simulado** |

Reglas del contrato:
- Toda cifra viaja con su etiqueta `tipo_dato` (`real`, `estimado`, `simulado`) y la UI la muestra.
- Nada personal: ni teléfonos ni nombres de personas se publican sin consentimiento explícito en la ficha.
- Esquemas Pydantic en `app/schemas/`, tipos espejo en `web/src/lib/types.ts`, fixtures en `app/fixtures/`.

## 7. IA y APIs externas (cada una = spike de 30 min + respaldo grabado)

**Aviso importante:** `o4-mini` se apagó el 23 de octubre de 2026. Lo que pidió el equipo ("ChatGPT o4") ya no responde en la API. Se usa OpenAI con el reemplazo vigente, y el spike confirma el ID con `GET /v1/models` antes de escribir una sola línea que dependa de él. [Decided: OpenAI · To validate: ID exacto]

| Uso | Modelo / API | Llave | Respaldo |
|---|---|---|---|
| Texto estructurado (interpretar lista, extraer ficha, artículo → giro, descripción) | `OPENAI_MODEL=gpt-5.6-terra` [To validate], respaldo `gpt-5-mini` (disponible hasta 11-dic-2026) | Humano en `.env` | Respuestas grabadas en `app/fixtures/llm/` |
| Voz a texto (notas de voz de Telegram) | `OPENAI_TRANSCRIBE_MODEL=gpt-transcribe` [To validate], respaldo `whisper-1` (hasta feb-2027) | Igual | Transcripción grabada |
| Foto del pizarrón o del puesto | El mismo `OPENAI_MODEL` si acepta imagen [To validate en spike] | Igual | Desactivar foto; pedir voz o texto |
| Mapa base y capas | Mapbox GL JS v3, token público `pk.` | Humano | Estilo guardado + teselas en caché del navegador |
| Ruta a pie | Mapbox Directions `walking` | Igual | Rutas precalculadas para la demo |
| Orden de paradas | Mapbox Optimization v1 `walking`: 2 a 12 coordenadas, 300 peticiones por minuto | Igual | Vecino más cercano en Python |
| Negocios | API DENUE INEGI (`BuscarAreaActEstr`, `Buscar` con radio máx. 5,000 m) | Humano (token por correo) | Descarga masiva del DENUE CDMX (CSV) |
| Bot de campo | Telegram Bot API, long polling (`python-telegram-bot`) | Humano (`@BotFather`) | `scripts/simular_alta.py` |
| Banxico SIE (si pide token) | SieAPIRest con header `Bmx-Token` | Humano si exige registro con correo | Omitir peso por giro (peso = 1) y decirlo |

Reglas de IA (del modo sprint):
- IDs de modelo fijados en `app/config.py`; nadie los escribe en otro archivo.
- Toda salida del LLM pasa por un esquema Pydantic con salida estructurada; si no valida, se reintenta una vez y luego se usa el respaldo.
- El LLM elige de listas cerradas (enum de clases SCIAN presentes en la zona) y cita IDs dados.
- `DEMO_MODE=1` hace que la demo funcione sin internet y sin llaves.
- Mastercard Insights y Visa Spend Signals **no se usan**: el sandbox solo trae datos de prueba.

## 8. Rúbrica → evidencia

La convocatoria pública no publica pesos. Estos criterios salen del documento de retos (soluciones centradas en personas, viables, con recursos accesibles, demostradas con un prototipo; se valoran tecnología + negocio + política pública; se castiga la idea genérica, el usuario indefinido y la falta de camino de validación). **Un humano reemplaza esta tabla con la rúbrica oficial en `/uak-setup`.** [To validate]

| ID | Criterio (provisional) | Peso provisional | Paso o artefacto que lo prueba |
|---|---|---:|---|
| C1 | Problema y usuario definidos | 15 | §2 personas; pasos 1, 3 y 4 con un usuario cada uno |
| C2 | Prototipo funcional y demostrable | 30 | Pasos 1–5 en vivo; alta por voz real; `DEMO_MODE` de respaldo |
| C3 | Viabilidad e implementación (quién mantiene, costos, piloto) | 20 | Diapositiva de implementación: colectivos INJUVE + SEDECO publica el estándar; costo casi cero; piloto Coyoacán–Iztapalapa |
| C4 | Impacto social centrado en personas | 20 | Ruta que manda demanda a zonas con poco movimiento; escalera de barrio; alta por voz para adultos mayores |
| C5 | Innovación (tecnología + negocio + política pública) | 15 | Mapa de dinero por hexágono, estándar abierto Tianguis Abierto, triple hélice |

Cada tarea P0 del backlog lleva `Rubric: C#`.

## 9. Alcance

**Dentro (P0):** vista SEDECO (mapa 3D, barra de tiempo, tarjeta de hexágono), vista Usuario (lista → ruta), bot de Telegram con alta por voz, vista Negocio (ficha, avance, escalera, programas), página web automática, regla anti-cadenas con prueba, `DEMO_MODE`.

**Dentro (P1):** panel de crecimiento, desiertos por día, clusters de barrio, página web con QR imprimible.

**Dentro (P2, solo si sobra tiempo):** brecha Mercomuna, simulador con top 10, exportación KML y consulta "tianguis de hoy".

**Fuera:** login y cuentas (decidido: sin login, selector de rol), pagos, pedidos con entrega, crédito (solo como horizonte en la escalera), WhatsApp Business API (se menciona como siguiente paso del piloto), Mastercard y Visa, cualquier trámite o padrón.

**Simulado con `demo_data: true`:** historia de eventos de la plataforma (búsquedas, rutas, "compré aquí" de días anteriores), muestra de directorio Mercomuna si el equipo de campo no la captura.

**Ética y datos:**
- SEDECO **nunca** ve un negocio con nombre: solo hexágonos agregados; un hexágono con menos de 3 negocios se pinta gris. [Decided]
- El avance del negocio es privado y no muestra ventas ni ingresos; el negocio decide si su ubicación es exacta o aproximada.
- Nada obligatorio ni ligado a trámites, cédulas o padrones (lección de la digitalización de trámites de mercados de 2025).
- Nunca se recomienda una cadena (§A.7).
- Nunca se inventa una cifra: si una fuente o un campo no existe, la tarea lo dice y propone la alternativa más cercana.

---

## 10. Datos citables (verificados el 25-oct-2026)

| Dato | Fuente |
|---|---|
| 339 mercados públicos, ~7 millones de clientes por semana | Presentación de retos del Chilangatón 2026 (SEDECO, SECTEI, SAF), documento del evento |
| 1,367 tianguis; Iztapalapa 362, Gustavo A. Madero 206, Coyoacán 136 | [Chilango, mapa de tianguis CDMX](https://www.chilango.com/noticias/crean-mapa-con-todos-los-tianguis-de-cdmx-ubicaciones-dias-y-horarios/) |
| 30.6% de los negocios usó internet y 6.7% vendió en línea (2023) | [STyFE CDMX con datos de Censos Económicos 2024](https://deet.trabajo.cdmx.gob.mx/storage/app/media/uploaded-files/b03-censos-economicos-012025docx.pdf) |
| Facturación promedio de tienditas −42.8% entre 2017 y 2023 (nacional) | [El CEO con datos de ANPEC](https://elceo.com/negocios/tiendas-de-la-esquina-pierden-clientes-sus-ventas-cayeron-42-8-en-un-sexenio/) |
| 700 mil apoyos Mercomuna en 2026 | [Chilango](https://www.chilango.com/noticias/vales-mercomuna-cdmx-entregara-700-mil-apoyos-2026/) |
| Más de 15 mil negocios aceptan vales Mercomuna | [Posta](https://www.posta.com.mx/cdmx/vales-mercomuna-2026-la-lista-completa-de-tiendas-y-mercados-de-cdmx-donde-si-te-los-aceptan/vl2231918) |
| Directorio oficial de negocios Mercomuna | [comercios-mercomuna.cdmx.gob.mx](https://comercios-mercomuna.cdmx.gob.mx/) |
| 11,261 millones de pagos con tarjeta y 6.44 billones de pesos en México en 2025 | [Expansión](https://expansion.mx/economia/2026/02/26/tarjetas-bancarias-mueven-record-de-6-4-billones-de-pesos-en-2025-bajo-la-lupa-regulatoria) |
| Banxico registra operaciones con tarjeta por giro (minoristas, gasolineras, transporte) | [Publimetro, oct-2026](https://www.publimetro.com.mx/noticias/2026/10/08/pagos-con-tarjeta-invaden-tu-rutina-42-millones-de-operaciones-en-un-dia/) |
| Base CNBV de inclusión financiera: transacciones en TPV por municipio; última actualización confirmada al 2023-2T | [Reporte CNBV](https://www.gob.mx/cms/uploads/attachment/file/810711/ReporteTrimestralBDIF_202209.pdf) · [BBVA Research](https://www.bbvaresearch.com/publicaciones/mexico-en-2023-2t-99-de-adultos-en-municipios-con-punto-de-acceso-creditocaptacion/) |
| BBVA México y el Gobierno CDMX ya miden consumo con datos de terminales (jul-2026) | [BBVA](https://www.bbva.com/es/mx/economia-y-finanzas/bbva-mexico-y-gobierno-cdmx-lanzan-plataforma-unica-que-midio-el-consumo-del-turismo-extranjero-durante-el-mundial/) |
| BBVA ya mapeó la CDMX con celdas hexagonales a partir de transacciones con tarjeta | [BBVA Urban Discovery](https://www.bbva.com/es/innovacion/bbva-reordena-mapas-madrid-barcelona-mexico-ayuda-big-data/) |
| Sede del evento: Utopía Elena Poniatowska Amor, San Lucas, Coyoacán | [Luma del evento](https://luma.com/j55anly0) |
| `o4-mini` apagado el 23 de octubre de 2026 | [Aviso en GitHub](https://github.com/llm-exe/llm-exe/issues/477) · [Lista de apagados](https://dev.to/importstatic/every-openai-model-shutdown-date-until-january-2027-and-what-replaces-it-1dfk) |
| Mapbox Optimization: 2 a 12 coordenadas, 300 peticiones por minuto, perfil `walking` | [Documentación Mapbox](https://docs.mapbox.com/api/navigation/optimization-v1/) |
| API DENUE: radio máximo 5,000 m; estratos 1 = 0–5 y 2 = 6–10 personas | [INEGI](https://www.inegi.org.mx/servicios/api_denue.html) |
| "Mi Mercado en Casa" (2022) arrancó en 2 mercados con meta de 40 | [Chilango](https://www.chilango.com/noticias/mi-mercado-en-casa-app-con-la-que-mercados-haran-envios-a-domicilio/) |
| SEDECO derogó la digitalización de trámites de mercados tras el rechazo de locatarios (2025) | [DPL News](https://dplnews.com/?p=289857) |
| Singapur pasó de 2,300 a 7,800 etiquetas QR en centros de comida en poco más de un año | [MAS](https://www.mas.gov.sg/news/parliamentary-replies/2021/reply-to-parliamentary-question-on-e-payments-and-progress-on-the-roll-out-of-sgqr) |
| Corea: 3.95 billones de wones en vales Onnuri en un año; 65% en mercados tradicionales | [Korea JoongAng Daily](https://koreajoongangdaily.joins.com/korea/korea-revamps-onnuri-gift-certificates-to-attract-tourists-revive-local-markets/12900849) (citada en el PDF del equipo) |
| Propuesta "economía de barrio" del juez Leovigildo Chávez López, pensada para Coyoacán | [Metrópoli Hoy, 2020](https://metropolihoy.com.mx/economia-de-barrio-una-oportunidad-para-la-alcaldia-de-coyoacan-leovigildo-chavez-lopez/) |

Cálculo propio (decirlo así): ticket promedio nacional con tarjeta en 2025 ≈ 6.44 billones ÷ 11,261 millones ≈ **572 pesos por pago**.

---

## 11. El jurado: cómo hablarle al juez de CANACOPE

**Lic. Leovigildo Chávez López** (CANACOPE, Cámara Nacional de Comercio en Pequeño) es jurado del Reto 1. Su propuesta pública, "economía de barrio", es una **visión sin datos ni mecanismo**: convertir colonias en zonas económicas articuladas por **redes de negocios** que formen **clusters**, con formalización, crédito, negocio en casa, adultos mayores con ingreso propio y **movilidad cero** (vivir y trabajar en la misma alcaldía). Su plataforma de 2024 agrega la **triple hélice** (gobierno, empresas, academia), una plataforma digital, mujeres empresarias y jóvenes. Su perspectiva es la de un organizador de comerciantes.

**Nuestra tesis frente a él:** *Pulso Barrial no compite con su visión; es la infraestructura que la vuelve operable y medible.*

| Su concepto | Dónde lo ve en Pulso Barrial | Tarea |
|---|---|---|
| Red de negocios / clusters de servicios | Capa **"Clusters de barrio"** en la vista SEDECO: grupos de hexágonos vecinos con alta densidad de negocios barriales, con número de negocios y giros | PB-020 |
| Zonas económicas de barrio | El mapa de hexágonos con oferta barrial real | PB-011 |
| Formalización (sin imponer) | **Escalera de barrio** voluntaria en la vista Negocio: visible → cobro digital → historial → crédito | PB-017 |
| Local como garantía de crédito | El último escalón: historial digital como garantía alternativa (horizonte, no se ofrece crédito) | PB-017 |
| De empleado a empleador | Avance del negocio y página web: herramientas para crecer | PB-017, PB-018 |
| Negocio en casa, adultos mayores | Alta por nota de voz en Telegram, sin apps ni formularios | PB-016 |
| Movilidad cero | Chip de la ruta: "100% en tu colonia · 1.8 km a pie" | PB-015 |
| Triple hélice | Diapositiva: gobierno (SEDECO, Mercomuna, INJUVE) · comercio (CANACOPE, comerciantes) · academia (el equipo, IPN) | PB-025 |
| Sin presupuesto, solo voluntad | Corre sobre lo que ya existe: Telegram, datos abiertos, directorio Mercomuna | Pitch |

Reglas para el pitch con este juez:
- Usar su vocabulario de forma natural (**economía de barrio, red de negocios, clusters, triple hélice, movilidad cero, de empleado a empleador**) sin citarlo como "su tesis".
- Abrir con una comerciante real (Doña Lupe), no con la tecnología.
- Mencionar el crédito como horizonte: es su tema y casi nadie más lo tocará.
- Decir que los datos que genera Pulso Barrial pueden **informar** decisiones como el uso de suelo mixto (dónde ya hay actividad comercial en colonias habitacionales), sin prometer cambios de uso de suelo ni reformas.
- **No** usar "marginados" ni "clientelares". Mercomuna se presenta como "demanda que fortalece al comercio de barrio".
- **No** proponer nada obligatorio ni ligado a trámites, cédulas o padrones.
- **No** presentar la tecnología como reemplazo del comerciante o de su oficio.

Preguntas probables del jurado y respuesta:

| Pregunta | Respuesta (≤ 20 s) |
|---|---|
| ¿Cómo convencen al comerciante? | Gratis, sin comisión, por voz. Le trae clientes, no trámites. El colectivo lo da de alta en un minuto en su puesto. |
| ¿Esto formaliza o solo digitaliza? | Es una escalera voluntaria: visible, luego cobro digital, luego historial, luego crédito. Cada escalón le conviene por sí mismo. |
| ¿Quién mantiene los datos? | Colectivos juveniles de INJUVE con fecha de verificación, y SEDECO publica el estándar Tianguis Abierto como dato oficial. |
| ¿El mapa de dinero es real? | El total por alcaldía es real (CNBV). El reparto por hexágono es una estimación y lo decimos en cada tarjeta. BBVA y la CDMX ya comparten datos de terminales: con un convenio, el hexágono se vuelve real. |
| ¿Por qué no mandan a la gente al súper si está más cerca? | Porque el objetivo es la economía de barrio: la ruta nunca incluye cadenas y prioriza zonas con poco movimiento, con un desvío máximo de 5 minutos. |
| ¿Qué tan exacta es la cobertura? | Es una aproximación de 800 m alrededor de cada punto abierto; la siguiente fase usa isócronas a pie. |
| ¿Cómo escala? | Todas las fuentes cubren la ciudad; el pipeline recibe la lista de alcaldías como parámetro. |
| ¿Qué papel tiene CANACOPE? | Aliado natural para sumar comerciantes y validar en campo: el lado del comercio en la triple hélice. |
| ¿Y la privacidad? | SEDECO solo ve hexágonos agregados; el negocio decide qué publica; nada de ventas ni ingresos. |

---

## 12. Cómo arrancar (humanos, minuto 0)

Hora actual de referencia: 11:30 CST. Entrega 18:00 [To validate]. Evento de 10 h → congelamiento ≈ 16:30.

```bash
# 1. Repo y kit
mkdir pulso-barrial && cd pulso-barrial && git init -b main
git clone --depth 1 https://github.com/JoahanMorales/upiixia-agentic-kit ~/.uak-kit
bash ~/.uak-kit/install.sh --mode sprint --stack fastapi-react .
cp /ruta/a/este/IDEA.md ./IDEA.md
git remote add origin <url-del-repo> && git add -A && git commit -m "setup: kit + IDEA" && git push -u origin main

# 2. Reloj del evento (calcula el congelamiento)
bash .uak/bin/uak clock "2026-10-25 08:00" "2026-10-25 18:00" America/Mexico_City --write

# 3. Preflight en cada máquina hasta DOCTOR PASS
bash .uak/bin/doctor --fix

# 4. En Claude Code: /uak-setup (llenar PROJECT.md con la rúbrica oficial) y luego /uak-plan
# 5. Arrancar agentes (2 por humano máximo) y mirar el tablero
bash .uak/bin/uak up 4 --tmux
bash .uak/bin/uak board --watch 10
```

`.env` (lo llena un humano en su editor; nunca se pega en el chat):

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-terra
OPENAI_FALLBACK_MODEL=gpt-5-mini
OPENAI_TRANSCRIBE_MODEL=gpt-transcribe
MAPBOX_TOKEN=pk.
DENUE_TOKEN=
TELEGRAM_BOT_TOKEN=
BANXICO_TOKEN=
ALCALDIAS=09003,09007
DEMO_MODE=0
```

En el frontend, el token de Mapbox entra como `VITE_MAPBOX_TOKEN` (token público `pk.`, restringido por URL en Mapbox).

Trabajo de humanos en paralelo (no es tarea de agentes):

| Rol | Ahora | Entrega |
|---|---|---|
| Datos | Token DENUE, token Mapbox, bot de Telegram (`@BotFather`), llave de OpenAI, descargar CSV de tianguis y Censo si el portal bloquea a los agentes | Llaves en `.env` de la máquina demo; archivos en `data/raw/` |
| Campo | 5 tianguis verificados cerca de la Utopía (nombre, calle, día, horario, giros, foto); 30–50 negocios Mercomuna de Coyoacán e Iztapalapa del directorio oficial; 2–3 testimonios con permiso; precios de 3 puestos | `data/campo/tianguis_verificados.csv`, `data/campo/mercomuna_muestra.csv`, fotos en `data/campo/fotos/` |
| Campo (alta real) | Dar de alta por el bot a 3 tianguistas reales con su permiso | Altas reales en `data/live/altas.jsonl` |
| Pitch | Guion de 3 min, máximo 6 diapositivas, ensayo 2 veces | `docs/pitch/` |
| Entrega | Un humano dueño de la entrega desde ya (ya pasó T−8 h) | Recibo de entrega |

---

## Apéndice A · Algoritmos (especificación exacta)

### A.1 Rejilla H3

- Librerías: `h3` (Python, API v4) en el pipeline; `h3-js` v4 en el navegador.
- Resolución **9** (hexágono promedio ≈ 0.105 km²). [Decided]
- `pipeline/hex/grid.py`: une los polígonos de las alcaldías de `ALCALDIAS` (Marco Geoestadístico, capa municipal, probablemente `09mun.shp` [To validate]) y llena con `h3.geo_to_cells(geojson, 9)`.
- Cada negocio, AGEB (centroide) y punto barrial recibe su `h3 = h3.latlng_to_cell(lat, lng, 9)`.

### A.2 Actividad de pago con tarjeta (estimado)

1. `T_a` = transacciones en TPV del último trimestre disponible de la CNBV para la alcaldía `a` (real).
2. Peso de cada establecimiento del DENUE en sectores de comercio al por menor y servicios de consumo (**incluyendo cadenas**, porque el gasto con tarjeta se concentra ahí): punto medio del estrato. `"0 a 5 personas"=3, "6 a 10 personas"=8, "11 a 30 personas"=20, "31 a 50 personas"=40, "51 a 100 personas"=75, "101 a 250 personas"=175, "251 y más personas"=300`.
3. Factor de giro opcional `g_i` = participación del giro en operaciones con tarjeta según Banxico, mapeando sectores SCIAN a las categorías de Banxico. Si la serie no existe o pide un token que no hay, `g_i = 1` y se anota en `data/fuentes/banxico.md`.
4. `actividad_tpv_est(h) = T_a × Σ_{i∈h}(w_i·g_i) / Σ_{i∈a}(w_i·g_i)`.
5. `monto_est(h) = actividad_tpv_est(h) × ticket_promedio_est` solo si Banxico da monto y operaciones; si no, `null`.
6. Etiquetas: `tipo_campos.actividad_tpv_est = "estimado"`, `periodo_cnbv = "2023-T2"` (o el más reciente que encuentre la tarea).
7. Dato real por alcaldía para el interruptor: `tpv_por_adulto = T_a / adultos_a` (adultos del Censo 2020).

### A.3 Índice de impulso

- `rank_pob(h)` y `rank_act(h)` = percentil (0 a 1) dentro de toda la zona de demo.
- `impulso(h) = rank_pob(h) × (1 − rank_act(h))` si `negocios_barriales(h) ≥ 1`; si no, `0`.
- Privacidad: `oculto = negocios_total(h) < 3` → la UI pinta gris y no muestra cifras de dinero.
- Prueba: `pipeline/tests/test_hex.py` comprueba que `Σ_h actividad_tpv_est = T_a` por alcaldía (± 0.5%).

### A.4 Barra de tiempo, cobertura y desiertos

- Abierto en `(dia, hora)`: tianguis si `dia ∈ dias` y `abre ≤ hora < cierra`; mercados según su horario (si no lo hay, 7:00–18:00 marcado "horario supuesto"); negocios DENUE siempre "horario no verificado" (se muestran con trazo punteado).
- Cobertura (navegador, Turf.js): buffer de 800 m alrededor de puntos abiertos; población cubierta = suma de `pob_total` de AGEB cuyo centroide cae dentro; se muestra `% cubierto` del total de la zona.
- Desierto del día: hexágono con `poblacion ≥ p50` sin ningún punto barrial abierto en 800 m ese día.

### A.5 Artículo → giro (alcance amplio)

Alcance [Decided: lo más robusto posible]: todas las clases SCIAN del comercio al por menor (sector 46: abarrotes y alimentos, ropa, calzado, farmacia, papelería, regalos, ferretería, enseres, electrónica, muebles, refacciones), más tortillerías y panaderías tradicionales (sector 31), fondas, cocinas económicas y taquerías (sector 72) y servicios de barrio (sector 81: reparación de calzado, celulares, estéticas, costura). Las claves exactas se toman del catálogo SCIAN de INEGI y de las clases que realmente aparecen en `negocios.json`; ningún agente escribe claves de memoria.

Construcción offline (`pipeline/articulos/`):
1. Lista de clases SCIAN presentes en la zona (de `negocios.json`) + giros de tianguis del CSV de SEDECO.
2. Para cada clase, el LLM propone 20–40 artículos comunes en español de México con sinónimos chilangos (jitomate/tomate, bolillo, chiles secos, tenis, chamarra, foco, pilas, recarga), con salida estructurada. La respuesta se graba en `app/fixtures/llm/articulos_*.json`.
3. Normalización: minúsculas, sin acentos, singular simple, sin cantidades.
4. Se descartan artículos ambiguos que caen en más de 3 clases; los de 2–3 clases se guardan con todas.
5. Meta: **≥ 2,000 artículos**. Un humano revisa una muestra de 50.

En ejecución (`app/services/articulos.py`):
1. Separar la lista: reglas (comas, "y", saltos de línea) y extracción de cantidad/unidad con regex; el LLM solo si la regla deja frases largas.
2. Buscar cada artículo: exacto → sinónimos → difuso con `rapidfuzz` (puntaje ≥ 88).
3. Si no aparece: LLM con salida estructurada cuyo campo `clase` es un **enum** de las clases presentes en la zona, más `"ninguna"`.
4. `"ninguna"` → el artículo se reporta en `sin_resultado` con la frase "No encontramos comercio de barrio para X".
5. Eval: `evals/articulos.csv` (150 artículos, incluidos 30 difíciles). `uv run python evals/articulos.py --min-accuracy 0.9`.

### A.6 Ruta de compras

Entrada: `origen{lat,lng}`, `texto_lista`, `dia`, `hora` (por defecto ahora), `radio_m=1500`, `alpha=0.6`, `regresar=true`.

1. Candidatos por artículo: negocios con `es_barrial=true` cuya clase coincide, más puntos barriales de Tianguis Abierto cuyos giros coinciden y que están abiertos en `(dia, hora)`, a ≤ `radio_m` en línea recta.
2. Tiempo estimado a pie: `t = distancia_linea_recta × 1.3 / 80 m/min`.
3. Puntaje: `puntaje = alpha × (1 − t/t_max) + (1 − alpha) × impulso(h)`; `t_max` = tiempo del candidato más lejano.
4. Desvío máximo: si el elegido tarda más de 5 min que el candidato más cercano, se usa el más cercano.
5. Cobertura voraz: mientras queden artículos sin cubrir, elegir el negocio que maximiza `artículos_cubiertos × puntaje_promedio`; máximo 10 paradas (Optimization admite 12 coordenadas, incluido el origen).
6. Orden: Mapbox Optimization `walking`, `roundtrip=true` si `regresar`, si no `source=first` y `destination=last`; geometría GeoJSON. Respaldo: vecino más cercano + Directions; sin red: líneas rectas y aviso.
7. "Por qué esta parada": plantilla con datos calculados, no LLM. Ejemplos: "Zona con poco movimiento de pago digital (impulso 0.82, estimado)", "Cubre 3 de tus artículos", "Acepta Mercomuna".
8. Resumen: `% barrial`, `cadenas: 0`, distancia y tiempo totales, paradas en hexágonos de impulso alto (≥ p70).
9. Cada parada registra `aparicion_ruta` en `eventos.jsonl`.
10. Invariante: `assert all(p.es_barrial for p in paradas)`; si falla, la API responde 500 (nunca entrega una cadena).

### A.7 Regla anti-cadenas

Un establecimiento es barrial solo si pasa los 4 filtros:
1. **Giro:** se excluyen supermercados (**462111**), minisúpers y tiendas de conveniencia (**462112**), tiendas departamentales y de autoservicio (claves confirmadas por la tarea en el catálogo SCIAN).
2. **Tamaño:** `Estrato ∈ {"0 a 5 personas", "6 a 10 personas"}`.
3. **Nombre:** lista negra con coincidencia difusa (`rapidfuzz.partial_ratio ≥ 90`) sobre `Nombre` y `Razon_social`, en `pipeline/denue/cadenas.txt`: OXXO, 7-ELEVEN, 7 ELEVEN, CIRCLE K, EXTRA, KIOSKO, WALMART, BODEGA AURRERA, MI BODEGA, SORIANA, CHEDRAUI, LA COMER, CITY MARKET, FRESKO, SUPERAMA, TIENDAS 3B, NETO, SMART, FARMACIAS GUADALAJARA, FARMACIAS DEL AHORRO, FARMACIAS SIMILARES, FARMACIA SAN PABLO, BENAVIDES, COPPEL, ELEKTRA, WOOLWORTH, DEL SOL, SUBURBIA, LIVERPOOL, SEARS, SANBORNS, MCDONALDS, BURGER KING, KFC, STARBUCKS, DOMINOS, LITTLE CAESARS, TELCEL, AT&T, MOVISTAR. La lista se puede ampliar.
4. **Repetición:** si el mismo `Nombre` normalizado o `Razon_social` aparece ≥ 5 veces en la CDMX, es cadena.

Siempre entran: mercados públicos, tianguis, altas del bot y del equipo de campo. `motivo_exclusion` guarda el filtro que excluyó a cada establecimiento. El campo `Tipo` del DENUE (fijo o semifijo) se conserva para mostrar "puesto semifijo" [To validate valores].

Pruebas: `pipeline/tests/test_sin_cadenas.py` (0 nombres de la lista en `negocios.json` con `es_barrial=true`) y `app/tests/test_ruta_sin_cadenas.py` (20 rutas de ejemplo). Si fallan, no hay merge.

### A.8 Bot de Telegram (alta y actualización por voz)

- Proceso aparte: `uv run python -m app.bot` (long polling; no necesita URL pública).
- Menú `/start`: **Dar de alta negocio** · **Actualizar mi negocio** · **Verificar tianguis**.
- Acepta nota de voz, texto, foto y ubicación (mensaje de ubicación de Telegram). La ubicación es obligatoria para un alta.
- Flujo de alta:
  1. Voz → transcripción (`OPENAI_TRANSCRIBE_MODEL`).
  2. Texto o transcripción (+ foto si la hay) → ficha con salida estructurada: `nombre, clase_scian (enum), productos[{nombre, precio?, unidad?}], dias[], abre, cierra, formas_pago[enum: efectivo, transferencia, dimo, codi, tarjeta], acepta_mercomuna (bool|null)`.
  3. Se asocia al tianguis más cercano abierto ese día a ≤ 150 m, si lo hay.
  4. El bot responde con la ficha en texto y botones **"Así queda"** / **"Corregir"**. Nada se publica sin "Así queda".
  5. Al confirmar: `POST /api/altas` → `data/live/altas.jsonl`, evento `alta`, página web generada, y el bot devuelve el link de la página y el link privado del panel del negocio.
- Privacidad: no se guarda teléfono ni nombre de la persona salvo que lo diga para su ficha; las fotos solo se publican si el comerciante acepta.
- Respaldo de demo: `scripts/simular_alta.py --caso dona-lupe` usa la ficha grabada.
- Siguiente paso del piloto (se dice en el pitch, no se construye): el mismo flujo en WhatsApp Business.

### A.9 Página web automática

- `POST /api/negocio/{id}/pagina` → genera `data/live/paginas/{slug}.html` con Jinja2 (`app/templates/pagina.html`) y un QR (`qrcode`) que apunta a `/n/{slug}`.
- Contenido: nombre, giro, descripción (LLM, ≤ 280 caracteres, solo con datos de la ficha; respaldo: plantilla fija), productos con precio y fecha, horario, mapa estático de Mapbox, formas de pago, "Acepta Mercomuna", botón de WhatsApp (`wa.me`) solo si el negocio dio su número.
- `GET /n/{slug}` sirve la página; cada visita registra `vista_pagina`.
- Cartel imprimible: `GET /n/{slug}/cartel` con QR grande y "Aceptamos transferencia / DiMo".

### A.10 Clusters de barrio (la "red de negocios")

- Hexágonos con `negocios_barriales ≥ 8` (umbral en config).
- Componentes conexos usando vecinos H3 (`h3.grid_disk(h, 1)`).
- Cada cluster: `cluster_id`, número de negocios, número de giros distintos, tianguis y mercados dentro.
- En el mapa: contorno grueso con etiqueta "Red de barrio: 214 negocios · 18 giros" (cifras calculadas).

### A.11 Simulador y top 10 (P2)

- Clic en el mapa = tianguis hipotético en ese punto y día; se recalcula cobertura.
- Top 10: algoritmo voraz de máxima cobertura sobre centroides de hexágonos candidatos (desiertos del día), sumando población nueva cubierta a 800 m.

---

## Apéndice B · Estructura del repo y dueños de archivos

```text
app/
  main.py · config.py                       # PB-001 (nadie más los edita)
  schemas/ · fixtures/                      # PB-002
  routers/<f>.py · services/<f>.py · tests/test_<f>.py   # una tarea por <f>
  bot/                                      # PB-016
  templates/pagina.html                     # PB-018
pipeline/
  base/ · denue/ · dinero/ · hex/ · articulos/ · tests/   # una tarea por carpeta
  fuentes.py                                # PB-009 (une data/fuentes/*.md)
data/
  raw/ (git-ignored) · processed/ · fuentes/ · campo/ · demo/ · live/ (git-ignored)
web/
  DESIGN.md · src/index.css                 # PB-003
  src/App.tsx · src/main.tsx · src/lib/api.ts · src/lib/types.ts   # PB-001 / PB-002
  src/lib/map/                              # PB-010 (componente de mapa compartido)
  src/features/shell/                       # PB-010 (selector de rol, layout, rutas por hash)
  src/views/sedeco/mapa/ · tiempo/ · crecimiento/ · clusters/
  src/views/usuario/ · src/views/negocio/
evals/ · scripts/ · spikes/ · docs/pitch/ · docs/demo/
```

Rutas del frontend (hash, sin login): `#/sedeco`, `#/usuario`, `#/negocio/:id`. El selector de rol está siempre visible arriba.

Configuración de pruebas: `PB-001` agrega `pipeline/tests` a `testpaths` en `pyproject.toml`.

## Apéndice C · API

| Método | Ruta | Devuelve | Tarea |
|---|---|---|---|
| GET | `/api/health` | `{status}` | PB-001 |
| GET | `/api/hex` | GeoJSON de hexágonos con propiedades y `tipo_campos` | PB-011 |
| GET | `/api/dinero/alcaldias` | CNBV por alcaldía (real) | PB-011 |
| GET | `/api/tianguis?dia=0-6&hora=HH:MM` | Puntos barriales abiertos | PB-012 |
| GET | `/api/negocios?h3=&clase=` | Negocios barriales (sin datos personales) | PB-014 |
| POST | `/api/articulos/interpretar` | `{items[{texto, cantidad, unidad, clases[], fuente}], sin_resultado[]}` | PB-013 |
| POST | `/api/ruta` | `{paradas[{negocio, articulos[], por_que[], orden}], geometria, distancia_m, minutos, resumen{barrial_pct, cadenas, paradas_impulso}, sin_resultado[], demo_data}` | PB-014 |
| POST | `/api/eventos` | Registra `compre_aqui` y `busqueda` | PB-014 |
| POST | `/api/altas` | Crea alta desde bot o campo | PB-016 |
| GET | `/api/altas/live?desde=ts` | Altas nuevas (la UI pregunta cada 3 s) | PB-016 |
| GET | `/api/negocio/{id}` | Ficha, avance, escalera, programas | PB-017 |
| PUT | `/api/negocio/{id}/ficha` | Edita ficha | PB-017 |
| POST | `/api/negocio/{id}/pagina` | Genera página y QR | PB-018 |
| GET | `/n/{slug}` · `/n/{slug}/cartel` | Página del negocio | PB-018 |
| GET | `/api/sedeco/crecimiento` | Series CNBV, altas DENUE por año, altas de plataforma, rutas por hexágono | PB-019 |
| GET | `/api/clusters` | Clusters de barrio | PB-020 |
| GET | `/api/feed/tianguis_abierto.{json,csv,kml}` | Estándar abierto | PB-023 |

## Apéndice D · Pantallas

**Diseño.** `PB-003` hace el design lock: 3 direcciones con capturas a 1280×720, el humano elige una. Recomendación: base clara y sobria tipo documento público, un acento cálido de mercado para el impulso y una paleta secuencial para la actividad; todos los colores como tokens CSS; legible en proyector. Cada número en pantalla lleva su fuente (tooltip o nota al pie) y su etiqueta real/estimado/simulado.

**SEDECO** (`#/sedeco`), a 1280×720 sin scroll:
- Izquierda 70%: mapa Mapbox con hexágonos `fill-extrusion` (altura = actividad estimada, color = impulso). Cámara inicial inclinada 50° sobre Coyoacán con Iztapalapa a la vista.
- Derecha 30%: selector de capa (actividad · oferta barrial · población · impulso · clusters), interruptor "Ver dato real" (coropleta de 2 alcaldías con `tpv_por_adulto`), barra lun–dom con reloj, `% población cubierta`, contador "altas hoy".
- Tarjeta al tocar un hexágono: población (real), negocios barriales (real), actividad con tarjeta (estimado), impulso (estimado), periodo CNBV, fuente. Hexágono oculto: "Menos de 3 negocios: sin cifras por privacidad".
- Pestaña Crecimiento (P1): serie trimestral CNBV por alcaldía, altas DENUE por año (`Fecha_Alta`), altas de plataforma hoy, rutas por hexágono.

**Usuario** (`#/usuario`):
- Mapa de su zona (botón "Usar mi ubicación" o colonia).
- Caja de texto grande con ejemplo: "2 kilos de jitomate, tortillas, tenis para niño…" y botón **Armar mi ruta**.
- Resultado: ruta dibujada, lista de paradas con artículos, chips de pago y Mercomuna, "por qué esta parada", resumen con "0 cadenas · 100% en tu colonia", artículos sin resultado, botón **Compartir por WhatsApp** (link `wa.me` con texto de la ruta) y **Compré aquí** por parada.
- Estados: vacío, cargando ("Buscando en los negocios de tu barrio…"), error, datos de ejemplo etiquetados.

**Negocio** (`#/negocio/:id`, selector de negocio en la demo):
- Ficha editable.
- Mi avance (privado): apariciones en búsquedas y rutas, "compré aquí", visitas a su página; últimos 7 días; comparación con el promedio de su zona.
- **Escalera de barrio:** 1 Visible (ficha publicada) → 2 Cobro digital (acepta transferencia, DiMo o CoDi) → 3 Historial (próximamente) → 4 Crédito (horizonte). Cada escalón con estado, beneficio y siguiente acción.
- Programas (`programas.json`): Mercomuna (existe; requisitos de afiliación por confirmar), DiMo y CoDi de Banxico (existe), condiciones especiales de Banxico para tarjeta en abarrotes (existe, condiciones por confirmar), "Crece tu Mipyme con pagos digitales" (por verificar; no se muestra si no se verifica), Puntos de barrio (**propuesta**, inspirada en Onnuri y PayPay).
- Página web: botón **Generar mi página**, vista previa, QR, cartel imprimible.
- Configuración: ubicación exacta o aproximada (centro del hexágono), aparecer en rutas, botón de WhatsApp, compartir datos agregados con SEDECO.

---

## Apéndice E · Backlog sugerido para `/uak-plan`

El planificador lo convierte en `.uak/TASKS.md` con el formato del kit. Evento corto: máximo 2 tareas por agente, cada una ≤ 60 min. Ola 1 = todas las tareas sin `Depends on`. Prefijo `PB`.

| ID | Tarea | Tipo | P | Est. | Rúbrica | Depends on | Uses contract | Paths principales | Verify |
|---|---|---|---|---|---|---|---|---|---|
| PB-001 | Setup FastAPI + React + todas las dependencias + smoke | setup | P0 | 30 min | C2 | None | — | `pyproject.toml, uv.lock, app/main.py, app/config.py, web/package*.json, web/vite.config.ts, web/src/App.tsx, web/src/main.tsx, web/src/lib/api.ts, .env.example, .gitignore` | `bash .uak/bin/smoke` |
| PB-002 | Contrato: esquemas Pydantic, tipos TS, fixtures y mocks de todas las entidades y APIs | contract | P0 | 40 min | C2 | None | — | `app/schemas/, app/fixtures/, web/src/lib/types.ts, data/demo/` | `uv run pytest -q app/tests/test_schemas.py` |
| PB-003 | Design lock: 3 direcciones, DESIGN.md, tokens | contract | P0 | 45 min | C2 | None | — | `web/DESIGN.md, web/src/index.css, web/public/design-lock/` | `test -s web/DESIGN.md` |
| PB-004 | Spike OpenAI: confirmar IDs con `/v1/models`, salida estructurada, transcripción, imagen; grabar respuestas | spike | P0 | 30 min | C2 | None | — | `spikes/openai/, app/fixtures/llm/` | `uv run python spikes/openai/spike.py --check` |
| PB-005 | Spike Mapbox: Directions y Optimization `walking` con 12 coordenadas; grabar | spike | P0 | 30 min | C2 | None | — | `spikes/mapbox/, app/fixtures/mapbox/` | `uv run python spikes/mapbox/spike.py --check` |
| PB-006 | Pipeline base: tianguis, mercados, Censo AGEB, marco geo → `tianguis_abierto.json`, `poblacion_ageb.json`, campo | feature | P0 | 60 min | C1 | None | PB-002 | `pipeline/base/, data/processed/tianguis_abierto.json, data/processed/poblacion_ageb.json, data/fuentes/base.md` | `uv run pytest -q pipeline/tests/test_base.py` |
| PB-007 | Pipeline DENUE + regla anti-cadenas → `negocios.json` | feature | P0 | 60 min | C4 | None | PB-002 | `pipeline/denue/, data/processed/negocios.json, data/fuentes/denue.md, pipeline/tests/test_sin_cadenas.py` | `uv run pytest -q pipeline/tests/test_sin_cadenas.py` |
| PB-008 | Pipeline dinero: CNBV por alcaldía + Banxico por giro | feature | P0 | 60 min | C5 | None | PB-002 | `pipeline/dinero/, data/processed/cnbv_tpv_municipios.json, data/processed/banxico_ticket_por_giro.json, data/fuentes/dinero.md` | `uv run pytest -q pipeline/tests/test_dinero.py` |
| PB-009 | Hexágonos: actividad estimada, impulso, privacidad, clusters + `FUENTES.md` | feature | P0 | 60 min | C5 | PB-006, PB-007, PB-008 | — | `pipeline/hex/, pipeline/fuentes.py, data/processed/hex.geojson, data/FUENTES.md, pipeline/tests/test_hex.py` | `uv run pytest -q pipeline/tests/test_hex.py` |
| PB-010 | Shell + mapa base: selector de rol, rutas por hash, componente Mapbox | feature | P0 | 45 min | C2 | None | PB-002, PB-003 | `web/src/features/shell/, web/src/lib/map/` | `npm --prefix web run build` |
| PB-011 | Vista SEDECO mapa: hexágonos 3D, capas, "Ver dato real", tarjeta | feature | P0 | 60 min | C5 | None | PB-002, PB-010 | `app/routers/hex.py, app/services/hex.py, app/tests/test_hex_api.py, web/src/views/sedeco/mapa/` | `uv run pytest -q app/tests/test_hex_api.py && npm --prefix web run build` |
| PB-012 | Vista SEDECO tiempo: barra lun–dom, cobertura 800 m, desiertos | feature | P0 | 60 min | C1 | None | PB-002, PB-010 | `app/routers/tianguis.py, app/services/tianguis.py, app/tests/test_tianguis.py, web/src/views/sedeco/tiempo/` | `uv run pytest -q app/tests/test_tianguis.py && npm --prefix web run build` |
| PB-013 | Artículos → giro: diccionario ≥ 2,000 + LLM con enum + eval | feature | P0 | 60 min | C4 | None | PB-002, PB-004 | `pipeline/articulos/, data/processed/articulo_giro.json, app/routers/articulos.py, app/services/articulos.py, app/tests/test_articulos.py, evals/` | `uv run python evals/articulos.py --min-accuracy 0.9` |
| PB-014 | API de ruta: candidatos, puntaje, cobertura voraz, Mapbox, invariante sin cadenas, eventos | feature | P0 | 60 min | C4 | None | PB-002, PB-005, PB-013 | `app/routers/ruta.py, app/services/ruta.py, app/services/mapbox.py, app/routers/eventos.py, app/tests/test_ruta.py, app/tests/test_ruta_sin_cadenas.py` | `uv run pytest -q app/tests/test_ruta.py app/tests/test_ruta_sin_cadenas.py` |
| PB-015 | Vista Usuario: lista → ruta, paradas, por qué, compartir, compré aquí | feature | P0 | 60 min | C1 | None | PB-002, PB-010, PB-014 | `web/src/views/usuario/` | `npm --prefix web run build` |
| PB-016 | Bot de Telegram: alta por voz/texto/foto/ubicación, confirmación, `/api/altas`, live | feature | P0 | 60 min | C2 | None | PB-002, PB-004 | `app/bot/, app/routers/altas.py, app/services/altas.py, app/tests/test_altas.py, scripts/simular_alta.py` | `uv run pytest -q app/tests/test_altas.py` |
| PB-017 | Vista Negocio: ficha, avance, escalera, programas, configuración | feature | P0 | 60 min | C4 | None | PB-002, PB-010 | `app/routers/negocio.py, app/services/negocio.py, app/tests/test_negocio.py, data/processed/programas.json, web/src/views/negocio/` | `uv run pytest -q app/tests/test_negocio.py && npm --prefix web run build` |
| PB-018 | Página web automática + QR + cartel | feature | P0 | 45 min | C4 | None | PB-002, PB-004 | `app/routers/paginas.py, app/services/paginas.py, app/templates/, app/tests/test_paginas.py` | `uv run pytest -q app/tests/test_paginas.py` |
| PB-019 | Panel de crecimiento SEDECO | feature | P1 | 45 min | C3 | None | PB-002, PB-010 | `app/routers/crecimiento.py, app/services/crecimiento.py, app/tests/test_crecimiento.py, web/src/views/sedeco/crecimiento/` | `uv run pytest -q app/tests/test_crecimiento.py && npm --prefix web run build` |
| PB-020 | Clusters de barrio en el mapa | feature | P1 | 30 min | C5 | PB-009 | PB-010 | `app/routers/clusters.py, app/tests/test_clusters.py, web/src/views/sedeco/clusters/` | `uv run pytest -q app/tests/test_clusters.py` |
| PB-021 | Integración: datos reales del pipeline en todas las vistas, `DEMO_MODE`, historia simulada | integration | P0 | 45 min | C2 | PB-009, PB-011, PB-014, PB-016 | — | `app/services/demo.py, scripts/generar_historia.py, data/demo/plataforma_simulada.json, app/tests/test_demo.py` | `DEMO_MODE=1 uv run pytest -q app/tests/test_demo.py` |
| PB-022 | Brecha Mercomuna | feature | P2 | 45 min | C3 | PB-009 | PB-010 | `app/routers/brecha.py, app/tests/test_brecha.py, web/src/views/sedeco/brecha/` | `uv run pytest -q app/tests/test_brecha.py` |
| PB-023 | Feed Tianguis Abierto: JSON, CSV, KML + esquema documentado | feature | P2 | 30 min | C5 | None | PB-002 | `app/routers/feed.py, app/tests/test_feed.py, docs/tianguis-abierto.md` | `uv run pytest -q app/tests/test_feed.py` |
| PB-024 | Simulador y top 10 | feature | P2 | 60 min | C3 | PB-012 | — | `web/src/views/sedeco/simulador/` | `npm --prefix web run build` |
| PB-025 | Demo y entrega: ensayo, video plan B, README en inglés, 6 diapositivas | demo | P0 | 60 min | C1–C5 | PB-021 | — | `docs/demo/, docs/pitch/, README.md` | `test -s docs/demo/guion.md` |

`PB-025` lleva `Freeze-Allowed: yes`.

Hay 20 tareas P0. Con menos de 8 agentes, recorten así antes de aprobar el backlog: PB-008 solo CNBV (sin Banxico), PB-012 solo la barra de tiempo (sin cobertura ni desiertos) y PB-017 sin configuración. El cartel imprimible de PB-018 pasa a P1.

Criterios de aceptación clave (el planificador los copia a cada tarea):
- PB-007: `negocios.json` existe, 0 nombres de la lista negra con `es_barrial=true`, cada registro con `h3` y `motivo_exclusion` si aplica.
- PB-009: suma de actividad por alcaldía = total CNBV (± 0.5%); hexágonos con `negocios_total < 3` tienen `oculto=true`; cada campo con su `tipo_campos`.
- PB-013: exactitud ≥ 0.9 en `evals/articulos.csv`; ninguna clase fuera del enum.
- PB-014: para la lista de la demo devuelve 4–6 paradas, 0 cadenas, ruta en < 3 s con fixtures; artículo inexistente aparece en `sin_resultado`.
- PB-016: una nota de voz grabada (`app/fixtures/telegram/voz_dona_lupe.ogg`) produce una ficha válida; sin "Así queda" no hay alta.
- PB-021: con `DEMO_MODE=1` y sin internet, los 6 pasos de §4 funcionan.

## Apéndice F · Reloj de hoy (CST) [To validate con `uak clock`]

| Hora | Qué |
|---|---|
| 11:30–12:00 | Instalar kit, `/uak-setup`, llaves en `.env`, `/uak-plan`, aprobar backlog |
| 12:00–12:45 | Ola 1: setup, contrato, design lock, spikes, pipelines, shell; campo sale a verificar tianguis |
| 12:45–14:30 | Ola 2: vistas SEDECO, Usuario, Negocio, bot, ruta |
| 14:30 | Esqueleto completo de punta a punta hasta el wow (con mocks etiquetados) |
| 15:00 | Video plan B v1; ola 3 (P1) |
| 16:30 | **Congelamiento**: solo tareas `Freeze-Allowed` |
| 16:30–17:30 | Ensayo cronometrado desde clon limpio, video final, diapositivas |
| 17:30 | Entrega interna y recibo guardado |

## Apéndice G · Guion del pitch (3 min)

| Tiempo | Qué se dice / se muestra |
|---|---|
| 0:00–0:20 | "Doña Lupe vende nopales en un tianguis a 10 minutos de aquí. Hace 20 años que su red de clientes vive en la calle, no en un mapa." |
| 0:20–0:45 | Problema con 3 cifras de §10: 1,367 tianguis sin un mapa vivo, 6.7% de negocios vende en línea, tienditas −42.8% de facturación. |
| 0:45–1:15 | **SEDECO:** mapa 3D, "Ver dato real", barra al martes, desiertos. "Así se ve dónde se mueve el dinero digital y dónde falta comercio de barrio." |
| 1:15–1:45 | **Usuario:** lista → ruta con 0 cadenas y paradas en zonas que necesitan clientes. "Movilidad cero: todo en tu colonia." |
| 1:45–2:15 | **Negocio en vivo:** nota de voz → aparece en el mapa, en la ruta y con su página web. Escalera de barrio hacia el crédito. |
| 2:15–2:40 | Implementación: colectivos INJUVE mantienen los datos; SEDECO publica el estándar abierto; triple hélice con CANACOPE e IPN. Evidencia: Singapur y Corea. |
| 2:40–3:00 | Cierre: "Los demás le dan una app al comerciante. Nosotros le damos a la ciudad la red viva de su economía de barrio." |

## Apéndice H · Riesgos

| Riesgo | Mitigación |
|---|---|
| El ID del modelo de OpenAI no existe o cambia | Spike PB-004 en los primeros 30 min; ID solo en `app/config.py`; respaldo y respuestas grabadas |
| Portal de datos bloquea la descarga | Un humano descarga a `data/raw/`; la tarea lo pide con el nombre exacto del archivo |
| CNBV no tiene un trimestre más reciente que 2023-T2 | Mostrar el periodo en cada cifra; decirlo en el pitch |
| La serie de Banxico por giro no existe en SIE o pide registro | `g_i = 1` y anotarlo; no inventar |
| Red o Telegram fallan en la demo | `DEMO_MODE=1` + `simular_alta.py` + video plan B |
| Mapbox limita peticiones | Rutas de la demo precalculadas; 300 por minuto es suficiente |
| El jurado cree que el hexágono es dato real | Etiqueta "estimado" en cada tarjeta e interruptor "Ver dato real" |
| Una cadena entra a una ruta | 4 filtros, invariante en la API y pruebas que bloquean el merge |
| Se ve como control de gobierno | SEDECO solo ve agregados; todo es voluntario; nada de trámites |
| Demasiado alcance para 6 h | P0 primero; P2 solo si sobra tiempo; congelamiento a las 16:30 |
