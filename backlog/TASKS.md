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
