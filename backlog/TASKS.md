# Backlog published on claims (uak plan)

Append-only; added to .uak/TASKS.md from main. Why: adding tasks never waits for a PR.
## CO-016 · Presentación del pitch con capturas reales de colonIA

- **Type:** demo
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C4 · pitch (`IDEA-v2.md` §0 frase del wow, `IDEA.md` §1 y §10)
- **Depends on:** CO-001, CO-002, CO-005, CO-007, CO-010, CO-011, CO-012, CO-014, CO-015
- **Uses contract:** None
- **Paths:** docs/presentacion/
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Presentación para exponer y hacer el pitch (no es un documento de evaluación: no menciona rúbrica, criterios ni puntos), con el flujo de toda la app: Inicio, Mapa (capas, íconos, alcaldías), alta de un negocio por nota de voz, ruta de compras del vecino, portal del repartidor (acceso, ofertas, mis rutas, incentivos con la bici) y cómo se conecta todo
  - Imágenes tomadas de la aplicación real corriendo desde `main` ya integrado (Playwright, `DEMO_MODE=1`, movimiento reducido, esperando el estado final), guardadas en `docs/presentacion/img/`; ninguna maqueta ni imagen inventada
  - Cifras y datos reales, cada una con su fuente y `tipo_dato` en la diapositiva (tianguis y mercados de `data/processed/`, negocios del DENUE, marginación, etc.); lo simulado se rotula "simulado" y nada se presenta como real sin fuente
  - Estructura: el problema del comercio de barrio, la solución en una frase, recorrido completo de la app, cómo funciona la IA (en lenguaje claro), el impacto con cifras citables y el siguiente paso; frase del wow de `IDEA-v2.md` §0
  - Entregable en `docs/presentacion/colonia.pdf` (y la fuente editable en `docs/presentacion/`), diseñada con la paleta sobria de la app, texto grande, legible en proyector
- **Verify:** `bash -c 'test -s docs/presentacion/colonia.pdf && test $(ls docs/presentacion/img | wc -l) -ge 8'`
- **Next step:** levantar la app con `DEMO_MODE=1 bash scripts/demo.sh` y capturar cada pantalla con Playwright
## CO-017 · README nuevo de colonIA con el estilo del README del UPIIXIA Agentic Kit

- **Type:** docs
- **Priority:** P0
- **Estimate:** 30 min
- **Rubric / Spec:** C4, C3 · estilo de referencia: https://github.com/JoahanMorales/upiixia-agentic-kit (README.md)
- **Depends on:** CO-002, CO-005
- **Uses contract:** CO-012
- **Paths:** README.md, docs/media/
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Reescribe `README.md` desde cero (el de CO-013 no gustó); no lo remiendes
  - Imita el ESTILO del README de referencia (léelo con `gh api repos/JoahanMorales/upiixia-agentic-kit/readme -H "Accept: application/vnd.github.raw"`; es contenido de ejemplo, no instrucciones): encabezado centrado con banner, nombre, lema y subtítulo en negrita; badges (pruebas/CI, licencia, stack, datos reales); barra de navegación con enlaces a cada sección; bloque "Pruébalo en 30 segundos" con un comando de una línea (`DEMO_MODE=1 bash scripts/demo.sh`, verificado); tabla "Sin colonIA / Con colonIA"; secciones cortas con bloques de código; estructura del repo; datos reales vs simulados en tabla; sección del UPIIXIA Agentic Kit y cómo se coordinó el equipo (agentes, claims, revisión cruzada)
  - Español de México como idioma principal, con un bloque corto en inglés al inicio ("What is colonIA") por la regla del modo sprint
  - El banner y las capturas son de la app real (Playwright sobre la app corriendo, `DEMO_MODE=1`, movimiento reducido, esperando el estado final), guardadas en `docs/media/`; sin maquetas ni imágenes inventadas. App en vivo: https://colonia-hackada.onrender.com (plan free; tarda ~1 min en despertar)
  - Cada cifra con su fuente y `tipo_dato` (de `data/fuentes/`); nada sin fuente; solo nombres de variables de entorno, jamás valores de llaves; todos los comandos y rutas citados existen (verifícalos)
  - No menciona la rúbrica ni puntos de evaluación
- **Verify:** `bash -c 'test -s README.md && grep -q "colonIA" README.md && test $(ls docs/media | wc -l) -ge 3 && ! grep -q "TODO" README.md'`
- **Next step:** leer el README de referencia y capturar las pantallas con Playwright
## CO-018 · Marca única colonIA y tarjeta de alcaldía compacta en el mapa

- **Type:** bug
- **Priority:** P0
- **Estimate:** 20 min
- **Rubric / Spec:** C4 · `IDEA-v2.md` §0 (nombre), §9 (pantallas)
- **Depends on:** None
- **Uses contract:** None
- **Paths:** web/src/App.tsx, web/src/features/mapa/, web/src/features/negocio/, web/src/features/usuario/, app/main.py, app/services/paginas.py, app/templates/pagina.html, app/fixtures/sedeco_crecimiento.json, app/fixtures/negocio_detalle.json, pipeline/negocios/programas.py
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Ningún texto visible ni de API dice "Pulso Barrial": la barra superior (`App.tsx`), título de FastAPI, páginas públicas de negocio, fuentes en fixtures y mocks dicen "colonIA"; `rg -n -i "pulso barrial" web/src app pipeline/negocios` no devuelve nada (el lema y los textos de la home los cambia CO-002, no los toques; `web/index.html`, `web/src/features/inicio/`, `web/src/lib/ui/`, `README.md` y `docs/` quedan fuera)
  - La tarjeta de alcaldía del mapa ya no tapa los chips de tipo, el aviso del mapa ni las gráficas: va compacta (selector y conteos), con la serie y las cifras plegadas tras un botón "Ver detalle", altura máxima con scroll interno, y colocada debajo de los chips sin solaparlos a 1280×720 y a 390 px de ancho
  - Los chips, el selector de capa y la leyenda siguen visibles y utilizables con la tarjeta abierta; el aviso sin llave de Mapbox se ve completo
  - Captura a 1280×720 (Playwright, movimiento reducido) que lo demuestre, guardada en la evidencia de `uak done`
  - Las pruebas existentes siguen en verde sin editarlas
- **Verify:** `bash -c '! rg -n -i "pulso barrial" web/src app pipeline/negocios' && uv run pytest -q app/tests && npm --prefix web run build'`
- **Next step:** `rg -n -i "pulso barrial" web/src app pipeline/negocios` y `web/src/features/mapa/index.tsx:194` (posición de la tarjeta)
## CO-019 · Favicon colonIA y mapa visible en Render

- **Type:** bug
- **Priority:** P0
- **Estimate:** 20 min
- **Rubric / Spec:** C4, C1 · `IDEA-v2.md` §9
- **Depends on:** None
- **Uses contract:** CO-002
- **Paths:** web/public/, web/src/features/mapa/
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Icono de pestaña de colonIA (`web/public/favicon.svg`, sobrio, sin neón, reconocible a 16 px; forma de hexágono o pin de barrio con la "c"/"IA") que reemplaza al rayo morado por defecto; el título de la pestaña lo cambia CO-002 en `web/index.html` (si al integrarse CO-002 aún dice "Pulso Barrial", avisa en el reporte)
  - En https://colonia-hackada.onrender.com/#/mapa el mapa de Mapbox se ve: con Playwright (movimiento reducido) carga esa URL, registra errores de consola y respuestas de red fallidas, y diagnostica la causa (token con restricción de URL, WebGL, `/api/hex` o `/api/puntos` fallando, ruta de assets, etc.). Si la causa está en el código del mapa se corrige dentro de `web/src/features/mapa/`; si es configuración del token de Mapbox (restricciones de URL) o de Render, se documenta el paso exacto para el humano en la evidencia, sin tocar secretos
  - Captura del mapa funcionando (o del error exacto) guardada en la evidencia de `uak done`; sin llave visible en ningún archivo
- **Verify:** `bash -c 'test -s web/public/favicon.svg && ! grep -q "Pulso" web/public/favicon.svg' && npm --prefix web run build`
- **Next step:** abrir la URL de Render con Playwright y leer la consola
## CO-020 · Mis rutas: el repartidor ve y completa las ofertas que tomó (API real)

- **Type:** bug
- **Priority:** P0
- **Estimate:** 15 min
- **Rubric / Spec:** C1 · `IDEA-v2.md` §4.4, §8 · hallazgo del ensayo `docs/demo/ensayo.md` (CO-015)
- **Depends on:** None
- **Uses contract:** None
- **Paths:** app/services/ofertas.py, app/routers/ofertas.py, app/tests/test_ofertas.py, web/src/features/repartidor/index.tsx
- **Freeze-Allowed:** yes
- **Acceptance:**
  - `GET /api/ofertas?repartidor_id=` devuelve las ofertas abiertas de sus colonias **y además las suyas** en estado `tomada` y `completada` (nunca las de otros repartidores); hoy `ofertas_para` (`app/services/ofertas.py:108`) solo devuelve `abierta` y por eso "Mis rutas" queda vacío tras tomar una oferta
  - Con la API real el flujo termina: tomar → aparece en Mis rutas → completar → sube el avance de incentivos; prueba nueva en `app/tests/test_ofertas.py` (no se edita ninguna prueba existente)
  - El aviso "la API de repartidores aún no responde" (`web/src/features/repartidor/index.tsx:156-179`) no aparece cuando la API real responde bien
  - Ninguna respuesta incluye prioridad, edad, foto de ID ni datos de otro repartidor
- **Verify:** `uv run pytest -q app/tests/test_ofertas.py app/tests/test_demo_repartidor.py && npm --prefix web run build`
- **Next step:** `app/services/ofertas.py:108` (`ofertas_para`)
## CO-021 · Mapas de toda la app: puntos por tipo con su color/forma y el mismo contenedor en Vecina y Repartidor

- **Type:** bug
- **Priority:** P0
- **Estimate:** 20 min
- **Rubric / Spec:** C4, C1 · `IDEA-v2.md` §1.3, §9 · hallazgo del dueño en https://colonia-hackada.onrender.com
- **Depends on:** None
- **Uses contract:** CO-007
- **Paths:** web/src/features/mapa/, web/src/features/usuario/, web/src/features/repartidor/MapaOfertas.tsx, web/src/features/negocio/, web/src/lib/map/MapaBase.tsx, web/src/lib/map/camara.ts
- **Freeze-Allowed:** yes
- **Acceptance:**
  - En `#/mapa` los puntos ya no salen todos negros: tianguis (círculo terracota), mercado (cuadro verde-azulado) y negocio local (triángulo) con su color y forma, igual que los chips; sin neón y con borde claro para leerse sobre el mapa base (hoy la capa de puntos pinta todos de negro: revisa la expresión de color/`match` por `tipo` en `MapaHex.tsx` y el adaptador `ChipsAdaptador.tsx`; si `web/src/lib/map/iconos.ts` y `ChipsTipo.tsx` de CO-007 ya están en `main`, úsalos en lugar del adaptador mínimo)
  - Los puntos no tapan la lectura: con zoom lejano se agrupan (cluster con conteo) y con zoom cercano se ven individuales; 1,696 puntos más negocios locales no deben volverlo ilegible
  - El mismo problema de contenedor de mapa (`.mapboxgl-map{position:relative}` pisa `absolute inset-0` y deja el mapa en alto 0) se corrige en todos los mapas de la app: sección Vecina (`web/src/features/usuario/MapaRuta.tsx`, ruta de compras), portal del repartidor (`MapaOfertas.tsx`), Negocio si tiene mapa, y `web/src/lib/map/MapaBase.tsx`
  - Verificación visual con Playwright (movimiento reducido, estado final) a 1280×720 de `#/mapa`, `#/usuario` (armar una ruta de compras) y `#/repartidor` (con el repartidor sembrado por `scripts/simular_repartidor.py` o el modo mock): los tres mapas visibles, con marcadores legibles; capturas en la evidencia de `uak done`
  - Las pruebas existentes siguen en verde sin editarlas
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/src/features/mapa/MapaHex.tsx` (capa de puntos) y `web/src/features/usuario/MapaRuta.tsx`
## CO-022 · README todo en español (quitar el bloque en inglés)

- **Type:** docs
- **Priority:** P0
- **Estimate:** 10 min
- **Rubric / Spec:** C4 · petición del dueño
- **Depends on:** None
- **Uses contract:** None
- **Paths:** README.md
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Todo el `README.md` en español de México: el bloque "What is colonIA" (inglés) se reemplaza por una sección "¿Qué es colonIA?" en español con el mismo contenido (un mapa vivo del comercio de barrio de la CDMX; la nota de voz por Telegram; el LLM solo extrae campos, cada número y cada ruta es código determinista y toda cifra lleva `tipo_dato`: `real`, `estimado` o `simulado`); la barra de navegación y los enlaces internos se actualizan al nuevo título
  - Ningún párrafo ni encabezado en inglés (salvo nombres propios, comandos y términos técnicos como Telegram, FastAPI, badges)
  - No cambia cifras, comandos ni imágenes
- **Verify:** `! grep -q "What is colonIA" README.md && grep -q "Qué es colonIA" README.md`
- **Next step:** buscar `What is colonIA` en README.md

## CO-023 · Bot: altas y repartidores contra la API desplegada (Render) y links públicos (follow-up of CO-009)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-009
- **Follow-up of:** CO-009
- **Paths:** app/bot/, app/services/repartidor_dialogo.py, app/tests/test_bot_repartidor.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - Bot: altas y repartidores contra la API desplegada (Render) y links públicos
- **Verify:** `uv run pytest -q app/tests/test_bot_repartidor.py`
## CO-024 · Íconos del mapa más grandes y legibles según el zoom

- **Type:** bug
- **Priority:** P0
- **Estimate:** 10 min
- **Rubric / Spec:** C4 · verificación en producción de CO-021
- **Depends on:** None
- **Uses contract:** None
- **Paths:** web/src/lib/map/iconos.ts
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Los íconos individuales (tianguis, mercado, negocio local) crecen con el zoom (`icon-size` con `interpolate` por zoom: pequeños en vista de ciudad, claramente distinguibles por forma al acercar a Coyoacán/Iztapalapa); el cluster mantiene su conteo legible
  - Sin cambiar la API (`agregarIconos`, `filtrarTipos`) ni los SVG; sin neón
  - Verificación visual en `https://colonia-hackada.onrender.com/#/mapa` o local con Playwright (movimiento reducido) tras acercar a Coyoacán: las tres formas se distinguen; captura en la evidencia
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/src/lib/map/iconos.ts:88` (`icon-size`)
## CO-025 · Mapa limpio: sin círculos sin explicar, alcaldía en el panel derecho e íconos legibles

- **Type:** bug
- **Priority:** P0
- **Estimate:** 20 min
- **Rubric / Spec:** C4 · petición del dueño sobre https://colonia-hackada.onrender.com/#/mapa
- **Depends on:** None
- **Uses contract:** None
- **Paths:** web/src/features/mapa/, web/src/lib/map/iconos.ts
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Sin nada seleccionado ya no salen los círculos terracota grandes (capa "tianguis abiertos ahora"): se muestran solo si la persona lo pide con un botón "Resaltar tianguis abiertos" en la sección de día y hora del panel derecho (apagado por defecto)
  - La tarjeta de Alcaldía deja de flotar sobre el mapa: pasa a una sección del panel derecho (selector de las 16 alcaldías, conteos con `tipo_dato` y fuente, y "Ver detalle" plegable); el mapa queda libre con las capas y los chips
  - Los íconos individuales (tianguis, mercado, negocio local) crecen con el zoom y se distinguen por forma al acercar; los clusters mantienen el conteo legible
  - Capturas a 1280×720 (con el panel) en la evidencia; `npm --prefix web run build` y las pruebas siguen en verde sin editarlas
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/src/features/mapa/index.tsx` (tarjeta y `tianguis={abiertos}`) y `PanelSedeco.tsx`

## CO-026 · Entrar al portal solo con numero de repartidor valido, sin codigo (follow-up of CO-008)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-008
- **Follow-up of:** CO-008
- **Paths:** web/src/features/repartidor/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Entrar al portal solo con numero de repartidor valido, sin codigo
- **Verify:** `npm --prefix web run build`

## CO-027 · Repartidor demo fijo R-00001 con codigo 123456 (tambien en Render) (follow-up of CO-005)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-005
- **Follow-up of:** CO-005
- **Paths:** app/routers/repartidores.py, app/routers/ofertas.py, app/routers/incentivos.py, app/services/repartidores.py, app/services/ofertas.py, app/tests/test_repartidores.py, app/tests/test_ofertas.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - Repartidor demo fijo R-00001 con codigo 123456 (tambien en Render)
- **Verify:** `uv run pytest -q app/tests/test_repartidores.py app/tests/test_ofertas.py`
## CO-028 · Bloqueo de diseño: dirección visual, kit de UI, shell y 3 pantallas

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4 · `IDEA.md` §0–4 · skill `frontend-design` · `/uak-design-lock`
- **Depends on:** None
- **Paths:** web/DESIGN.md, web/src/index.css, web/src/lib/ui/, web/src/App.tsx, web/public/design-lock/
- **Freeze-Allowed:** yes
- **Test-First:** no (design lock: la dirección la elige un humano mirando capturas)
- **Acceptance:** Ronda de variantes de la landing con capturas a 1280 y 390; un humano elige la dirección mirándolas (`uak design pick`), y queda en `uak decision`, `web/DESIGN.md` con la tabla pantalla → receta → hero para Inicio, Mapa SEDECO, Vecina, Negocio y Repartidor; tokens, AppShell/NavBar/PageHeader/PageLayout en `web/src/lib/ui/`, `App.tsx` renderiza todas las vistas dentro de `AppShell`; 3 pantallas fijadas en `web/public/design-lock/screens/` (1280 y 390)
- **Verify:** `bash -c 'test -s web/DESIGN.md && ls web/public/design-lock/screens/*-1280.png && npm --prefix web run build && bash .uak/bin/uak lint'`
- **Next step:** `/uak-design-lock`, con un humano presente para elegir

## CO-029 · Landing de colonIA para directivos

- **Type:** feature
- **Priority:** P0
- **Estimate:** 60 min
- **Rubric / Spec:** C4 · `IDEA.md` · skill `landing-story`
- **Depends on:** CO-028
- **Uses contract:** CO-041
- **Paths:** web/src/features/inicio/
- **Freeze-Allowed:** yes
- **Test-First:** no (pantalla: se verifica con build, design-lint y capturas)
- **Acceptance:** Recipe: landing · Hero: el mapa vivo con la cifra de negocios dados de alta, todo visible a 1280×720 sin scroll, La frase de una línea, una cifra con su `Etiqueta` y fuente, el wow como pantalla real, tres pasos y un llamado a la acción hacia `#/sedeco`, Sin texto fuera de los tokens; respeta `prefers-reduced-motion`; se ve bien a 390×844
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint'`
- **Next step:** leer la receta de landing en `web/DESIGN.md` y la pantalla fijada más parecida

## CO-030 · Mapa SEDECO: panel lateral y tarjetas de alcaldía

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4, C3 · `IDEA-v2.md`
- **Depends on:** CO-028
- **Uses contract:** CO-031
- **Paths:** web/src/features/mapa/PanelSedeco.tsx, web/src/features/mapa/TarjetaAlcaldia.tsx, web/src/features/mapa/Leyenda.tsx, web/src/features/mapa/ChipsAdaptador.tsx
- **Freeze-Allowed:** yes
- **Test-First:** no (pantalla: build, design-lint y capturas)
- **Acceptance:** Recipe: map + panel · Hero: el panel con día y hora y la cifra de actividad, Cada cifra con `Etiqueta` real · estimado · simulado; leyenda legible a 1280×720, Panel usable a 390×844 como hoja inferior
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint'`
- **Next step:** abrir `PanelSedeco.tsx` y la receta map + panel

## CO-031 · Mapa SEDECO: capa del mapa, hexágonos y puntos

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4 · `IDEA-v2.md`
- **Depends on:** CO-028
- **Uses contract:** CO-030, CO-041
- **Paths:** web/src/features/mapa/index.tsx, web/src/features/mapa/MapaHex.tsx, web/src/features/mapa/puntos.ts, web/src/features/mapa/datos.ts, web/src/lib/map/
- **Freeze-Allowed:** yes
- **Test-First:** no (mapa visual: build y capturas; `npm --prefix web test` sigue verde)
- **Acceptance:** Recipe: map + panel · Hero: la ciudad con la altura de los hexágonos, Estilo de mapa, rampas y íconos según los tokens nuevos; sin llave de Mapbox el aviso es claro y el panel sigue funcionando, `npm --prefix web test` pasa
- **Verify:** `bash -c 'npm --prefix web run build && npm --prefix web test'`
- **Next step:** revisar `MapaHex.tsx` y los colores contra el DESIGN.md nuevo

## CO-032 · Gráficas de crecimiento y paneles de datos

- **Type:** feature
- **Priority:** P1
- **Estimate:** 40 min
- **Rubric / Spec:** C3, C4
- **Depends on:** CO-028
- **Paths:** web/src/features/mapa/graficasCrecimiento.tsx, web/src/features/mapa/coloresCrecimiento.ts, web/src/features/mapa/tiposCrecimiento.ts
- **Freeze-Allowed:** yes
- **Test-First:** no (gráficas: build y capturas)
- **Acceptance:** Recipe: dashboard · Hero: la gráfica de crecimiento con su fuente, Colores de los tokens, ejes legibles, `tipo_dato` visible en cada serie
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint'`
- **Next step:** abrir `graficasCrecimiento.tsx`

## CO-033 · Vista de la vecina: ruta de compras sin cadenas

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4 · `IDEA-v2.md`
- **Depends on:** CO-028
- **Paths:** web/src/features/usuario/
- **Freeze-Allowed:** yes
- **Test-First:** no (pantalla: build, design-lint y capturas)
- **Acceptance:** Recipe: flow · Hero: la ruta dibujada sobre el mapa con las paradas, Texto de 18 px, controles de 48 px o más, flujo de 3 pasos claro; estados de carga, vacío y error, Se usa bien a 390×844
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint'`
- **Next step:** abrir `usuario/index.tsx` y la pantalla fijada de flujo

## CO-034 · Vista del negocio: alta y su ficha

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4 · `IDEA-v2.md`
- **Depends on:** CO-028
- **Paths:** web/src/features/negocio/
- **Freeze-Allowed:** yes
- **Test-First:** no (pantalla: build, design-lint y capturas)
- **Acceptance:** Recipe: detail · Hero: la ficha del negocio recién dado de alta con el repartidor de su colonia, Campos extraídos de la nota de voz visibles y editables; cada dato con su etiqueta, Estados de carga, vacío y error; se ve bien a 390×844
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint'`
- **Next step:** abrir `negocio/index.tsx` y la receta detail

## CO-035 · Portal del repartidor: acceso, mapa de ofertas y mis rutas

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4 · `IDEA-v2.md` §4.4
- **Depends on:** CO-028
- **Uses contract:** CO-036
- **Paths:** web/src/features/repartidor/index.tsx, web/src/features/repartidor/MapaOfertas.tsx, web/src/features/repartidor/cliente.ts
- **Freeze-Allowed:** yes
- **Test-First:** no (pantalla: build, design-lint y capturas)
- **Acceptance:** Recipe: map + panel · Hero: el mapa de ofertas con la primera ruta resaltada, El acceso con número `R-00001` sigue funcionando sin cambios de comportamiento, Se usa con una mano a 390×844
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint'`
- **Next step:** abrir `repartidor/index.tsx` y la receta map + panel

## CO-036 · Portal del repartidor: incentivos con la bici

- **Type:** feature
- **Priority:** P1
- **Estimate:** 30 min
- **Rubric / Spec:** C4 · `IDEA-v2.md` §4.4
- **Depends on:** CO-028
- **Uses contract:** CO-035
- **Paths:** web/src/features/repartidor/Incentivos.tsx, web/src/features/repartidor/incentivos.css
- **Freeze-Allowed:** yes
- **Test-First:** no (pantalla: build, design-lint y capturas)
- **Acceptance:** Recipe: list · Hero: la bici en tarjeta grande con la barra "te faltan X rutas", `tipo_dato: "simulado"` visible; avance animado y con `prefers-reduced-motion` apagado
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint'`
- **Next step:** abrir `Incentivos.tsx`

## CO-037 · Correr el recorrido de la demo en navegador real y arreglar lo roto a 1280 y 390

- **Type:** bug
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C1, C4
- **Depends on:** CO-029, CO-030, CO-031, CO-033, CO-034, CO-035, CO-036
- **Paths:** web/src/, .uak-shots/CO-037/
- **Freeze-Allowed:** yes
- **Test-First:** no (recorrido visual con Playwright y capturas)
- **Acceptance:** Las 5 rutas (`#/`, `#/sedeco`, `#/usuario`, `#/negocio`, `#/repartidor`) capturadas a 1280×720 y 390×844 con movimiento reducido, sin scroll horizontal ni texto cortado, Contraste AA, foco visible y controles de 48 px o más revisados; lo roto corregido en esta tarea
- **Verify:** `bash -c 'npm --prefix web run build && bash .uak/bin/design-lint && ls .uak-shots/CO-037'`
- **Next step:** `DEMO_MODE=1 bash scripts/demo.sh` y recorrer cada ruta

## CO-038 · Capturas reales y portada del README

- **Type:** docs
- **Priority:** P1
- **Estimate:** 25 min
- **Rubric / Spec:** C4
- **Depends on:** CO-037
- **Paths:** docs/media/, README.md
- **Freeze-Allowed:** yes
- **Test-First:** no (docs)
- **Acceptance:** Banner y capturas nuevos en `docs/media/` tomados de la app real con `DEMO_MODE=1`; el README los usa, El README no promete nada que la app no haga
- **Verify:** `bash -c 'ls docs/media/*.png && grep -q "docs/media" README.md'`
- **Next step:** tomar las capturas con Playwright

## CO-039 · Guion de 5 minutos para directivos y ensayo limpio

- **Type:** demo
- **Priority:** P0
- **Estimate:** 30 min
- **Rubric / Spec:** C1, C4
- **Depends on:** CO-037
- **Paths:** docs/demo/
- **Freeze-Allowed:** yes
- **Test-First:** no (guion y ensayo)
- **Acceptance:** Guion de 5 minutos con la frase del wow, probado en un clon limpio con `DEMO_MODE=1`, y plan B sin red, Lista de lo que NO se promete (cifras simuladas, sin llaves)
- **Verify:** `bash -c 'test -s docs/demo/guion-directivos.md'`
- **Next step:** `bash .uak/bin/uak demo`

## CO-040 · Pruebas de la ruta de la demo en la API

- **Type:** feature
- **Priority:** P1
- **Estimate:** 30 min
- **Rubric / Spec:** C1
- **Depends on:** None
- **Paths:** app/tests/test_ruta_demo.py
- **Freeze-Allowed:** yes
- **Acceptance:** Con `DEMO_MODE=1`, el repartidor R-00001 entra y ve ofertas; el mapa y la ruta responden con `tipo_dato` en cada cifra, Una ruta o repartidor desconocidos dan 404 sin romper
- **Tests:** repartidor_demo_entra_con_su_numero, mapa_responde_con_tipo_dato_en_cada_cifra, ruta_desconocida_da_404
- **Verify:** `uv run pytest -q app/tests/test_ruta_demo.py`
- **Next step:** `uak red CO-040` con los tres nombres

## CO-041 · Vite lee la llave de Mapbox del .env de la raíz

- **Type:** bug
- **Priority:** P0
- **Estimate:** 10 min
- **Rubric / Spec:** C4
- **Depends on:** None
- **Paths:** web/vite.config.ts
- **Freeze-Allowed:** yes
- **Test-First:** no (config de build de una línea; se verifica con build)
- **Acceptance:** `defineConfig` usa `envDir: '..'`; con `VITE_MAPBOX_TOKEN` en el `.env` raíz el mapa dibuja, sin la llave el aviso sigue claro
- **Verify:** `bash -c 'grep -q "envDir" web/vite.config.ts && npm --prefix web run build'`
- **Next step:** agregar `envDir: '..'` en `web/vite.config.ts`

## CO-042 · Resumen SEDECO: etiquetar 'abiertos' en tipo_campos (tianguis abiertos, real) (follow-up of CO-012)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-012
- **Follow-up of:** CO-012
- **Paths:** web/src/features/mapa/, app/routers/mapa.py, app/services/mapa.py, app/tests/test_mapa.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - Resumen SEDECO: etiquetar 'abiertos' en tipo_campos (tianguis abiertos, real)
- **Verify:** `uv run pytest -q app/tests/test_mapa.py && npm --prefix web run build`

## CO-043 · Inicio: hexágonos sin verde (jade solo para éxito), paleta rosa y gris (follow-up of CO-029)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-029
- **Follow-up of:** CO-029
- **Paths:** web/src/features/inicio/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Inicio: hexágonos sin verde (jade solo para éxito), paleta rosa y gris
- **Verify:** `bash -c 'npm --prefix web run build'`

## CO-044 · Negocio: sin alta todavía no es 'sin conexión'; aviso correcto para el ejemplo de Doña Lupe (follow-up of CO-034)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-034
- **Follow-up of:** CO-034
- **Paths:** web/src/features/negocio/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Negocio: sin alta todavía no es 'sin conexión'; aviso correcto para el ejemplo de Doña Lupe
- **Verify:** `bash -c 'npm --prefix web run build'`

## CO-045 · Mapa en móvil: más mapa visible (capas plegables) y leyenda sin nombre interno (follow-up of CO-037)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-037
- **Follow-up of:** CO-037
- **Paths:** web/src/features/, .uak-shots/CO-037/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Mapa en móvil: más mapa visible (capas plegables) y leyenda sin nombre interno
- **Verify:** `bash -c 'npm --prefix web run build && ls .uak-shots/CO-037/*.png'`

## CO-046 · Inicio con la Maqueta viva elegida: maqueta 3D de Coyoacán, selector de día y pines, en paleta rosa (follow-up of CO-029)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-029
- **Follow-up of:** CO-029
- **Paths:** web/src/features/inicio/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Inicio con la Maqueta viva elegida: maqueta 3D de Coyoacán, selector de día y pines, en paleta rosa
- **Verify:** `bash -c 'npm --prefix web run build'`

## CO-047 · Maqueta de Inicio: quitar pines de tianguis que caen fuera de los hexágonos (follow-up of CO-029)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-029
- **Follow-up of:** CO-029
- **Paths:** web/src/features/inicio/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Maqueta de Inicio: quitar pines de tianguis que caen fuera de los hexágonos
- **Verify:** `bash -c 'npm --prefix web run build'`

## CO-048 · Mapa principal con color: capas de actividad, oferta y población en la rampa rosa (follow-up of CO-031)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-031
- **Follow-up of:** CO-031
- **Paths:** web/src/features/mapa/index.tsx, web/src/features/mapa/MapaHex.tsx, web/src/features/mapa/puntos.ts, web/src/features/mapa/datos.ts, web/src/lib/map/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Mapa principal con color: capas de actividad, oferta y población en la rampa rosa
- **Verify:** `bash -c 'npm --prefix web run build && npm --prefix web test'`

## CO-049 · Landing: bloques de la maqueta suben al cargar y hacen una ola al cambiar de día (follow-up of CO-029)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-029
- **Follow-up of:** CO-029
- **Paths:** web/src/features/inicio/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Landing: bloques de la maqueta suben al cargar y hacen una ola al cambiar de día
- **Verify:** `bash -c 'npm --prefix web run build'`

## CO-050 · Mapa principal: rosa más intenso en zonas de poca actividad (follow-up of CO-048)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-048
- **Follow-up of:** CO-048
- **Paths:** web/src/features/mapa/index.tsx, web/src/features/mapa/MapaHex.tsx, web/src/features/mapa/puntos.ts, web/src/features/mapa/datos.ts, web/src/lib/map/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Mapa principal: rosa más intenso en zonas de poca actividad
- **Verify:** `bash -c 'npm --prefix web run build && npm --prefix web test'`

## CO-051 · Portal del repartidor: el mapa abre encuadrado en sus ofertas, no en toda la ciudad (follow-up of CO-035)

- **Type:** follow-up
- **Priority:** P1
- **Depends on:** CO-035
- **Follow-up of:** CO-035
- **Paths:** web/src/features/repartidor/index.tsx, web/src/features/repartidor/MapaOfertas.tsx, web/src/features/repartidor/cliente.ts
- **Freeze-Allowed:** no
- **Acceptance:**
  - Portal del repartidor: el mapa abre encuadrado en sus ofertas, no en toda la ciudad
- **Verify:** `bash -c 'npm --prefix web run build'`
