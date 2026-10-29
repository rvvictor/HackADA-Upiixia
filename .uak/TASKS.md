# TASKS · HackADA (backlog vacío; el plan llega con /uak-plan)

State lives on the `claims` branch (`uak status`); this file holds only tasks. IDs are `PREFIX-NNN` (`HACK-001`, `T-001`, `API-120`).
Priority is `P0/P1/P2`. Type is `setup/contract/spike/feature/bug/integration/demo/docs`. Check the graph with `uak graph`.

Format rules (the CLI parses them):
- `Depends on:` real IDs separated by commas, or `None`. It blocks the claim until they are INTEGRATED. Text in parentheses is ignored.
- `Uses contract:` soft dependency. It never blocks; it routes contract notices. Work against the mock.
- `Paths:` relative paths separated by commas; directories end in `/`. Reserve everything you will touch.
- `Verify:` one exact command that exits 0 when the task is done.
- `Estimate:` minutes or hours, used for the critical path.

Plan de colonIA (HackADA, reto Mercaditos locales). Fuente: `IDEA-v2.md` (cambios) sobre `IDEA.md` (base). Rúbrica `.uak/PROJECT.md`:
C1 núcleo funcional · C2 uso inteligente de IA · C3 trazabilidad de datos · C4 diseño de experiencia (25 pts cada una).
Reglas: el LLM nunca produce una cifra visible; toda cifra lleva `tipo_dato` (`real`/`estimado`/`simulado`); `DEMO_MODE=1` corre sin red ni llaves.
`data/raw/` no se versiona: las pruebas usan mini-muestras en `pipeline/tests/` o `app/fixtures/`. Las llaves viven solo en `.env`.
Ola 1 sin dependencias duras (CO-01..09, CO-13); consumidores usan `Uses contract` + fixtures. Ola 2: CO-10, 11, 12, 14, 15.

## CO-01 · Contrato v2: esquemas, fixtures y tipos TS

- **Type:** contract
- **Priority:** P0
- **Estimate:** 25 min
- **Rubric / Spec:** C1, C3 · `IDEA-v2.md` §2, §7
- **Depends on:** None
- **Uses contract:** None
- **Paths:** app/schemas/, app/config.py, app/fixtures/repartidores.json, app/fixtures/ofertas.json, app/fixtures/incentivos.json, app/fixtures/puntos.json, app/fixtures/alcaldias.json, app/tests/test_schemas_v2.py, web/src/lib/types.ts, data/processed/incentivos.json
- **Freeze-Allowed:** no
- **Acceptance:**
  - `tipo` de punto barrial: `tianguis | mercado | negocio_local`
  - Modelos Pydantic Repartidor, Oferta, Incentivo, Alcaldia (con `prioridad`), Colonia; sin foto de ID ni prioridad en la respuesta pública del repartidor
  - `app/config.py`: pesos de prioridad, umbral de negocio local y `denue_token` ya existe
  - Fixtures válidas por endpoint de `IDEA-v2.md` §8 y `data/processed/incentivos.json` (bici destacada, `tipo_dato: "simulado"`)
  - `web/src/lib/types.ts` espeja los nombres de campo
- **Verify:** `uv run pytest -q app/tests/test_schemas_v2.py app/tests/test_schemas.py`
- **Next step:** crear `app/schemas/repartidores.py` con los modelos de §7

## CO-02 · Paleta sin neón y marca colonIA

- **Type:** feature
- **Priority:** P0
- **Estimate:** 35 min
- **Rubric / Spec:** C4 · `IDEA-v2.md` §3
- **Depends on:** None
- **Uses contract:** None
- **Paths:** web/src/features/inicio/, web/src/lib/ui/, web/src/index.css, web/index.html
- **Freeze-Allowed:** no
- **Acceptance:**
  - Fuera `--ci-rosa-luz`, `--ci-jade-luz`, `.ci-hero-glow`, `text-shadow` y `drop-shadow` de color; sombras solo neutras (≤ 0.15)
  - Base clara `#f6f7f4`, acento terracota apagado, todos los colores como tokens en `tokens.css`; contraste AA
  - Nombre visible "colonIA" en logo, inicio y título; la frase del wow de `IDEA-v2.md` §0 en Inicio; texto "negocios de barrio"
- **Verify:** `bash -c '! rg -n "glow|text-shadow|drop-shadow\(0 0" web/src' && npm --prefix web run build`
- **Next step:** `rg -n "luz|glow|shadow" web/src/features/inicio/inicio.css`

## CO-03 · Datos reales de las 16 alcaldías: tianguis, mercados, colonias, marginación

- **Type:** feature
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C3 · `IDEA-v2.md` §5, `data/fuentes/raw.md`
- **Depends on:** None
- **Uses contract:** CO-01
- **Paths:** pipeline/reales/, pipeline/tests/test_reales.py, pipeline/tests/muestras/, data/processed/tianguis_abierto.json, data/processed/mercados.json, data/processed/colonias.json, data/processed/marginacion_colonia.json, data/processed/contaminacion_colonia.json, data/fuentes/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Lee `data/raw/` (tianguis 1,367, mercados 329, colonias, marginación CONAPO 2020, contaminación) y escribe JSON en `data/processed/` con `tipo_dato: "real"`, `fuente` y `fecha_consulta: 2026-10-25` por fila
  - Corrige acentos mal codificados y unifica nombres de alcaldía (`COYOACÁN`/`COYOACAN`); las 16 alcaldías presentes
  - `colonias.json` por alcaldía con `prioridad: true` solo en 09003 y 09007
  - Una ficha por fuente en `data/fuentes/` (de dónde viene, columnas, qué sigue simulado)
  - Pruebas con mini-muestras, sin depender de `data/raw/`
- **Verify:** `uv run pytest -q pipeline/tests/test_reales.py`
- **Next step:** `uv run python -m pipeline.reales` leyendo `data/raw/ubicacion_tianguis.csv`

## CO-04 · DENUE: negocios locales reales (Coyoacán e Iztapalapa primero)

- **Type:** feature
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C3, C1 · `IDEA-v2.md` §2, `IDEA.md` A.7
- **Depends on:** None
- **Uses contract:** CO-01
- **Paths:** pipeline/denue/, pipeline/tests/test_denue.py, pipeline/tests/muestras/denue.json, data/processed/negocios_denue.json, data/fuentes/denue.md
- **Freeze-Allowed:** no
- **Acceptance:**
  - Una descarga única (no consulta en vivo en la demo) con `DENUE_TOKEN` desde `app/config.py`: 09003 y 09007 completas, el resto de alcaldías con muestra acotada; sin llamadas en paralelo
  - Filtra comercio al por menor y servicios, estrato 0 a 5 o 6 a 10, sin cadenas (`pipeline/negocios/cadenas.txt`); cada registro con `id_denue`, `tipo: "negocio_local"`, `tipo_dato: "real"`
  - El token nunca aparece en logs ni archivos; ficha `data/fuentes/denue.md` con fecha y términos de uso
  - Pruebas sin red, con muestra grabada
- **Verify:** `uv run pytest -q pipeline/tests/test_denue.py`
- **Next step:** consulta `Buscar` de DENUE por radio desde el centro de cada colonia; solo la persona con `DENUE_TOKEN` en su `.env` puede reclamarla

## CO-05 · API de repartidores, ofertas e incentivos con priorización

- **Type:** feature
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C1 · `IDEA-v2.md` §4.3, §4.5, §8
- **Depends on:** None
- **Uses contract:** CO-01
- **Paths:** app/routers/repartidores.py, app/routers/ofertas.py, app/routers/incentivos.py, app/services/repartidores.py, app/services/ofertas.py, app/tests/test_repartidores.py, app/tests/test_ofertas.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `POST /api/repartidores` crea `R-XXXXX` con estado `pendiente_verificacion`; `POST /api/repartidores/codigo` y `/sesion` (código de 6 dígitos, sesión corta)
  - `GET /api/ofertas` ordena `prioridad DESC, cercanía ASC, antigüedad ASC`; con 2 repartidores en una colonia, el de 18 a 30 años que estudia la ve primero y el otro también la ve
  - `/tomar` y `/completar` cambian el estado; `GET /api/incentivos` con la bici primero
  - La foto de ID y la prioridad nunca salen en una respuesta
- **Verify:** `uv run pytest -q app/tests/test_repartidores.py app/tests/test_ofertas.py`
- **Next step:** `app/services/ofertas.py` con la función de orden y su prueba

## CO-06 · Mapa unificado: altura = color y sin vista Crecimiento

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4, C1 · `IDEA-v2.md` §1.1, §1.2, §9
- **Depends on:** None
- **Uses contract:** CO-01
- **Paths:** web/src/lib/map/hex.ts, web/src/lib/map/hex.test.ts, web/src/features/mapa/, web/src/features/sedeco/, web/src/features/crecimiento/, web/src/App.tsx
- **Freeze-Allowed:** no
- **Acceptance:**
  - La vista pasa a `#/mapa` (la ruta `#/sedeco` redirige); se elimina `#/crecimiento`
  - `pintarCapa(map, capa)`: altura y color leen la misma propiedad en todas las capas (prueba unitaria); selector de capa con leyenda de una rampa, `tipo_dato` y fuente
  - La serie CNBV y las altas por año salen en una tarjeta de alcaldía; selector de alcaldía con Coyoacán e Iztapalapa primero
  - `npm --prefix web run build` sin errores con el mapa vacío si no hay llave de Mapbox
- **Verify:** `npm --prefix web run build && npm --prefix web test --if-present`
- **Next step:** `web/src/lib/map/hex.ts:76` y `web/src/features/sedeco/MapaSedeco.tsx:39`

## CO-07 · Íconos por tipo de negocio, cluster y chips

- **Type:** feature
- **Priority:** P1
- **Estimate:** 30 min
- **Rubric / Spec:** C4 · `IDEA-v2.md` §1.3
- **Depends on:** None
- **Uses contract:** CO-01
- **Paths:** web/src/lib/map/iconos.ts, web/src/lib/map/ChipsTipo.tsx, web/public/iconos/
- **Freeze-Allowed:** no
- **Acceptance:**
  - Tres SVG con forma distinta (`tianguis`, `mercado`, `negocio`) y `agregarIconos(map, puntos)` con cluster y conteo
  - `ChipsTipo` enciende y apaga cada tipo; tooltip con etiqueta, no solo color
  - Se integra al mapa en CO-12, aquí solo se publica la API
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/public/iconos/tianguis.svg` y `iconos.ts` con `map.addImage`

## CO-08 · Portal de repartidores: acceso, mapa de ofertas y mis rutas

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C1, C4 · `IDEA-v2.md` §4.4, §9
- **Depends on:** None
- **Uses contract:** CO-01, CO-05
- **Paths:** web/src/features/repartidor/
- **Freeze-Allowed:** no
- **Acceptance:**
  - `#/repartidor`: entrada con número `R-XXXXX` y código de 6 dígitos; sin sesión no se ve ninguna ruta
  - Mapa de ofertas (60% de ancho) con negocio de origen, paradas, distancia, tiempo y pago estimado con su `tipo_dato`; botón **Tomar ruta**; polling cada 5 s sin recargar
  - Mis rutas con contador; aviso suave si el transporte no es ecológico
  - Trabaja contra `app/fixtures/` si la API aún no está
- **Verify:** `npm --prefix web run build`
- **Next step:** `web/src/features/repartidor/index.tsx` exportando `default`, `route: "repartidor"`, `label` y `order`

## CO-09 · Bot de Telegram: alta de repartidor por texto y voz

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C2, C1 · `IDEA-v2.md` §4.2, §4.5
- **Depends on:** None
- **Uses contract:** CO-01, CO-05
- **Paths:** app/bot/, app/services/repartidor_dialogo.py, app/tests/test_bot_repartidor.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `/start` ofrece Dar de alta negocio, Actualizar mi negocio y **Quiero ser repartidor**; preguntas de una en una, cada una acepta texto o nota de voz (transcripción) y el LLM solo extrae el campo con salida estructurada validada con Pydantic
  - Pasos: aviso de privacidad, nombre, edad, estudia, ID por foto (se borra tras verificar), alcaldía (Coyoacán e Iztapalapa primero), hasta 3 colonias, transporte con mensaje a favor de la bici, disponibilidad, resumen **Así queda** / **Corregir**
  - Termina con el número `R-XXXXX` y el link al portal; `DEMO_MODE=1` usa respuestas grabadas, sin red ni llaves
  - El LLM nunca produce una cifra visible
- **Verify:** `uv run pytest -q app/tests/test_bot_repartidor.py`
- **Next step:** `app/services/repartidor_dialogo.py` con la máquina de estados y su prueba

## CO-10 · Simulación para la demo: repartidor y ofertas

- **Type:** feature
- **Priority:** P0
- **Estimate:** 25 min
- **Rubric / Spec:** C1 · `IDEA-v2.md` §11 criterio 10
- **Depends on:** CO-05
- **Uses contract:** CO-01
- **Paths:** scripts/simular_repartidor.py, scripts/demo.sh, data/demo/, app/tests/test_demo_repartidor.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `scripts/simular_repartidor.py` da de alta un repartidor y publica ofertas con `demo_data: true`; la UI muestra la etiqueta
  - `DEMO_MODE=1 bash scripts/demo.sh` corre el flujo completo sin red ni llaves
- **Verify:** `uv run pytest -q app/tests/test_demo_repartidor.py`
- **Next step:** reutilizar `scripts/simular_alta.py` como plantilla

## CO-11 · Bot: ¿tienes repartidor para tu negocio? e invitación por link

- **Type:** feature
- **Priority:** P1
- **Estimate:** 30 min
- **Rubric / Spec:** C2, C1 · `IDEA-v2.md` §6
- **Depends on:** CO-09
- **Uses contract:** CO-05
- **Paths:** app/bot/negocio_repartidor.py, app/tests/test_bot_negocio_repartidor.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - Tras **Así queda** del alta de negocio, el bot pregunta por el repartidor: **Sí** (lo doy de alta yo, sin foto de ID, o le mando un link `t.me/<bot>?start=inv_<token>`) o **No** (red del barrio)
  - El repartidor queda ligado a `negocio_id` y ve primero las rutas de ese negocio
- **Verify:** `uv run pytest -q app/tests/test_bot_negocio_repartidor.py`
- **Next step:** extender el flujo de alta en `app/bot/`

## CO-12 · Integración del mapa: puntos con íconos, 16 alcaldías y datos reales

- **Type:** integration
- **Priority:** P0
- **Estimate:** 35 min
- **Rubric / Spec:** C1, C3, C4 · `IDEA-v2.md` §5, §8, §9
- **Depends on:** CO-06, CO-03
- **Uses contract:** CO-07, CO-04
- **Paths:** web/src/features/mapa/, app/routers/mapa.py, app/services/mapa.py, app/tests/test_mapa.py
- **Freeze-Allowed:** no
- **Acceptance:**
  - `GET /api/puntos?tipo=&bbox=` y `GET /api/alcaldias` sirven los datos reales de `data/processed/`; el frontend pide primero 09003 y 09007
  - Íconos, chips y cluster de CO-07 conectados al mapa; cada cifra con `tipo_dato` y fuente visibles
  - Si el JSON de hexágonos pasa de ~5 MB, usar resolución 7 en zoom lejano
- **Verify:** `uv run pytest -q app/tests/test_mapa.py && npm --prefix web run build`
- **Next step:** `app/services/mapa.py` leyendo `data/processed/tianguis_abierto.json`

## CO-13 · Entregables de la rúbrica: README, prompt, flujo de IA, cuello de botella, impacto y ruta a 30 días

- **Type:** docs
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C2, C3 · `.uak/PROJECT.md` (entregables)
- **Depends on:** None
- **Uses contract:** None
- **Paths:** README.md, IDEA.md, docs/entregables/, docs/legal/
- **Freeze-Allowed:** yes
- **Acceptance:**
  - README con qué es colonIA, cómo correrlo (`DEMO_MODE=1`), llaves y el UPIIXIA Agentic Kit
  - `docs/entregables/` con `prompt_inicial.md`, `flujo_ia.md` (dónde decide el modelo y dónde no), `cuello_botella.md`, `ficha_impacto.md` y `ruta_30_dias.md`; `docs/legal/priorizacion.md` con el pendiente legal
  - Ninguna cifra sin fuente: lo no verificado lleva la etiqueta "no verificado" o `simulado`
- **Verify:** `bash -c 'for f in prompt_inicial flujo_ia cuello_botella ficha_impacto ruta_30_dias; do test -s docs/entregables/$f.md || exit 1; done && test -s README.md'`
- **Next step:** `docs/entregables/flujo_ia.md` con el diagrama de la nota de voz a la ficha

## CO-14 · Portal de repartidores: incentivos con la bici destacada

- **Type:** feature
- **Priority:** P1
- **Estimate:** 25 min
- **Rubric / Spec:** C4 · `IDEA-v2.md` §4.4
- **Depends on:** CO-08
- **Uses contract:** CO-05
- **Paths:** web/src/features/repartidor/Incentivos.tsx, web/src/features/repartidor/incentivos.css
- **Freeze-Allowed:** no
- **Acceptance:**
  - Pestaña Incentivos con la bici en tarjeta grande y barra "te faltan X rutas"; el avance sube al completar rutas
  - Todo con `tipo_dato: "simulado"` visible
- **Verify:** `npm --prefix web run build`
- **Next step:** consumir `GET /api/incentivos`

## CO-15 · Ensayo limpio de la demo y video plan B

- **Type:** demo
- **Priority:** P0
- **Estimate:** 30 min
- **Rubric / Spec:** C1, C4 · `.uak/modes/sprint.md` §Submission checklist
- **Depends on:** CO-12, CO-10
- **Uses contract:** CO-08, CO-09
- **Paths:** docs/plan-b/, docs/demo/
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Guion de la demo con la frase del wow, probado en un clon limpio con `DEMO_MODE=1`
  - Video plan B del flujo completo en `docs/plan-b/`
  - Checklist de entrega completa; el link del formulario se agrega cuando se conozca
- **Verify:** `bash -c 'test -s docs/demo/guion.md && ls docs/plan-b | grep -q .'`
- **Next step:** `bash .uak/bin/uak demo`
