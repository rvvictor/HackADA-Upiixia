# Plan B: video de la demo

Recorrido completo de colonIA grabado con Playwright (Chromium, 1280x720, movimiento reducido) contra una app local levantada con `DEMO_MODE=1` en un clon limpio del repo.

- `colonia-demo-completo.mp4` (0.46 MB, 34 s) y `.webm` (3.9 MB): Inicio, Mapa (capas, chips, alcaldía), alta de Doña Lupe con `simular_alta.py`, Negocio, ruta de la vecina, portal del repartidor (entrar, tomar, completar, incentivos).
- `capturas/`: una captura por pantalla.

## Cuándo usarlo
Si la demo en vivo falla (sin red, API caída, Render dormido) o no hay tiempo: reprodúcelo y narra con `docs/demo/guion.md`.

## Limitaciones honestas
- Se grabó **sin llave de Mapbox**: el mapa base muestra el aviso "El mapa necesita una llave de Mapbox"; el panel, las capas y la tarjeta sí se ven.
- La parte del repartidor se grabó con las rutas `/api/repartidores/*` bloqueadas en el navegador, es decir, en el **modo mock** del portal (etiqueta Simulado), porque con la API real "Mis rutas" queda vacío tras tomar una oferta (bug reportado en `docs/demo/ensayo.md`). Las ofertas y el código del paso de login sí se sembraron en la API real.

## Reproducirlo
```bash
DEMO_MODE=1 PORT=8765 bash scripts/demo.sh        # en un clon limpio
# en otra terminal, con Playwright (npm i playwright && npx playwright install chromium)
# visitar http://127.0.0.1:8765/#/inicio, #/mapa, #/negocio, #/usuario, #/repartidor y seguir docs/demo/guion.md
```
