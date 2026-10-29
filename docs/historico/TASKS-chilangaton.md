# TASKS · Pulso Barrial (Chilangatón, Reto 1 · Comercio popular y barrial)

State lives on the `claims` branch (`uak status`); this file holds only tasks. Source of truth for the product: `IDEA.md`.
Rubric IDs are the official ones in `.uak/PROJECT.md` (C1 Pertinencia · C2 Impacto · C3 Innovación · C4 Viabilidad ·
C5 Prototipo · C6 Accesibilidad · C7 Asequibilidad · C8 Escalabilidad), not the provisional table in IDEA.md §8.

Reglas de este plan (corte de la solución 15:00, freeze 13:57):
- Lo pesado se **simula**: DENUE, CNBV, Banxico, Censo y el diccionario de 2,000 artículos no se descargan. Scripts en
  `pipeline/` generan datos plausibles para Coyoacán (09003) e Iztapalapa (09007). Todo registro simulado lleva
  `tipo_dato: "simulado"` (o `"estimado"` si sale de un cálculo sobre simulados) y la UI muestra esa etiqueta.
- Real en vivo: mapa Mapbox, nota de voz por Telegram con OpenAI, rutas a pie de Mapbox, los tianguis que el equipo
  de campo deje en `data/campo/tianguis_verificados.csv` (si existe, entra con `tipo_dato: "real"`).
- Nunca se presenta una cifra simulada como real. Las cifras citables del pitch salen de IDEA.md §10.
- `DEMO_MODE=1` hace que todo funcione sin internet y sin llaves (fixtures grabados).
- Backend: un router por archivo en `app/routers/` (main.py los descubre solo). Frontend: una carpeta por vista en
  `web/src/features/<vista>/index.tsx` que exporta `default`, `route`, `label` y `order` (App.tsx las descubre solo).
- Interfaz en español de México, lenguaje claro, texto grande, alto contraste (rúbrica C6).

## PB-001 · Setup FastAPI + React con todas las dependencias, shell por rol y smoke

- **Type:** setup
- **Priority:** P0
- **Estimate:** 30 min
- **Rubric / Spec:** C5 · `IDEA.md` Apéndice B, `.uak/stacks/fastapi-react/STACK.md`
- **Depends on:** None
- **Uses contract:** None
- **Paths:** pyproject.toml, uv.lock, .python-version, app/__init__.py, app/main.py, app/config.py, app/routers/__init__.py, app/services/__init__.py, app/tests/__init__.py, app/tests/test_health.py, web/package.json, web/package-lock.json, web/index.html, web/vite.config.ts, web/tsconfig.json, web/tsconfig.app.json, web/tsconfig.node.json, web/eslint.config.js, web/src/App.tsx, web/src/main.tsx, web/src/index.css, web/src/vite-env.d.ts, web/src/lib/api.ts, .env.example, .gitignore, .uak/bin/smoke-project, .uak/bin/.smoke-project.provenance
- **Freeze-Allowed:** no
- **Acceptance:**
  - Sigue `.uak/stacks/fastapi-react/STACK.md` (main.py autodescubre routers y sirve `web/dist`)
  - Python: fastapi, uvicorn[standard], pydantic-settings, httpx, h3 (v4), rapidfuzz, openai, python-telegram-bot, qrcode[pil], jinja2, python-multipart; dev: pytest, ruff, httpx2
  - Web: mapbox-gl, h3-js, @turf/turf, tailwindcss, @tailwindcss/vite, motion, @phosphor-icons/react, @fontsource-variable/geist
  - `pyproject.toml`: `testpaths = ["app/tests", "pipeline/tests"]`, `pythonpath = ["."]`
  - `app/config.py` es el único lugar con IDs de modelo y llaves (desde `.env`): OPENAI_API_KEY, OPENAI_MODEL, OPENAI_FALLBACK_MODEL, OPENAI_TRANSCRIBE_MODEL, MAPBOX_TOKEN, TELEGRAM_BOT_TOKEN, ALCALDIAS=09003,09007, DEMO_MODE; `.env.example` con los nombres vacíos (IDEA.md §12) y `VITE_MAPBOX_TOKEN`
  - `App.tsx`: barra superior fija con el selector de rol, construida con `import.meta.glob("./features/*/index.tsx")`; cada feature exporta `route` (p. ej. `"sedeco"`), `label` y `order`; ruteo por hash (`#/sedeco`, `#/usuario`, `#/negocio/:id`); por defecto `#/sedeco`; sin features muestra "Cargando vistas…"
  - `.gitignore` agrega `data/raw/` y `data/live/`
  - `bash .uak/bin/uak init-smoke --command "<Product smoke de STACK.md>"` y `bash .uak/bin/smoke` sale 0
- **Verify:** `bash .uak/bin/smoke`
- **Next step:** `uv init --bare --name app --python 3.12 --pin-python .` y seguir STACK.md

## PB-002 · Contrato: esquemas Pydantic, tipos TS y fixtures de todas las APIs

- **Type:** contract
- **Priority:** P0
- **Estimate:** 30 min
- **Rubric / Spec:** C5 · `IDEA.md` §6, Apéndice C
- **Depends on:** None
- **Uses contract:** PB-001
- **Paths:** app/schemas/, app/fixtures/, web/src/lib/types.ts, app/tests/test_schemas.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - Modelos Pydantic de IDEA.md §6: PuntoBarrial, Negocio, Hexagono (feature GeoJSON), DineroAlcaldia, Articulo, Programa, Alta, Ficha, Evento; respuestas de Apéndice C: RutaRequest/RutaResponse, ArticulosResponse, NegocioDetalle (ficha, avance, escalera, programas), AltasLive, SedecoResumen
  - Toda cifra visible viaja con `tipo_dato: Literal["real","estimado","simulado"]` (o `tipo_campos` en el hexágono)
  - `web/src/lib/types.ts` espeja los mismos tipos con los mismos nombres de campo
  - `app/fixtures/<endpoint>.json`: una respuesta de ejemplo válida por endpoint de Apéndice C (≥ 30 hexágonos alrededor de 19.3467,-99.1617, 8 tianguis, 20 negocios, una ruta de 4 paradas, la ficha de Doña Lupe); los frontends trabajan contra estos mocks
  - Cada fixture valida contra su modelo en la prueba
- **Verify:** `uv run pytest -q app/tests/test_schemas.py`
- **Next step:** crear `app/schemas/entidades.py` con los modelos de §6

## PB-003 · Diseño accesible y componente de mapa compartido

- **Type:** contract
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C6 · `IDEA.md` Apéndice D
- **Depends on:** None
- **Uses contract:** PB-001
- **Paths:** web/DESIGN.md, web/src/lib/ui/, web/src/lib/map/
- **Freeze-Allowed:** no
- **Acceptance:**
  - No hay tiempo para 3 direcciones: una sola, la recomendada en Apéndice D (base clara tipo documento público, acento cálido de mercado para impulso, paleta secuencial para actividad), escrita en `web/DESIGN.md` con la skill design-taste-frontend
  - Tokens como variables CSS en `web/src/lib/ui/tokens.css` (importado por `web/src/lib/ui/index.ts`); contraste AA, texto base ≥ 18 px, botones ≥ 48 px, legible en proyector a 1280×720
  - Componentes en `web/src/lib/ui/`: `Etiqueta` (real / estimado / simulado, siempre visible junto a una cifra), `Boton`, `Tarjeta`, `Chip`
  - `web/src/lib/map/MapaBase.tsx`: Mapbox GL v3 con `import.meta.env.VITE_MAPBOX_TOKEN`, cámara inicial inclinada 50° sobre Coyoacán con Iztapalapa a la vista, prop `onReady(map)`; sin token muestra un aviso claro en lugar de romperse
  - Helper `web/src/lib/map/hex.ts`: celdas H3 → GeoJSON con `h3-js` para capas `fill-extrusion`
- **Verify:** `test -s web/DESIGN.md && npm --prefix web run build`
- **Next step:** escribir `web/DESIGN.md` con la dirección de Apéndice D

## PB-004 · Datos simulados: hexágonos, población, dinero CNBV y tianguis

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C2 · `IDEA.md` §6, A.1–A.4
- **Depends on:** None
- **Uses contract:** PB-001, PB-002
- **Paths:** pipeline/__init__.py, pipeline/geo/, pipeline/tests/__init__.py, pipeline/tests/test_geo.py, data/processed/hex.geojson, data/processed/tianguis_abierto.json, data/processed/cnbv_tpv_municipios.json, data/fuentes/geo.md
- **Freeze-Allowed:** no
- **Acceptance:**
  - `uv run python -m pipeline.geo` genera los 3 archivos de forma determinista (semilla fija) para ALCALDIAS
  - Rejilla H3 res 9 sobre polígonos aproximados de Coyoacán e Iztapalapa (contornos simplificados escritos a mano, documentados como aproximados)
  - Hexágonos con `poblacion`, `negocios_barriales`, `negocios_total`, `actividad_tpv_est`, `impulso`, `oculto`, `cluster_id`, `tipo_campos`, `periodo_cnbv`; impulso con la fórmula exacta de A.3; `oculto = negocios_total < 3`; la suma de actividad por alcaldía = total de la alcaldía (± 0.5%)
  - Iztapalapa más densa en población y con menos actividad por adulto que Coyoacán, para que el contraste del paso 1 se vea
  - ~60 tianguis y mercados con días y horarios (A.4); si existe `data/campo/tianguis_verificados.csv` se agregan con `tipo_dato: "real"`; el resto `"simulado"`
  - `data/fuentes/geo.md` dice qué es simulado, qué es real y qué fuente real lo reemplaza (CNBV BDIF, Censo 2020, SEDECO)
- **Verify:** `uv run pytest -q pipeline/tests/test_geo.py`
- **Next step:** `pipeline/geo/__main__.py` con los polígonos aproximados y `h3.geo_to_cells`

## PB-005 · Datos simulados: negocios con regla anti-cadenas, diccionario de artículos y programas

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C1 · `IDEA.md` §6, A.5, A.7
- **Depends on:** None
- **Uses contract:** PB-001, PB-002
- **Paths:** pipeline/negocios/, pipeline/articulos/, pipeline/tests/test_sin_cadenas.py, pipeline/tests/test_articulos_dic.py, data/processed/negocios.json, data/processed/articulo_giro.json, data/processed/programas.json, data/fuentes/negocios.md
- **Freeze-Allowed:** no
- **Acceptance:**
  - `uv run python -m pipeline.negocios` y `uv run python -m pipeline.articulos` son deterministas
  - ~500 negocios simulados tipo DENUE en las 2 alcaldías (abarrotes, tortillerías, recauderías, zapaterías, ferreterías, papelerías, fondas, estéticas…) con `h3` res 9, incluyendo ~40 cadenas (OXXO, Bodega Aurrera, Farmacias Similares…) que los 4 filtros de A.7 marcan `es_barrial=false` con `motivo_exclusion`
  - Los 4 filtros de A.7 son código real (giro, estrato, lista negra con rapidfuzz ≥ 90, repetición ≥ 5) sobre los datos simulados
  - `articulo_giro.json` con ≥ 300 artículos de México con sinónimos chilangos (jitomate, bolillo, chiles secos, tenis, pilas, recarga…), escritos a mano sin LLM, incluidos los 5 de la demo (IDEA.md §4 paso 3)
  - `programas.json` con Mercomuna, DiMo y CoDi (existe), y Puntos de barrio (propuesta), con `estado` y `url_oficial`
  - Prueba: 0 nombres de la lista negra con `es_barrial=true`; cada artículo de la demo resuelve a ≥ 1 clase
- **Verify:** `uv run pytest -q pipeline/tests/test_sin_cadenas.py pipeline/tests/test_articulos_dic.py`
- **Next step:** `pipeline/negocios/cadenas.txt` con la lista de A.7 y el generador

## PB-006 · API del mapa SEDECO: hexágonos, dinero por alcaldía, tianguis por día y hora

- **Type:** feature
- **Priority:** P0
- **Estimate:** 30 min
- **Rubric / Spec:** C2 · `IDEA.md` §4 pasos 1–2, Apéndice C
- **Depends on:** None
- **Uses contract:** PB-001, PB-002, PB-004
- **Paths:** app/routers/mapa.py, app/services/mapa.py, app/tests/test_mapa.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `GET /api/hex`, `GET /api/dinero/alcaldias`, `GET /api/tianguis?dia=0-6&hora=HH:MM` y `GET /api/sedeco/resumen` (altas hoy, rutas por hexágono, % población cubierta del día)
  - Lee `data/processed/`; si falta un archivo usa el fixture de `app/fixtures/` (nunca 500)
  - Hexágono `oculto` no devuelve cifras de dinero
  - `dia=2&hora=10:00` devuelve menos puntos abiertos que `dia=0&hora=10:00` con los fixtures
- **Verify:** `uv run pytest -q app/tests/test_mapa.py`
- **Next step:** `app/services/mapa.py` con la carga de archivos y respaldo a fixtures

## PB-007 · API de ruta de compras: lista → giros → ruta a pie sin cadenas

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C1 · `IDEA.md` §4 paso 3, A.5, A.6
- **Depends on:** None
- **Uses contract:** PB-001, PB-002, PB-005
- **Paths:** app/routers/ruta.py, app/services/ruta.py, app/services/articulos.py, app/services/mapbox.py, app/routers/eventos.py, app/services/eventos.py, app/tests/test_ruta.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `POST /api/articulos/interpretar` y `POST /api/ruta` con el contrato de Apéndice C; `POST /api/eventos`
  - Interpretación por reglas + diccionario + rapidfuzz (≥ 88); el LLM solo si hay llave y `DEMO_MODE=0`, con enum cerrado
  - Puntaje, desvío máximo y cobertura voraz de A.6; orden con Mapbox Optimization `walking` si hay token, si no vecino más cercano con líneas rectas y aviso
  - Invariante: ninguna parada con `es_barrial=false` (si pasa, 500); "por qué esta parada" con plantillas, nunca LLM
  - Cada parada registra `aparicion_ruta` en `data/live/eventos.jsonl` vía `app/services/eventos.py`
  - Para la lista de la demo devuelve 4–6 paradas, 0 cadenas, en < 3 s sin red; un artículo inexistente sale en `sin_resultado`
- **Verify:** `uv run pytest -q app/tests/test_ruta.py`
- **Next step:** `app/services/articulos.py` con la separación de la lista y la búsqueda en el diccionario

## PB-008 · Alta por voz: bot de Telegram + API de altas en vivo

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C6 · `IDEA.md` §4 paso 4, A.8
- **Depends on:** None
- **Uses contract:** PB-001, PB-002
- **Paths:** app/bot/, app/routers/altas.py, app/services/altas.py, app/tests/test_altas.py, scripts/simular_alta.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - Primero confirma los IDs de modelo con `GET /v1/models` y, si difieren de `.env`, avisa al humano con `uak msg human` (no edita `app/config.py`)
  - `uv run python -m app.bot` (long polling): nota de voz / texto + ubicación → transcripción → ficha con salida estructurada validada por Pydantic → el bot responde con la ficha y botones "Así queda" / "Corregir"; nada se publica sin "Así queda"
  - Al confirmar: `POST /api/altas` escribe en `data/live/altas.jsonl` (con `h3`) y un evento `alta`; el bot devuelve el link `/n/{slug}`
  - `GET /api/altas/live?desde=ts` devuelve las altas nuevas
  - `DEMO_MODE=1` o sin llave: transcripción y ficha grabadas en `app/bot/fixtures/` (Doña Lupe, IDEA.md §4 paso 4)
  - `uv run python scripts/simular_alta.py --caso dona-lupe` inyecta el alta sin Telegram
- **Verify:** `uv run pytest -q app/tests/test_altas.py`
- **Next step:** `app/services/altas.py` con el guardado en jsonl y la ficha grabada de Doña Lupe

## PB-009 · API del negocio y página web automática con QR

- **Type:** feature
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C7 · `IDEA.md` §4 paso 5, A.9, Apéndice D
- **Depends on:** None
- **Uses contract:** PB-001, PB-002, PB-005
- **Paths:** app/routers/negocio.py, app/services/negocio.py, app/routers/paginas.py, app/services/paginas.py, app/templates/, app/tests/test_negocio.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `GET /api/negocio/{id}` (negocios de `negocios.json` y altas de `data/live/altas.jsonl`): ficha, avance de 7 días desde eventos (simulado si no hay reales, etiquetado), escalera de barrio de 4 escalones con estado, programas de `programas.json`
  - `PUT /api/negocio/{id}/ficha`
  - `POST /api/negocio/{id}/pagina` genera la página con Jinja2 y QR; `GET /n/{slug}` la sirve (registra `vista_pagina`); `GET /n/{slug}/cartel` imprimible
  - Descripción: plantilla fija con datos de la ficha (sin LLM, sin costo); botón `wa.me` solo si hay número
  - La página se ve bien en celular y no muestra ventas ni ingresos
- **Verify:** `uv run pytest -q app/tests/test_negocio.py`
- **Next step:** `app/templates/pagina.html` y `app/services/paginas.py`

## PB-010 · Vista SEDECO: hexágonos 3D, dato real, barra de tiempo y altas en vivo

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C2 · `IDEA.md` §4 pasos 1, 2 y 6, Apéndice D
- **Depends on:** None
- **Uses contract:** PB-001, PB-002, PB-003, PB-006
- **Paths:** web/src/features/sedeco/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Exporta `route = "sedeco"`, `label = "SEDECO"`, `order = 1`; a 1280×720 sin scroll: mapa 70% / panel 30%
  - Hexágonos `fill-extrusion` (altura = actividad estimada, color = impulso) visibles en ≤ 15 s; selector de capa (actividad · oferta barrial · población · impulso)
  - Interruptor "Ver dato real" (coropleta de las 2 alcaldías con `tpv_por_adulto`)
  - Barra lun–dom + hora: los tianguis cerrados se apagan, cambia el % de población cubierta
  - Tarjeta al tocar un hexágono: cada cifra con su `Etiqueta` real / estimado / simulado y la fuente; oculto = "Menos de 3 negocios: sin cifras por privacidad"
  - Contador "altas hoy" que pregunta `/api/altas/live` cada 3 s; un alta nueva aparece como punto que pulsa en el mapa
  - Funciona con los fixtures de PB-002 si la API aún no existe
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/src/features/sedeco/index.tsx` con `MapaBase` y la capa de hexágonos

## PB-011 · Vista Usuario: lista del mandado → ruta a pie de barrio

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C1 · `IDEA.md` §4 paso 3, Apéndice D
- **Depends on:** None
- **Uses contract:** PB-001, PB-002, PB-003, PB-007
- **Paths:** web/src/features/usuario/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Exporta `route = "usuario"`, `label = "Vecina"`, `order = 2`
  - Caja de texto grande con el ejemplo de la demo y botón "Armar mi ruta"; botón "Usar mi ubicación" con respaldo a la sede (Utopía Elena Poniatowska)
  - Ruta dibujada en el mapa, lista de paradas con artículos, chips de pago y Mercomuna, "por qué esta parada", chip resumen "0 cadenas · 1.8 km · N paradas en zonas que necesitan clientes"
  - Artículos sin resultado visibles; botones "Compartir por WhatsApp" (`wa.me`) y "Compré aquí" por parada (`POST /api/eventos`)
  - Estados vacío, cargando ("Buscando en los negocios de tu barrio…"), error y datos de ejemplo etiquetados
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/src/features/usuario/index.tsx` contra el fixture de ruta

## PB-012 · Vista Negocio: ficha, avance, escalera de barrio, programas y página web

- **Type:** feature
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C7 · `IDEA.md` §4 paso 5, Apéndice D
- **Depends on:** None
- **Uses contract:** PB-001, PB-002, PB-003, PB-009
- **Paths:** web/src/features/negocio/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Exporta `route = "negocio"`, `label = "Negocio"`, `order = 3`; `#/negocio/:id` con selector de negocio (Doña Lupe primero)
  - Ficha, "Mi avance" privado (apariciones en rutas, compré aquí, visitas; 7 días, etiquetado simulado cuando lo sea), escalera de 4 escalones con estado y siguiente acción, programas con su estado (existe / por verificar / propuesta)
  - Botón "Generar mi página" con vista previa, QR y link al cartel
  - Lenguaje claro y botones grandes: lo puede usar una persona mayor
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/src/features/negocio/index.tsx` contra el fixture de NegocioDetalle

## PB-013 · Integración: datos simulados en todas las vistas, DEMO_MODE e historia de la plataforma

- **Type:** integration
- **Priority:** P0
- **Estimate:** 30 min
- **Rubric / Spec:** C5 · `IDEA.md` §4, PB-021 en Apéndice E
- **Depends on:** PB-004, PB-005, PB-006, PB-007, PB-008, PB-010, PB-011
- **Uses contract:** PB-002
- **Paths:** app/services/demo.py, scripts/generar_historia.py, scripts/demo.sh, data/demo/, app/tests/test_demo.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `scripts/generar_historia.py` crea `data/demo/plataforma_simulada.json` (búsquedas, rutas y "compré aquí" de 7 días, `demo_data: true`)
  - `scripts/demo.sh` construye el web y levanta todo en un proceso (`:8000`) más el bot si hay token
  - Prueba de punta a punta con `DEMO_MODE=1` y sin red: los pasos 1–6 de IDEA.md §4 responden (hex, tianguis por día, ruta de la demo con 0 cadenas, alta simulada de Doña Lupe aparece en `/api/altas/live` y en `/api/negocio/{id}`)
  - Lista de lo que quedó simulado en `data/demo/README.md` para decirlo en el pitch
- **Verify:** `DEMO_MODE=1 uv run pytest -q app/tests/test_demo.py`
- **Next step:** `app/tests/test_demo.py` con los 6 pasos

## PB-014 · Panel de crecimiento SEDECO y escalabilidad

- **Type:** feature
- **Priority:** P1
- **Estimate:** 30 min
- **Rubric / Spec:** C8 · `IDEA.md` §4 paso 6
- **Depends on:** None
- **Uses contract:** PB-001, PB-002, PB-003
- **Paths:** app/routers/crecimiento.py, app/services/crecimiento.py, app/tests/test_crecimiento.py, web/src/features/crecimiento/
- **Freeze-Allowed:** no
- **Acceptance:**
  - `GET /api/sedeco/crecimiento`: serie trimestral por alcaldía (simulada, etiquetada), altas de negocios por año (simulada), altas de plataforma hoy (real de `altas.jsonl`), rutas por hexágono
  - Vista `route = "crecimiento"`, `label = "Crecimiento"`, `order = 4` con 3 gráficas simples y el contador "altas hoy"
  - Bloque "Cómo escala": las 16 alcaldías con `ALCALDIAS` como parámetro y costo casi cero (Telegram, datos abiertos), en texto claro
- **Verify:** `uv run pytest -q app/tests/test_crecimiento.py && npm --prefix web run build`
- **Next step:** `app/services/crecimiento.py` con las series simuladas

## PB-015 · Pitch y respuestas al jurado: 6 diapositivas con la rúbrica oficial

- **Type:** docs
- **Priority:** P1
- **Estimate:** 40 min
- **Rubric / Spec:** C3 · `IDEA.md` §10, §11, Apéndice G
- **Depends on:** None
- **Uses contract:** None
- **Paths:** docs/pitch/
- **Freeze-Allowed:** yes
- **Acceptance:**
  - `docs/pitch/guion.md`: guion de 3 min de Apéndice G ajustado a los 8 criterios oficiales (una frase por criterio, sobre todo C3 innovación, C4 viabilidad, C7 asequibilidad y C8 escalabilidad)
  - `docs/pitch/diapositivas.md`: máximo 6 diapositivas; cada cifra con su fuente de §10; lo simulado dicho como simulado
  - `docs/pitch/preguntas.md`: las respuestas de §11, incluida "¿el dato es real?"
  - Listo para los 30 min de la semifinal
- **Verify:** `test -s docs/pitch/guion.md && test -s docs/pitch/diapositivas.md`
- **Next step:** copiar Apéndice G a `docs/pitch/guion.md` y mapear cada bloque a C1–C8

## PB-016 · Demo y entrega: ensayo, video plan B, README y formulario

- **Type:** demo
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C5 · `.uak/PROJECT.md` Event, `IDEA.md` §4
- **Depends on:** PB-013
- **Uses contract:** None
- **Paths:** docs/demo/, README.md
- **Freeze-Allowed:** yes
- **Acceptance:**
  - `docs/demo/guion.md`: los 6 pasos con qué clic y qué decir, ≤ 3 min, primer wow ≤ 15 s
  - `README.md` en inglés: qué es, cómo correrlo (`scripts/demo.sh`, `DEMO_MODE=1`), qué es real y qué es simulado
  - Ensayo desde un clon limpio con `DEMO_MODE=1` y anotado en `docs/demo/ensayo.md`
  - `docs/demo/entrega.md`: lista de lo que pide el formulario https://forms.gle/4BFrPf49hDGx8Q5s7 y el link del repo; el humano Victor envía el formulario antes de las 14:43 y guarda el recibo
  - Video plan B del flujo completo grabado por un humano (`docs/demo/plan-b.mp4` o link)
- **Verify:** `test -s docs/demo/guion.md && test -s README.md`
- **Next step:** `bash scripts/demo.sh` desde un clon limpio y escribir `docs/demo/guion.md`
