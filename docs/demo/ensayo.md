# Ensayo limpio de la demo (CO-015)

Fecha: 2026-10-29, ~15:35-15:45 CDMX. Clon limpio con `git clone git@github.com:rvvictor/HackADA-Upiixia.git` (rama main, SHA 4217b4c), sin `data/raw` ni `.env`.

## Comando
```
DEMO_MODE=1 PORT=8765 bash scripts/demo.sh
```
Salida relevante (real):
```
> web@0.0.0 build
> tsc -b && vite build
...
REPARTIDOR R-89158 · código 515438 · colonias Ciudad Jardín, San Lucas, Culhuacán
Portal: http://127.0.0.1:8765/#/repartidor  (entra con R-89158 y 515438; el código vence en 10 min)
OFERTA O-3B7FB1 · frutas y verduras frescas en San Lucas · 2500 m · $113 (simulado)
colonIA: http://127.0.0.1:8765  (SEDECO #/sedeco · Vecina #/usuario · Negocio #/negocio)
```
`curl localhost:8765/api/health` devolvió `{"status":"ok"}`. Arranque completo (uv sync + npm ci + build + seed) en menos de 2 min. El bot de Telegram se omitió por `DEMO_MODE=1` (esperado).

Alta: `uv run python scripts/simular_alta.py --caso dona-lupe --url http://127.0.0.1:8765` imprimió `ALTA alta-puesto-de-dona-lupe-9914 · h3 89499585d6fffff · página /n/puesto-de-dona-lupe-9914`.

## Recorrido con Playwright (Chromium, reducedMotion, 1280x720)
| Paso | Resultado |
|---|---|
| Inicio `#/inicio` | OK |
| Mapa: capas Oferta barrial, Impulso, Rutas, Actividad; chips Tianguis y Mercado; selector Iztapalapa/Coyoacán; tarjeta | OK, con salvedades 1 y 2 |
| Alta `simular_alta.py` y vista Negocio (aparece "Puesto de Doña Lupe · alta nueva") | OK |
| Vecina: "2 kilos de jitomate, tortillas y pan" -> 0 cadenas, 1.5 km, 3 paradas, primera parada Puesto de Doña Lupe | OK (ruta en línea recta, sin Mapbox) |
| Repartidor: login con el par impreso, lista de ofertas, **Tomar ruta** | OK contra la API real |
| Repartidor: **Marcar como completada** e Incentivos con la API real | FALLA (hallazgo 3) |
| Repartidor en modo mock (rutas `/api/repartidores/*` bloqueadas): tomar, completar, incentivos | OK; es lo que muestra el video plan B |

## Hallazgos fuera de mis Paths (no corregidos)
1. **Mapa sin llave**: el clon limpio no tiene `VITE_MAPBOX_TOKEN` en el build, así que Mapa, ruta de la vecina y portal del repartidor muestran "El mapa necesita una llave de Mapbox" (`web/src/features/mapa/MapaHex.tsx:206`). El panel sigue funcionando. Reproducir: demo.sh en clon sin `.env`. Para la demo en vivo hay que construir con la llave pública.
2. **Chips tapados por la tarjeta de alcaldía** a 1280x720: la tarjeta (`web/src/features/mapa/index.tsx`, contenedor `absolute left-3 top-24`) cubre los chips "Tianguis / Mercado" que se envuelven en una segunda fila; un clic normal en el chip lo intercepta la tarjeta (Playwright agotó 30 s). Reproducir: `#/mapa` a 1280x720 y clic en "Tianguis".
3. **Bug bloqueante con la API real: "Mis rutas" siempre vacío.** `app/services/ofertas.py:108` (`ofertas_para`) solo devuelve ofertas con `estado == "abierta"`, y el portal (`web/src/features/repartidor/index.tsx:153`) arma "Mis rutas" filtrando esa misma lista por `repartidor_id`. Tras `POST /api/ofertas/{id}/tomar` (200, estado `tomada`) la oferta desaparece de `GET /api/ofertas?repartidor_id=…` (devuelve `[]`), así que no hay botón "Marcar como completada" ni avance a la bici. Verificado con curl y con Playwright. Arreglo sugerido: incluir también las ofertas `tomada` y `completada` cuyo `repartidor_id` sea el solicitante.
4. **Aviso engañoso**: `web/src/features/repartidor/index.tsx:156-179` muestra "la API de repartidores aún no responde, por eso ves ejemplos" también con la API real conectada, porque las ofertas sembradas llevan `demo_data: true`. Cosmético.
5. **Reensayos**: las ofertas sembradas tienen id determinista; las ya tomadas no regresan (`Ofertas (1)` en la segunda corrida). Para repetir: borrar `data/live/ofertas.jsonl` y correr `simular_repartidor.py`. (Documentado en el guion.)
6. Un error de consola no crítico (`Failed to load resource: net::ERR_FAILED`) solo aparece cuando yo bloqueo las rutas para la variante mock.
