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
