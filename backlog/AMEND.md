# Amended tasks (uak plan --amend)

Append-only; the last section of an ID replaces its section in the backlog. Why: Paths can grow before review.

## CO-016 · Presentación del pitch con capturas reales de colonIA

- **Type:** demo
- **Priority:** P0
- **Estimate:** 40 min
- **Rubric / Spec:** C4 · pitch (`IDEA-v2.md` §0 frase del wow, `IDEA.md` §1 y §10)
- **Depends on:** CO-001, CO-002, CO-005, CO-007, CO-010, CO-011, CO-012, CO-014, CO-015, CO-017
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
## CO-019 · Favicon colonIA y mapa visible en Render

- **Type:** bug
- **Priority:** P0
- **Estimate:** 20 min
- **Rubric / Spec:** C4, C1 · `IDEA-v2.md` §9
- **Depends on:** None
- **Uses contract:** CO-002
- **Paths:** web/public/favicon.svg, web/src/features/mapa/
- **Freeze-Allowed:** yes
- **Acceptance:**
  - Icono de pestaña de colonIA (`web/public/favicon.svg`, sobrio, sin neón, reconocible a 16 px; forma de hexágono o pin de barrio con la "c"/"IA") que reemplaza al rayo morado por defecto; el título de la pestaña lo cambia CO-002 en `web/index.html` (si al integrarse CO-002 aún dice "Pulso Barrial", avisa en el reporte)
  - En https://colonia-hackada.onrender.com/#/mapa el mapa de Mapbox se ve: con Playwright (movimiento reducido) carga esa URL, registra errores de consola y respuestas de red fallidas, y diagnostica la causa (token con restricción de URL, WebGL, `/api/hex` o `/api/puntos` fallando, ruta de assets, etc.). Si la causa está en el código del mapa se corrige dentro de `web/src/features/mapa/`; si es configuración del token de Mapbox (restricciones de URL) o de Render, se documenta el paso exacto para el humano en la evidencia, sin tocar secretos
  - Captura del mapa funcionando (o del error exacto) guardada en la evidencia de `uak done`; sin llave visible en ningún archivo
- **Verify:** `bash -c 'test -s web/public/favicon.svg && ! grep -q "Pulso" web/public/favicon.svg' && npm --prefix web run build`
- **Next step:** abrir la URL de Render con Playwright y leer la consola
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
- **Verify:** `bash -c 'test -s web/DESIGN.md && ls web/public/design-lock/screens/*-1280.png && npm --prefix web run build'`
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
- **Verify:** `bash -c 'npm --prefix web run build'`
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
- **Verify:** `bash -c 'npm --prefix web run build'`
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
- **Verify:** `bash -c 'npm --prefix web run build'`
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
- **Verify:** `bash -c 'npm --prefix web run build'`
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
- **Verify:** `bash -c 'npm --prefix web run build'`
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
- **Verify:** `bash -c 'npm --prefix web run build'`
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
- **Verify:** `bash -c 'npm --prefix web run build'`
- **Next step:** abrir `Incentivos.tsx`

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
- **Acceptance:** Recipe: landing · Hero: el mapa vivo con la cifra de negocios dados de alta, todo visible a 1280×720 sin scroll, La frase de una línea, una cifra grande con su texto, el wow como pantalla real, tres pasos y un llamado a la acción hacia `#/sedeco`, Sin texto fuera de los tokens; respeta `prefers-reduced-motion`; se ve bien a 390×844
- **Verify:** `bash -c 'npm --prefix web run build'`
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
- **Acceptance:** Recipe: map + panel · Hero: el panel con día y hora y la cifra de actividad, Sin textos real · estimado · simulado en pantalla (uak decision CO-028); leyenda legible a 1280×720, Panel usable a 390×844 como hoja inferior
- **Verify:** `bash -c 'npm --prefix web run build'`
- **Next step:** abrir `PanelSedeco.tsx` y la receta map + panel

## CO-032 · Gráficas de crecimiento y paneles de datos

- **Type:** feature
- **Priority:** P1
- **Estimate:** 40 min
- **Rubric / Spec:** C3, C4
- **Depends on:** CO-028
- **Paths:** web/src/features/mapa/graficasCrecimiento.tsx, web/src/features/mapa/coloresCrecimiento.ts, web/src/features/mapa/tiposCrecimiento.ts
- **Freeze-Allowed:** yes
- **Test-First:** no (gráficas: build y capturas)
- **Acceptance:** Recipe: dashboard · Hero: la gráfica de crecimiento con su fuente, Colores de los tokens (rampa rosa), ejes legibles, sin textos real · estimado · simulado en pantalla (uak decision CO-028)
- **Verify:** `bash -c 'npm --prefix web run build'`
- **Next step:** abrir `graficasCrecimiento.tsx`

## CO-034 · Vista del negocio: alta y su ficha

- **Type:** feature
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C4 · `IDEA-v2.md`
- **Depends on:** CO-028
- **Paths:** web/src/features/negocio/
- **Freeze-Allowed:** yes
- **Test-First:** no (pantalla: build, design-lint y capturas)
- **Acceptance:** Recipe: detail · Hero: la ficha del negocio recién dado de alta con el repartidor de su colonia, Campos extraídos de la nota de voz visibles y editables; sin textos real · estimado · simulado en pantalla (uak decision CO-028), Estados de carga, vacío y error; se ve bien a 390×844
- **Verify:** `bash -c 'npm --prefix web run build'`
- **Next step:** abrir `negocio/index.tsx` y la receta detail

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
- **Acceptance:** Recipe: list · Hero: la bici en tarjeta grande con la barra "te faltan X rutas", sin textos real · estimado · simulado en pantalla (uak decision CO-028); avance animado y con `prefers-reduced-motion` apagado
- **Verify:** `bash -c 'npm --prefix web run build'`
- **Next step:** abrir `Incentivos.tsx`

## CO-037 · Correr el recorrido de la demo en navegador real y arreglar lo roto a 1280 y 390

- **Type:** bug
- **Priority:** P0
- **Estimate:** 45 min
- **Rubric / Spec:** C1, C4
- **Depends on:** CO-029, CO-030, CO-031, CO-033, CO-034, CO-035, CO-036
- **Paths:** web/src/features/, .uak-shots/CO-037/
- **Freeze-Allowed:** yes
- **Test-First:** no (recorrido visual con Playwright y capturas)
- **Acceptance:** Las 5 rutas (`#/`, `#/sedeco`, `#/usuario`, `#/negocio`, `#/repartidor`) capturadas a 1280×720 y 390×844 con movimiento reducido, sin scroll horizontal ni texto cortado, Contraste AA, foco visible y controles de 48 px o más revisados; lo roto corregido en esta tarea
- **Verify:** `bash -c 'npm --prefix web run build && ls .uak-shots/CO-037/*.png'`
- **Next step:** `DEMO_MODE=1 bash scripts/demo.sh` y recorrer cada ruta

