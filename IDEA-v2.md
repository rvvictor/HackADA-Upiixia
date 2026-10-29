# IDEA v2 · colonIA (Pulso Barrial) · Realineación

> Este archivo describe **los cambios** sobre la versión 1 (repo `Chilangaton-Upiixia`, `main@216cafd`). Se aplica en un repo nuevo que parte de esa base.
> Etiquetas: **[Decided]** · **[Recommended]** · **[To validate]**.
> Regla que se conserva de v1: **el LLM nunca produce una cifra que se muestre**. Toda cifra lleva `tipo_dato` (`real`, `estimado`, `simulado`) y la UI la muestra.
> Si algo de este archivo contradice al `IDEA.md` v1, manda este archivo.

---

## 0. Resumen de los 6 cambios

| # | Cambio | Qué se va | Qué llega |
|---|---|---|---|
| 1 | Mapa unificado | Pestaña/vista **Crecimiento** separada; altura y color de hexágono con datos distintos | Una sola vista **Mapa** con selector de capa; altura y color = **la misma métrica**; íconos por tipo de negocio |
| 2 | Enfoque ampliado | Solo tianguis y mercados como protagonistas | **Tianguis + mercados + pequeños negocios locales** como tres tipos de primer nivel |
| 3 | Sin neón | Paleta oscura con rosa/jade "luz", glows, `text-shadow` y `drop-shadow` brillantes | Paleta sobria, sin brillos |
| 4 | Repartidores | — | Alta de repartidores 100% por Telegram (texto y voz) + **portal web de repartidores** con mapa de rutas e incentivos (bici) |
| 5 | Datos de toda la CDMX | Solo Coyoacán e Iztapalapa | Las 16 alcaldías visibles, **con prioridad** de Coyoacán e Iztapalapa |
| 6 | Repartidor del negocio | — | Al dar de alta un negocio, el bot pregunta si tiene repartidor y lo da de alta |

Nueva frase del wow: *"Una nota de voz da de alta un negocio y a su repartidor; el negocio aparece en el mapa de la ciudad y el repartidor ve su primera ruta en el portal."*

---

## 1. Mapa unificado (adiós a la sección Crecimiento)

### 1.1 Qué cambia
- Se **elimina** `web/src/features/crecimiento/` como vista propia y su entrada en la navegación. [Decided]
- Sus datos (serie CNBV por alcaldía, altas DENUE por año, altas de plataforma hoy, rutas por hexágono) **pasan a ser capas y paneles del mapa**:
  - capas de hexágono: `crecimiento_altas` (altas DENUE recientes por hexágono), `rutas` (rutas que pasaron por el hexágono), `altas_hoy`;
  - la serie trimestral CNBV y "altas por año" se muestran en la **tarjeta de alcaldía** (clic en el contorno de la alcaldía o en el modo "Ver dato real"), no en otra página.
- `GET /api/sedeco/crecimiento` se mantiene para no romper el contrato, pero el frontend lo consume desde el panel del mapa. [Recommended]

### 1.2 Altura = color (una sola métrica)
Hoy (`web/src/features/sedeco/MapaSedeco.tsx:39-40`, `web/src/lib/map/hex.ts:76-77`) la altura es la actividad estimada y el color es el índice de impulso. Eso confunde: un hexágono alto puede verse pálido.

Regla v2 [Decided]:
- Cada capa define **una** métrica `m`. Altura y color salen de `m`: `altura = escala_altura(m)`, `color = rampa(m)`.
- El hexágono más alto es siempre el más intenso de color en la capa activa.
- La leyenda muestra una sola rampa con el nombre de la métrica, su `tipo_dato` y su fuente.
- Si se quiere mostrar una segunda métrica, se hace con **otra capa**, no mezclando canales.
- Si existe una capa de *heatmap* (densidad de puntos), usa la misma métrica y la misma rampa que los hexágonos. Recomendación: no mostrar heatmap y hexágonos a la vez; el heatmap solo aparece en zoom lejano (vista de ciudad) y los hexágonos en zoom cercano. [Recommended]

Capas del selector (cada una = una métrica):

| Capa | Métrica | tipo_dato |
|---|---|---|
| Actividad | `actividad_tpv_est` | estimado |
| Oferta barrial | `negocios_barriales` (tianguis + mercados + pequeños negocios) | real |
| Población | `poblacion` | real |
| Impulso | `impulso` | estimado |
| Crecimiento | altas DENUE recientes por hexágono | real |
| Rutas | rutas de reparto/compra que pasaron por el hexágono | real de plataforma o simulado |

Implementación: una función `pintarCapa(map, capa)` en `web/src/lib/map/hex.ts` que fija altura y color con la **misma** expresión de entrada. Hay una prueba unitaria que comprueba que, para toda capa, la expresión de altura y la de color leen la misma propiedad.

### 1.3 Íconos por tipo de negocio
- Tres íconos (capa `symbol` de Mapbox, imágenes SVG cargadas con `map.addImage`): [Decided]
  - **Tianguis**: toldo/lona.
  - **Mercado**: edificio con techo de dos aguas.
  - **Pequeño negocio**: tiendita/puerta con toldo corto.
- Los íconos se agrupan en zoom lejano (`cluster: true` en la fuente GeoJSON) y muestran el conteo.
- Filtro en el panel: tres chips para encender o apagar cada tipo.
- Accesibilidad: el ícono no depende solo del color; forma distinta por tipo y etiqueta en el tooltip.
- Archivos: `web/public/iconos/{tianguis,mercado,negocio}.svg`, `web/src/lib/map/iconos.ts`.

---

## 2. Enfoque ampliado: pequeños negocios locales

- El campo `tipo` del punto barrial pasa de `tianguis | mercado` a `tianguis | mercado | negocio_local`. [Decided]
- **Pequeño negocio local** = establecimiento DENUE de comercio al por menor o servicios de consumo, estrato `0 a 5` o `6 a 10` personas, que pasa la regla anti-cadenas (v1 §A.7). [Recommended · umbral en `app/config.py`]
- La ruta de compras (`POST /api/ruta`) ya usa negocios barriales; v2 solo asegura que `negocio_local` tenga el mismo peso que tianguis y mercados en el puntaje.
- El bot de Telegram ofrece en `/start`: **Dar de alta negocio** (cualquier tipo), **Actualizar mi negocio**, **Quiero ser repartidor** (ver §4).
- Textos de la UI: dejar de decir "tianguis y mercados" como sinónimo de "comercio barrial"; usar "negocios de barrio" e incluir los tres tipos.

---

## 3. Sin color neón

Fuera [Decided]:
- tokens `--ci-rosa-luz`, `--ci-jade-luz` y cualquier color saturado usado como "luz" (`web/src/features/inicio/inicio.css:3-16`);
- `.ci-hero-glow`, `text-shadow` y `drop-shadow` con halo de color (`inicio.css:165, 201, 210`);
- animaciones de pulso con `box-shadow` de color (`inicio.css:339`).

Dirección nueva [Recommended]:
- Base clara tipo documento público (fondo `#f6f7f4`, texto `#0e1116`, como ya define `web/src/index.css`).
- Un acento cálido apagado (terracota o barro) para llamadas a la acción.
- Rampas secuenciales de mapa de saturación media (por ejemplo tonos de un solo matiz, de claro a oscuro), legibles en proyector y con contraste AA.
- Sombras solo neutras (gris, opacidad ≤ 0.15) para elevación, nunca para brillo.
- Todos los colores como tokens en `web/src/lib/ui/tokens.css`; ningún hex suelto en componentes.

Criterio: `rg -n "glow|text-shadow|drop-shadow\(0 0" web/src` no devuelve nada, y ningún token tiene saturación HSL > 85% con luminosidad > 55%.

---

## 4. Repartidores: alta por Telegram + portal web

### 4.1 Por qué
El comercio de barrio necesita entregar sin pagar comisiones de plataforma. Una red de repartidores de barrio, en bici, resuelve la última milla y da empleo local.

### 4.2 Flujo en Telegram (todo por chat, texto o nota de voz)
Cada pregunta acepta **texto o nota de voz**; la voz se transcribe con `OPENAI_TRANSCRIBE_MODEL` y el LLM solo extrae el campo pedido (salida estructurada, validada con Pydantic). Preguntas cortas, una por mensaje, con botones cuando hay opciones cerradas.

1. `/start` → **Quiero ser repartidor**.
2. Aviso de privacidad corto + botón **Acepto** (sin aceptar no sigue).
3. Nombre (como quiere que lo llamen).
4. Fecha de nacimiento (o edad).
5. ¿Estudias? → botones **Sí** / **No**. Si sí: escuela (texto libre opcional).
6. Identificación oficial: foto (INE, pasaporte o credencial escolar vigente). Ver §4.5 privacidad.
7. Alcaldía: botones con las 16 alcaldías (Coyoacán e Iztapalapa primero).
8. Colonias: el bot muestra las colonias de esa alcaldía (paginadas, con búsqueda por texto o voz) y deja elegir hasta 3. [Recommended]
9. Medio de transporte: botones **Bici** · **Bici eléctrica** · **A pie** · **Scooter eléctrico** · **Moto** · **Auto**. El bot **sugiere** los ecológicos: si elige moto o auto, responde con un mensaje corto sobre los beneficios de la bici y el incentivo de §4.4, sin bloquear la elección.
10. Disponibilidad: días y franja horaria (botones).
11. Resumen con botones **Así queda** / **Corregir**.
12. Al confirmar: `POST /api/repartidores` → se genera el **número de repartidor** (`R-XXXXX`) y el bot lo envía junto con el link al portal.

Estados posibles del alta: `pendiente_verificacion` → `activo` | `rechazado`. La verificación de identidad la hace una persona (o queda simulada en demo con `demo_data: true`).

### 4.3 Priorización (no exclusión)
- Se **prioriza** a personas de **18 a 30 años que estudian**; nadie queda excluido por edad o por no estudiar. [Decided]
- Requisito legal: **mayor de 18 años** para registrarse. [To validate con asesoría legal]
- La prioridad solo actúa cuando hay más repartidores que rutas en una colonia: al ofrecer una ruta, el orden es `prioridad DESC, cercanía ASC, antigüedad ASC`.
- `prioridad = 2` si 18–30 y estudiante; `1` si cumple solo una; `0` si ninguna. Peso en `app/config.py`.
- La UI y el bot nunca muestran la prioridad de otra persona.
- [To validate] Revisar con alguien de lo legal que la preferencia por edad y por ser estudiante se enmarque como programa de empleo juvenil (acción afirmativa) y no como discriminación, conforme a la Ley Federal para Prevenir y Eliminar la Discriminación y a la Ley Federal del Trabajo. Documentarlo en `docs/legal/priorizacion.md`.

### 4.4 Portal web de repartidores
Ruta del frontend: `#/repartidor`. [Decided]

- **Entrada**: número de repartidor + un código de 6 dígitos que el bot envía por Telegram al pedirlo (sin contraseñas). [Recommended: solo el número no basta, cualquiera podría ver las rutas de otro]
- **Mapa de ofertas**: mapa con las ofertas de ruta abiertas en sus colonias; cada oferta muestra negocio de origen (con su ícono de §1.3), paradas, distancia, tiempo estimado y pago estimado (`tipo_dato` visible). Las ofertas nuevas aparecen sin recargar (polling cada 5 s, como `altas/live`). Botón **Tomar ruta**.
- **Mis rutas**: rutas tomadas, en curso y completadas, con contador.
- **Incentivos**: catálogo de premios por número de rutas completadas, con barra de avance. El premio destacado (tarjeta grande, arriba) es la **bici**, al llegar a `N` rutas. `N` y el catálogo viven en `data/processed/incentivos.json`. Otros premios de ejemplo: casco, luces, candado, mochila térmica, mantenimiento de bici. [To validate: N y patrocinador reales; en demo todo con `tipo_dato: "simulado"`]
- Mensaje de transporte: si su medio no es ecológico, un aviso suave con el beneficio de cambiar a bici.

### 4.5 Privacidad de repartidores
- La foto de identificación no se publica nunca y no se envía al frontend. Se guarda fuera de git (`data/live/ids/`, ignorado), se borra tras verificar y solo se conserva `id_verificada: bool`, `tipo_id` y fecha. [Recommended]
- No se guarda número de teléfono; el contacto es el `chat_id` de Telegram.
- Aviso de privacidad conforme a la ley de protección de datos personales en posesión de particulares vigente. [To validate texto con asesoría legal]
- Los datos de prioridad (edad, estudiante) no salen del backend.

---

## 5. Datos de toda la CDMX con prioridad en Coyoacán e Iztapalapa

- El pipeline deja de filtrar por `ALCALDIAS=09003,09007`; procesa las 16 alcaldías (`09002` a `09017`). [Decided]
- **Prioridad** de Coyoacán (`09003`) e Iztapalapa (`09007`), de cuatro formas:
  1. cámara inicial del mapa sobre Coyoacán con Iztapalapa a la vista (igual que v1);
  2. esas dos alcaldías con contorno destacado y su resumen primero en el panel;
  3. en el bot y en los selectores, aparecen primero en la lista;
  4. la carga del frontend pide primero esas dos (`GET /api/hex?alcaldias=09003,09007`) y luego el resto en segundo plano.
- Rendimiento [Recommended]: con toda la ciudad hay muchos hexágonos de res 9.
  - zoom lejano: hexágonos de res 7 agregados (o heatmap, §1.2);
  - zoom cercano: res 9 solo del área visible (`GET /api/hex?bbox=...&res=9`);
  - si el GeoJSON pesa más de ~5 MB, convertir a teselas vectoriales (PMTiles o tileset de Mapbox).
- Los datos reales que inyecte el equipo llegan a `data/raw/` y se procesan a `data/processed/` con su ficha en `data/fuentes/<fuente>.md`. Nada se muestra como `real` sin ficha de fuente.
- Las cifras citables de v1 (§10) se revisan con los datos nuevos; ninguna cifra del pitch se cambia sin fuente.

---

## 6. El bot pregunta por el repartidor del negocio

- Al final del alta de un negocio (después de **Así queda**), el bot pregunta: **"¿Tienes a alguien que haga entregas para tu negocio?"** → **Sí** / **No**. [Decided]
- **Sí** → dos opciones:
  - **Lo doy de alta yo**: el bot hace las preguntas de §4.2 a nombre del repartidor (sin la foto de identificación), y lo deja `pendiente_verificacion`;
  - **Le mando un link**: el bot genera un link de invitación `t.me/<bot>?start=inv_<token>` que el repartidor abre para terminar su alta él mismo (con identificación). [Recommended, porque así la identificación y el consentimiento son del propio repartidor]
- El repartidor queda ligado al negocio (`negocio_id`) y sus rutas de ese negocio le llegan primero, antes que la cola general.
- **No** → el bot ofrece la red de repartidores del barrio: "Cuando tengas un pedido, lo publicamos para repartidores de tu colonia."

---

## 7. Contrato de datos nuevo (`app/schemas/`)

| Entidad | Archivo | Campos clave | Tipo |
|---|---|---|---|
| Punto barrial (cambia) | `tianguis_abierto.json` | `tipo: tianguis \| mercado \| negocio_local` (antes solo los dos primeros) | Real |
| Repartidor | `data/live/repartidores.jsonl` | `id (R-XXXXX), ts_alta, chat_id_hash, nombre_mostrar, rango_edad (18-30 \| 31+), estudiante (bool), alcaldia_cvegeo, colonias[], transporte (bici \| bici_electrica \| a_pie \| scooter_electrico \| moto \| auto), disponibilidad{dias[], desde, hasta}, id_verificada (bool), tipo_id, estado (pendiente_verificacion \| activo \| rechazado), negocio_id?, prioridad (0-2), rutas_completadas, demo_data` | Real de plataforma |
| Oferta de ruta | `data/live/ofertas.jsonl` | `id, ts, negocio_id, tipo_negocio, paradas[{lat, lng, h3, colonia}], distancia_m, minutos_est, pago_est, tipo_dato_pago, colonia, estado (abierta \| tomada \| completada \| cancelada), repartidor_id?, demo_data` | Real de plataforma / simulado |
| Incentivo | `data/processed/incentivos.json` | `id, nombre, descripcion, rutas_requeridas, destacado (bool), imagen, patrocinador?, estado (existe \| propuesta), tipo_dato` | Propuesta / simulado |
| Alcaldía y colonias | `data/processed/colonias.json` | `alcaldia_cvegeo, alcaldia_nombre, prioridad (bool), colonias[{id, nombre, lat, lng}]` | Real (fuente a fijar) |

Reglas:
- `rango_edad` en lugar de fecha de nacimiento cuando sea posible (minimizar datos).
- Tipos espejo en `web/src/lib/types.ts`, fixtures en `app/fixtures/`, `DEMO_MODE=1` sigue funcionando sin red.
- Repartidores y ofertas en demo llevan `demo_data: true` y la UI lo muestra.

---

## 8. API nueva o cambiada

| Método | Ruta | Devuelve |
|---|---|---|
| GET | `/api/hex?alcaldias=&bbox=&res=&capa=` | Hexágonos; `capa` define la métrica única de altura y color |
| GET | `/api/puntos?tipo=tianguis,mercado,negocio_local&bbox=` | Puntos con su tipo, para la capa de íconos |
| GET | `/api/alcaldias` | 16 alcaldías con bandera `prioridad` |
| GET | `/api/alcaldias/{cvegeo}/colonias` | Colonias de una alcaldía |
| POST | `/api/repartidores` | Crea alta desde el bot; devuelve `id` |
| POST | `/api/repartidores/invitacion` | Token de invitación ligado a `negocio_id` |
| POST | `/api/repartidores/codigo` | Pide el código de acceso (el bot lo entrega por Telegram) |
| POST | `/api/repartidores/sesion` | `{id, codigo}` → sesión corta (token) |
| GET | `/api/repartidores/{id}` | Perfil propio, rutas completadas, avance de incentivos |
| GET | `/api/ofertas?repartidor_id=&desde=ts` | Ofertas abiertas en sus colonias, ordenadas por la regla de §4.3 |
| POST | `/api/ofertas/{id}/tomar` · `/completar` | Cambia el estado de la oferta |
| GET | `/api/incentivos` | Catálogo, con el destacado primero |
| GET | `/api/sedeco/crecimiento` | Se conserva; lo consume el panel del mapa |

---

## 9. Pantallas

- **Navegación**: `#/mapa` (antes `#/sedeco`; con redirección), `#/usuario`, `#/negocio/:id`, `#/repartidor`. Sale `#/crecimiento`.
- **Mapa**:
  - selector de capa (§1.2);
  - chips de tipo de negocio (§1.3);
  - selector de alcaldía (16, las prioritarias primero);
  - barra de tiempo lun–dom (v1);
  - tarjeta de hexágono con una sola métrica destacada;
  - tarjeta de alcaldía con la serie CNBV y las altas por año (lo que antes era Crecimiento).
- **Portal repartidor**:
  - entrada con número + código;
  - mapa de ofertas (60% de ancho);
  - lista de mis rutas;
  - pestaña Incentivos con la bici destacada y barra "te faltan X rutas".
- **Inicio**: sin glows, con la paleta de §3, y con la frase del wow de §0.

---

## 10. Backlog sugerido (tareas verticales para `/uak-plan`)

| ID | Tarea | Prio | Depende |
|---|---|---|---|
| V2-01 | Contrato v2: `tipo` con `negocio_local`, esquemas Repartidor, Oferta, Incentivo, Colonias + fixtures + tipos TS | P0 | — |
| V2-02 | Paleta sin neón: tokens nuevos, quitar glows y sombras de color, revisar contraste AA | P0 | — |
| V2-03 | Mapa: altura = color con una sola métrica por capa + prueba de expresión | P0 | V2-01 |
| V2-04 | Mapa: íconos de tianguis, mercado y negocio local con cluster y chips | P0 | V2-01 |
| V2-05 | Quitar vista Crecimiento; mover sus datos a capas y tarjeta de alcaldía | P0 | V2-03 |
| V2-06 | Pipeline de las 16 alcaldías + `colonias.json` + carga por prioridad y por bbox | P0 | V2-01 |
| V2-07 | Bot: flujo "Quiero ser repartidor" (texto y voz, alcaldía → colonias, transporte con sugerencia ecológica, ID) | P0 | V2-01, V2-06 |
| V2-08 | API de repartidores, ofertas e incentivos + regla de priorización con pruebas | P0 | V2-01 |
| V2-09 | Portal repartidor: acceso por código, mapa de ofertas en vivo, mis rutas | P0 | V2-08, V2-04 |
| V2-10 | Portal repartidor: incentivos con la bici destacada | P1 | V2-09 |
| V2-11 | Bot: pregunta por el repartidor del negocio + invitación por link | P1 | V2-07 |
| V2-12 | Rendimiento ciudad completa: res 7 en zoom lejano o teselas vectoriales | P1 | V2-06 |
| V2-13 | `scripts/simular_repartidor.py` y ofertas simuladas para `DEMO_MODE=1` | P0 | V2-08 |
| V2-14 | Textos: "negocios de barrio" en toda la UI y el README; aviso de privacidad de repartidores | P1 | V2-07 |

## 11. Criterios de aceptación

1. En toda capa del mapa, el hexágono más alto tiene el color más intenso (prueba automática sobre la expresión y revisión visual).
2. No existe la ruta `#/crecimiento`; sus cifras se ven en el mapa.
3. Los tres tipos de negocio se distinguen por ícono y se pueden filtrar.
4. `rg -n "glow|text-shadow|drop-shadow\(0 0" web/src` vacío.
5. Un alta de repartidor completa por Telegram usando **solo notas de voz** (salvo foto de ID y botones) termina con número `R-XXXXX`.
6. Con 2 repartidores en la misma colonia, el de 18–30 estudiante ve la oferta primero; el otro también la ve (no hay exclusión). Prueba en `app/tests/test_ofertas.py`.
7. En el portal, una oferta nueva aparece en ≤ 5 s sin recargar; al completar rutas avanza la barra de la bici.
8. El mapa muestra las 16 alcaldías y abre sobre Coyoacán e Iztapalapa en ≤ 15 s.
9. La foto de identificación nunca aparece en ninguna respuesta de la API (prueba).
10. `DEMO_MODE=1` corre todo el flujo sin red ni llaves.

## 12. Riesgos y pendientes

- **Legal** de la priorización por edad y estudiante, y del aviso de privacidad. [To validate antes de piloto real]
- **Verificación de identidad** real necesita una persona o un proveedor; en demo es simulada.
- **Premio de bici** necesita patrocinador (por ejemplo, un programa de movilidad de la ciudad). Sin confirmarlo, se presenta como propuesta. [To validate]
- **Pago al repartidor**: v2 muestra un pago estimado. No procesa pagos; cómo se paga queda fuera de alcance.
- **Peso de datos** con toda la CDMX: medir el tamaño del GeoJSON antes de decidir entre res 7 y teselas.
